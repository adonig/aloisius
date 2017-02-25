# Copyright 2017 The contributors. All rights reserved.
#
# See LICENSE file for full license.

from collections import Mapping
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import time

from boto3.session import Session
from botocore.exceptions import ClientError

from . import export
from .exception import StackException


@export
class Stack(object):
    # Treat template_body as a pathname if it starts with this prefix.
    file_prefix = 'file://'

    # The time between stack status checks.
    sleep_seconds = 5

    max_retries = 3

    create_stack_params = ['StackName', 'TemplateBody', 'TemplateURL',
                           'Parameters', 'DisableRollback', 'TimeoutInMinutes',
                           'NotificationARNs', 'Capabilities', 'OnFailure',
                           'StackPolicyBody', 'StackPolicyURL', 'Tags']

    update_stack_params = ['StackName', 'TemplateBody', 'TemplateURL',
                           'UsePreviousTemplate', 'StackPolicyDuringUpdateBody',
                           'StackPolicyDuringUpdateURL', 'Parameters',
                           'Capabilities', 'StackPolicyBody', 'StackPolicyURL',
                           'NotificationARNs']

    _executor = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())

    def __init__(self, **kwargs):
        self.outputs = FutureOutputs(self)
        self._future = self._executor.submit(self._execute, **kwargs)

    def __del__(self):
        self._future.result()

    def _execute(self, **kwargs):
        kwargs['TargetState'] = kwargs['TargetState'] or 'present'

        # Like `aws-cli cloudformation create-stack` read the template
        # from a local file if template_body starts with 'file://' .
        if kwargs['TargetState'] == 'present' and 'TemplateBody' in kwargs:
            template_body = kwargs['TemplateBody']
            if template_body.startswith(self.file_prefix):
                filepath = template_body[len(self.file_prefix):]
                with open(filepath) as fp:
                    kwargs['TemplateBody'] = fp.read()

        # Transform the parameter dict into a list of Parameter structures.
        if kwargs['TargetState'] == 'present' and 'Parameters' in kwargs:
            kwargs['Parameters'] = [{
                'ParameterKey': key,
                'ParameterValue': str(val.result() if isinstance(val, Future)
                                      else val),
                'UsePreviousValue': False  # Always use the current value.
            } for key, val in kwargs['Parameters'].items()]

        # Store the keyword arguments as member, so we can logically
        # separate our code without having to pass the kwargs around.
        self._kwargs = kwargs

        # Create a custom Session in our region of choice.
        session = Session(region_name=kwargs['RegionName'])

        # Get the CloudFormation service resource.
        self._cfn = session.resource('cloudformation')

        # Wait until no stack operation is in progress.
        self._wait_until_ready()

        # Execute the stack operation necessary to establish the target state.
        stack_operation = self._establish_target_state()

        # Wait until the stack operation is complete or has failed.
        stack = self._wait_until_done(stack_operation)

        # Return the stack outputs.
        if stack_operation != 'DELETE' and stack.outputs:
            return {o['OutputKey']: o['OutputValue'] for o in stack.outputs}
        else:
            return {}

    def _wait_until_ready(self):
        while True:
            stack = self._describe_stack()
            if stack and stack.stack_status.endswith('_IN_PROGRESS'):
                self.sleep(self.sleep_seconds)
            else:
                break

    def _establish_target_state(self):
        target_state = self._kwargs['TargetState']
        if target_state == 'present':
            if not self._create() and self._update():
                # The stack does already exist and an update is necessary.
                return 'UPDATE'
            else:
                # The stack does not exist or no update is necessary.
                return 'CREATE'
        elif target_state == 'absent':
            self._delete()
            return 'DELETE'
        else:
            raise AssertionError('Invalid state {!r}'.format(target_state))

    def _wait_until_done(self, stack_operation):
        while True:
            stack = self._describe_stack()
            # The delete operation is complete when there's no stack.
            if not stack and stack_operation == 'DELETE':
                return None
            # Otherwise there should always be a stack.
            assert stack, "Shoot! Where is my stack? :("
            # Return if the stack operation is complete.
            if stack.stack_status.endswith('_COMPLETE'):
                return stack
            # Raise an exception if the stack operation has failed.
            if stack.stack_status.endswith('_FAILED'):
                msg = 'Stack operation {!r} has failed.'
                raise StackException(msg.format(stack_operation))
            # Sleep if the stack operation neither is complete nor has failed.
            time.sleep(self.sleep_seconds)

    def _describe_stack(self):
        try:
            stacks = list(self._invoke(self._cfn.stacks.filter,
                                       StackName=self._kwargs['StackName']))
            return stacks[0]
        except ClientError as err:
            error_code = err.response['Error']['Code']
            error_message = err.response['Error']['Message']
            if error_code == 'ValidationError' and \
               error_message == 'Stack with id {} does not exist'.format(
                   self._kwargs['StackName']):
                return None
            else:
                raise err

    def _create(self):
        stack = self._describe_stack()
        if stack and stack.stack_status != 'ROLLBACK_COMPLETE':
            return False
        else:
            kwargs = {key: val for key, val in self._kwargs.items()
                      if key in self.create_stack_params}
            self._invoke(self._cfn.create_stack, **kwargs)
            return True

    def _update(self):
        stack = self._describe_stack()
        kwargs = {key: val for key, val in self._kwargs.items()
                  if key in self.update_stack_params}
        try:
            self._invoke(stack.update, **kwargs)
            return True
        except ClientError as err:
            error_code = err.response['Error']['Code']
            error_message = err.response['Error']['Message']
            if error_code == 'ValidationError' and \
               error_message == 'No updates are to be performed.':
                return False
            else:
                raise err

    def _delete(self):
        stack = self._describe_stack()
        if stack:
            self._invoke(stack.delete)

    def _invoke(self, func, *args, **kwargs):
        retries = 0
        while True:
            try:
                return func(*args, **kwargs)
            except ClientError as err:
                error_code = err.response['Error']['Code']
                if error_code != 'Throttling' or retries == self.max_retries:
                    raise err
            time.sleep(self.sleep_seconds * (2 ** retries))
            retries += 1


class FutureOutputs(Mapping):
    def __init__(self, stack):
        self._stack = stack
        self._result = None

    def __getitem__(self, key):
        return self._get_result()[key]

    def __iter__(self):
        return iter(self._get_result())

    def __len__(self):
        return len(self._get_result())

    def _get_result(self):
        if self._result is None:
            self._result = self._stack._executor.submit(
                lambda: self._stack._future.result()).result()
        return self._result
