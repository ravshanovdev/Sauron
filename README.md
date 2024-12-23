#PyLord: Python Web Framework built for creating  APIs

![purpose](https://img.shields.io/badge/:Purpose-learning-green)

![PyPI - Version](https://img.shields.io/pypi/v/:pylord)


PyLord is a Python web framework built for learning purpose

It's a WSGI framework and can be used with any WSGI application server such as Gunicorn/Waitress


```shell
pip install pylord

```

## How to use it 

### Basic Usage


```python
from pylord.app import PyLordApp
from pylord.middleware import Middleware
app = PyLordApp()


# you can add allowed methods in you function_handler
@app.route("/home", allowed_methods=["get"])
def home(request, response):
    response.text = "hi this is home page"


@app.route("/about")
def about(request, response):
    response.text = 'hi this is about page'


@app.route("/hello/{name}")
def generating(request, response, name):
    response.text = f"hello {name}"


# working with class
@app.route("/book")
class Books:
    def get(self, request, response):
        response.text = "this is get method"

    def post(self, request, response):
        response.text = "endpoint to create a book"


# route your class here
def new_handler(req, resp):
    resp.text = "New Handler"


app.add_route("/new_handler", new_handler)


# for creating any exception
def on_exception(req, resp, exc):
    resp.text = str(exc)


app.add_exception_handler(on_exception)


@app.route("/exception")
def exception_throwing_handler(req, resp):
    raise AttributeError("some exception")


# working with json
@app.route("/json")
def json_handler(req, resp):
    response_data = {"name": "asasa"}
    resp.json = response_data






```


### Unit Tests

The recommended way of writing unit tests is with pytest. There are two built in fixtures that you may want to use when writing unit tests with PyLord. The first one is app which is an instance of the main API class:

```python

def test_route_overlap_throws_exception(app):
    @app.route("/")
    def home(req, resp):
        resp.text = "Welcome Home."

    with pytest.raises(AssertionError):
        @app.route("/")
        def home2(req, resp):
            resp.text = "Welcome Home2."

```

The other one is client that you can use to send HTTP requests to your handlers. It is based on the famous requests and it should feel very familiar:

```python

def test_parameterized_route(app, client):
    @app.route("/{name}")
    def hello(req, resp, name):
        resp.text = f"hi {name}"

    assert client.get("http://testserver/sauron").text == "hi sauron"

```

### Templates

The default folder for templates is templates. You can change it when initializing the main API() class: 

```python
app = API(templates_dir="templates_dir_name")
```

Then you can use HTML files in that folder like so in a handler: 

```python
@app.route("/show/template")
def handler_with_template(req, resp):
    resp.html = app.template(
        "example.html", context={"title": "Awesome Framework", "body": "welcome to the future!"})
```

### Static Files

```python
app = API(static_dir="static_dir_name")
```

Then you can use the files inside this folder in HTML files: 

```HTML
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>{{title}}</title>

    <link href="/static/main.css" rel="stylesheet" type="text/css">
</head>

<body>
    <h1>{{body}}</h1>
    <p>This is a paragraph</p>
</body>
</html>
```

### Middleware
You can create custom middleware classes by inheriting from the bumbo.middleware.Middleware class and overriding its two methods that are called before and after each request: 

```python
from pylord.app import PyLordApp
from pylord.middleware import Middleware


app = PyLordApp()


class SimpleCustomMiddleware(Middleware):
    def process_request(self, req):
        print("Before dispatch", req.url)

    def process_response(self, req, res):
        print("After dispatch", req.url)


app.add_middleware(SimpleCustomMiddleware)
```

