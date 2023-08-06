"""
bidirectional URI routing
"""

from functools import partial
from .restful import RestfulRouter

routes = RestfulRouter()

path_for = routes.path_for
match = routes.match
resource = routes.resource
resources = routes.resources


def method(httpmethod):
    """decorator to overwrite default method(GET) for custom actions,
    intended to be used within restful resource
    """
    def add_method(fn):
        fn.__httpmethod__ = httpmethod
        return fn
    return add_method


def route(method, pattern, handler=None):
    """register a routing rule

    Example:

         route('GET', '/path/<param>', handler)

    """
    if handler is None:
        return partial(route, method, pattern)
    return routes.append(method, pattern, handler)

for _ in ["get", "post", "head", "delete", "put", "patch"]:
    locals()[_] = partial(route, _.upper())
    locals()[_].__doc__ = """register a %(method)s handler

    Example:

        %(method)s('/path/<param', handler)

        @%(method)s('/path/<param')
        def handler(param):
            pass
    """ % dict(method=_)
