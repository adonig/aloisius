import json
import re

from aloisius import Stack, StackException

import mock
from moto import mock_cloudformation
import pytest

dummy_template = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Stack 3",
    "Resources": {
        "VPC": {
            "Properties": {
                "CidrBlock": "192.168.0.0/16",
            },
            "Type": "AWS::EC2::VPC"
        }
    },
    "Outputs": {
        "VPC": {
            "Value": {"Ref": "VPC"},
            "Description": "This is a description."
        }
    }
}


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
def test_stack_create_failed_raises_exception(monkeypatch):
    def mock_return(_):
        return mock.Mock(stack_status='CREATE_FAILED')
    monkeypatch.setattr(Stack, '_describe_stack', mock_return)

    with pytest.raises(StackException):
        stack = Stack(
            StackName='dummy_failed',
            TargetState='present',
            RegionName='eu-west-1',
            TemplateBody=json.dumps(dummy_template)
        )
        stack.outputs['VPC']  # Wait for result


@mock_cloudformation
def test_stack_rollback(monkeypatch):
    def mock_return(_):
        return mock.Mock(stack_status='ROLLBACK_COMPLETE')
    monkeypatch.setattr(Stack, '_describe_stack', mock_return)

    with pytest.raises(StackException):
        stack = Stack(
            StackName='dummy_failed',
            TargetState='present',
            RegionName='eu-west-1',
            TemplateBody=json.dumps(dummy_template)
        )
        stack.outputs['VPC']  # Wait for result


@mock_cloudformation
def test_stack_results():
    Stack._futures = {}  # Cleanup from other runs
    Stack(
        StackName='dummy',
        TargetState='present',
        RegionName='eu-west-1',
        TemplateBody=json.dumps(dummy_template)
    )
    for name, result in Stack.results().items():
        assert name == 'dummy'
        assert result.keys() == ['VPC']
