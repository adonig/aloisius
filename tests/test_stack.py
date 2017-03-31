import json
import re

from moto import mock_cloudformation

from .utils import dummy_template
from aloisius import Stack


@mock_cloudformation
def test_stack_is_created():
    stack = Stack(
        StackName='dummy',
        TargetState='present',
        RegionName='eu-west-1',
        TemplateBody=json.dumps(dummy_template)
    )
    assert re.match("vpc-[a-z0-9]+", stack.outputs['VPC'])


@mock_cloudformation
def test_stack_is_updated_when_already_exists(monkeypatch, mocker):
    stack = Stack(
        StackName='dummy',
        TargetState='present',
        RegionName='eu-west-1',
        TemplateBody=json.dumps(dummy_template)
    )

    assert stack.outputs

    monkeypatch.setattr(Stack, '_create', lambda x: False)

    update_stack = Stack(
        StackName='dummy',
        TargetState='present',
        RegionName='eu-west-1',
        TemplateBody=json.dumps(dummy_template)
    )

    spy = mocker.spy(update_stack, '_update')

    assert re.match("vpc-[a-z0-9]+", update_stack.outputs['VPC'])

    assert spy.call_count == 1
