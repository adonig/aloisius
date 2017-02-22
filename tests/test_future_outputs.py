import unittest
from aloisius.stack import Stack, FutureOutputs


# Mock execution for testing purpouses to just return the list of kargs
class MockStack(Stack):
    def _execute(self, **kargs):
        return kargs


class TestFutureOutputs(unittest.TestCase):

    def test_dictionary_interface(self):
        outputs = FutureOutputs(MockStack(key='value'))
        self.assertEqual(outputs['key'], 'value')

    def test_iterator_interface(self):
        outputs = FutureOutputs(MockStack(key='value'))
        for key in outputs:
            self.assertEqual(key, 'key')
            self.assertEqual(outputs[key], 'value')

    def test_iteritems(self):
        outputs = FutureOutputs(MockStack(key='value'))
        for key, value in outputs.iteritems():
            self.assertEqual(key, 'key')
            self.assertEqual(value, 'value')

if __name__ == '__main__':
    unittest.main()
