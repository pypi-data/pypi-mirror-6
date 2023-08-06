# biro

bidirectional URI routing

```python
from biro import get, path_for, match

@get('/article')
def list_article():
    pass

@get('/article/<article_id>')
def show_article():
    pass

path_for(show_article, article_id=618)  # /article/618
path_for(list_article, limit=10)  # /article?limit=10

match('GET', "/article/309")  # (article, {"article_id": "309"})
match('POST', "/article/309")  # (None, None)
```

## the Router class

```python
from biro import Router

router = Router()
router.append('DETELE', '/article/<article_id>', handler)

router.match('PATCH', '/path')
router.path_for(handler, q=val)
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
