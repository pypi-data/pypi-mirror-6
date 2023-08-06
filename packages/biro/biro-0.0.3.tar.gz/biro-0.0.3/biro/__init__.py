"""
bidirectional URI routing
"""

from functools import partial
from .router import Router

routes = Router()

path_for = routes.path_for
match = routes.match


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
