

setup = """
import dynamic_scope

class Scope(object):
    pass

_publisher = Scope()
_publisher.session = Scope()
_publisher.session.user = None

ctx = dynamic_scope.DynamicScope()
ctx._push(dict(user=None))

def get_user():
    return _publisher.session.user
"""


import timeit

print timeit.Timer('get_user()', setup).timeit()
print timeit.Timer('ctx.user', setup).timeit()

