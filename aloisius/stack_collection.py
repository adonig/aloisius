from six.moves import UserList
from concurrent.futures import wait
from . import export


@export
class StackCollection(UserList):
    def wait(self):
        return wait([stack._future for stack in self.data])

    def results(self):
        self.wait()
        results = {}
        for stack in self.data:
            results[stack.kwargs['StackName']] = stack._future.exception() or \
                                                 stack._future.result()
        return results

    def success(self):
        return not any(stack._future.exception() for stack in self.data)
