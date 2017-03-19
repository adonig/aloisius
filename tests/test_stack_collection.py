import json
from aloisius import Stack, StackCollection
import aloisius

from .utils import dummy_template
import mock
from moto import mock_cloudformation


@mock_cloudformation
def test_stack_results():
    aloisius.stacks = StackCollection()
    Stack(
        StackName='dummy',
        TargetState='present',
        RegionName='eu-west-1',
        TemplateBody=json.dumps(dummy_template)
    )
    for name, result in aloisius.stacks.results().items():
        assert name == 'dummy'
        assert list(result.keys()) == ['VPC']


@mock_cloudformation
def test_stack_success(monkeypatch):
    aloisius.stacks = StackCollection()
    Stack(
        StackName='dummy_failed',
        TargetState='present',
        RegionName='eu-west-1',
        TemplateBody=json.dumps(dummy_template)
    )
    assert aloisius.stacks.success()


@mock_cloudformation
def test_stack_success_failed(monkeypatch):
    def mock_return(_):
        return mock.Mock(stack_status='ROLLBACK_COMPLETE')
    monkeypatch.setattr(Stack, '_describe_stack', mock_return)

    aloisius.stacks = StackCollection()

    Stack(
        StackName='dummy_failed',
        TargetState='present',
        RegionName='eu-west-1',
        TemplateBody=json.dumps(dummy_template)
    )
    assert aloisius.stacks.success() is False
