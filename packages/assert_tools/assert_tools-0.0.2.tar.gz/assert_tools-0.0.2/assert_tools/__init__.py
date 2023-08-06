"""
pep8 style names for unittest2 assert*
"""

import re
import unittest2


def pep8(name):
    return re.sub(
        re.compile('([A-Z])'), lambda m: '_' + m.group().lower(), name
    )


class NoOp(unittest2.TestCase):
    def no_op(self):
        pass


no_op = NoOp('no_op')

_asserts = [_ for _ in dir(no_op) if
            _.startswith('assert') and not '_' in _]
for _attrib in _asserts:
    vars()[pep8(_attrib)] = getattr(no_op, _attrib)
    del _attrib

del NoOp
del no_op
del pep8
del _asserts
del unittest2
del re
del _

