# biro

bidirectional URI routing

```python
from biro import get, path_for, match

def article():
    pass

get('/article/<article_id>', article)

path_for(article, article_id=618)  # /article/618

match('GET', "/article/309")  # (article, {"article_id": "309"})
match('POST', "/article/309")  # (None, None)
```

decorators

```python
from biro import delete

@delete('/article/<article_id>')
def article():
    pass
```

RESTful shortcut

```python
from biro import resource

resource('/article', article_module_or_class)

resources(m_or_c, m_or_c2, prefix='/v2')
```

the resource decorator

```python
@resource('/v1/article')
class Article:
    def show(article_id):
        pass

    def create():
        pass

    @method('patch')
    def like(article_id):
        pass
```

default rules

```python
('GET',    '%(path)s',               'query'),
('POST',   '%(path)s',               'create'),
('GET',    '%(path)s/<%(id)s>',      'show'),
('PUT',    '%(path)s/<%(id)s>',      'replace'),
('PATCH',  '%(path)s/<%(id)s>',      'modify'),
('DELETE', '%(path)s/<%(id)s>',      'destroy'),
('GET',    '%(path)s/new',           'new'),
('GET',    '%(path)s/<%(id)s>/edit', 'edit'),
```

## wsgi example

```python
from biro import get, match

@get('/')
def home():
    return 'home'

@get('/hello/<name>')
def hello(name):
    return 'hello %s' % name

def application(environ, start_response):
    handler, params = match(environ['REQUEST_METHOD'].upper(),
                            environ['PATH_INFO'])
    if handler:
        status = '200 OK'
        response = handler(**params)
    else:
        status = '404 Not Found'
        response = 'page not found'
    start_response(status, [('Content-Type', 'text/html; charset=utf-8')])
    return [response.encode('utf-8')]
```

save it as example.py, then it can be lunched using gunicorn like this:

```
$ gunicorn example:application
```
