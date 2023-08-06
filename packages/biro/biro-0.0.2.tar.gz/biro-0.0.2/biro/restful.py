import types
from functools import partial
from .router import Router


def get_module_fns(module):
    "get defined functions of a module"
    attrs = [getattr(module, a) for a in dir(module) if not a.startswith('_')]
    return [attr for attr in attrs if isinstance(attr, types.FunctionType)
            and attr.__module__ == module.__name__]


def get_methods(cls):
    "get public methods of a class"
    attrs = [getattr(cls, a) for a in dir(cls) if not a.startswith('_')]
    return [attr for attr in attrs if isinstance(attr, types.FunctionType)]


class RestfulRouter(Router):

    restful_routes = [
        ('GET',    '%(path)s',               'query'),
        ('POST',   '%(path)s',               'create'),
        ('GET',    '%(path)s/<%(id)s>',      'show'),
        ('PUT',    '%(path)s/<%(id)s>',      'replace'),
        ('PATCH',  '%(path)s/<%(id)s>',      'modify'),
        ('DELETE', '%(path)s/<%(id)s>',      'destroy'),
        ('GET',    '%(path)s/new',           'new'),
        ('GET',    '%(path)s/<%(id)s>/edit', 'edit'),
    ]

    restful_methods = [method for _, _, method in restful_routes]

    def resource(self, url_path=None, module=None):
        """register a restful resource

        Example:

            @resource('/article')
            class Article:
                def show(article_id):
                    pass

                @method('put')
                def upvote(article_id):
                    pass

        """
        if url_path is None:
            url_path = '/' + module.__name__.replace('.', '/')
        if module is None:
            return partial(self.register_resource, url_path)
        else:
            return self.register_resource(url_path, module)

    def resources(self, *resources, prefix=''):
        """register a list of restful resources

        Example:

            resources(articles, users, '/api/v1')

        """
        for resource in resources:
            url_path = prefix + '/' + resource.__name__.split('.').pop()
            self.register_resource(url_path, resource)

    def register_resource(self, url_path, module):
        url_id = '%s_id' % url_path.split('/').pop()
        vals = {'path': url_path, 'id': url_id}
        rules = [(method, pattern % vals, getattr(module, handler))
                 for method, pattern, handler in self.restful_routes
                 if hasattr(module, handler)]

        if isinstance(type(module), types.ModuleType):
            fns = get_module_fns(module)
        else:
            fns = get_methods(module)

        custom_rules = [(getattr(fn, '__httpmethod__', 'GET'),
                        '%s/<%s>/%s' % (url_path, url_id, fn.__name__),
                        fn) for fn in fns
                        if fn.__name__ not in self.restful_methods]
        self.extend(rules)
        self.extend(custom_rules)
        return module
