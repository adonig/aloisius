# Copyright 2017 The contributors. All rights reserved.
#
# See LICENSE file for full license.

import pytest

from aloisius.stack import Stack, FutureOutputs


@pytest.fixture
def outputs():
    class MockStack(Stack):
        def _execute(self, **kwargs):
            return {'key': 'value'}
    return FutureOutputs(MockStack(StackName='name'))


def test_contains(outputs):
    assert 'key' in outputs
    assert 'non-key' not in outputs


def test_get(outputs):
    assert outputs.get('key') == 'value'
    assert outputs.get('non-key') is None
    assert outputs.get('non-key', 'value') == 'value'


def test_getitem(outputs):
    assert outputs['key'] == 'value'
    with pytest.raises(KeyError):
        outputs['non-key']


def test_items(outputs):
    for key, value in outputs.items():
        assert key == 'key'
        assert value == 'value'


def test_iter(outputs):
    for key in outputs:
        assert key == 'key'
        assert outputs[key] == 'value'


def test_keys(outputs):
    for key in outputs.keys():
        assert key == 'key'


def test_values(outputs):
    for value in outputs.values():
        assert value == 'value'


def test_len(outputs):
    assert len(outputs) == 1
