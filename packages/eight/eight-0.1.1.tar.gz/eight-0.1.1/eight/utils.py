from __future__ import print_function

import sys
from collections import namedtuple

USING_PYTHON2 = True if sys.version_info < (3, 0) else False

def input_with_unbuffered_stdout(prompt=None):
    class Unbuffered(object):
        def __init__(self, stream):
            self.stream = stream

        def write(self, data):
            self.stream.write(data)
            self.stream.flush()

        def __getattr__(self, attr):
            return getattr(self.stream, attr)

    orig_stdout = sys.stdout
    try:
        sys.stdout = Unbuffered(sys.stdout)
        result = raw_input(prompt)
    finally:
        sys.stdout = orig_stdout
    return result

Move = namedtuple('Move', ('new_name', 'old_module', 'old_name'))

class RedirectingLoader(object):
    def __init__(self, name):
        self._name = name
        self._moves = {}
        self._old_module = None
        self._module = None

    def _add_redirect(self, move):
        self._moves[move.new_name] = move

    def __getattr__(self, attr):
        if USING_PYTHON2 and attr in self._moves:
            move = self._moves[attr]
            if self._old_module is None:
                self._old_module = __import__(move.old_module)
            return getattr(self._old_module, move.old_name)
        else:
            if self._module is None:
                self._module = __import__(self._name)
            return getattr(self._module, attr)
