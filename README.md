#PyLord: Python Web Framework built for creating  APIs

![purpose](https://img.shields.io/badge/:Purpose-learning-green)

[![PyPI - Version](https://img.shields.io/pypi/v/pylord)](https://pypi.org/project/pylord/)




PyLord is a Python web framework built for building APIs

It's a WSGI framework and can be used with any WSGI application server such as Gunicorn/Waitress


```shell
pip install pylord
```

## How to use it 

### Basic Usage For WSGI version

```python
import threading

from pylord.app import PyLordApp
from pylord.orm import ForeignKey, Table, Column, Database

threading_local = threading.local()
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


def get_db():
    if not hasattr(threading_local, "db"):
        threading_local.db = Database("./test_main.db")
    return threading_local.db


class User(Table):
    username = Column(str)
    email = Column(str)
    password_hash = Column(str)


class Product(Table):
    user = ForeignKey(User)
    name = Column(str)
    price = Column(int)


from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password):
    return generate_password_hash(password)


def check_password(password, hashed_password):
    return check_password_hash(hashed_password, password)


@app.route("/user_register", allowed_methods=['post'])
def user_register(req, resp):
    db = get_db()

    data = req.json
    username = data.get("username")
    email = data.get("email")
    password1 = data.get("password1")
    password2 = data.get("password2")

    if not all([username, email, password1, password2]):
        resp.status_code = 400
        resp.json = {"error": "Barcha qatorlarni to'ldiring"}
        return

    if password1 != password2:
        resp.status_code = 400
        resp.json = {"error": "Parollar mos kelmayapti"}
        return

    existing_user_id = db.get_user(User, field_name="username", value=username)
    existing_user_email = db.get_user(User, field_name="email", value=email)
    if existing_user_id:
        resp.status_code = 400
        resp.json = {"error": "User already exists"}
        return
    elif existing_user_email:
        resp.status_code = 400
        resp.json = {"error": "Email already exists"}
        return

    hashed_password = hash_password(password1)

    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.save(new_user)

    resp.status_code = 201
    resp.json = {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "username": username,
        "email": email
    }

``` python 

import jwt
import datetime
import secrets
from functools import wraps

# just for test
SECRET_KEY = "your_secret_key"


def generate_token(user_id, username):
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=3)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def auth_required(f):
    @wraps(f)
    def decorated(req, resp, *args, **kwargs):
        auth_header = req.headers.get("Authorization")

        def reject(msg):
            resp.status_code = 401
            resp.json = {"error": msg}
            return

        if not auth_header or not auth_header.startswith("Bearer "):
            return reject("Token Required!")

        try:
            token = auth_header.split("Bearer ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            req.user_id = payload.get("user_id")
            req.username = payload.get("username")
        except (IndexError, AttributeError):
            return reject("Incorrect Token!")
        except jwt.ExpiredSignatureError:
            return reject("Token Expired!")
        except jwt.InvalidTokenError:
            return reject("Invalid Token")

        return f(req, resp, *args, **kwargs)

    return decorated
```

### Basic Usage For ASGI version (This mode is currently in testing mode.)

``` python

from pylord.asgi import PyLordASGI
from pylord.orm import ForeignKey, Table, Column, Database
from main import get_db

app = PyLordASGI()


@app.route("/", methods=["get"])
async def get_hello(request):
    return {"message": "hello"}


class TestModel(Table):
    name = Column(str)
    text = Column(str)


@app.route("/create_model", methods=['post'])
async def create_test(request, response):
    db = get_db()
    db.create(TestModel)

    try:
        data = await request.json()
    except Exception:
        return {"error": "Invalid or empty JSON body"}

    model = TestModel(name=data['name'], text=data['text'])
    db.save(model)
    # return {"id": model.id, "name": model.name, "text": model.text}

    response.status_code = 201
    response.json = {"id": model.id, "name": model.name, "text": model.text}


@app.route("/get_all_test_models", methods=['get'])
async def get_test(request, response):
    db = get_db()

    tests = db.all(TestModel)

    response.status_code = 200
    response.json = [{"id": test.id, "name": test.name, "text": test.text} for test in tests]


@app.route("/delete/{id:d}", methods=['delete'])
async def delete_test(request, response, id):
    db = get_db()

    db.delete(TestModel, id=id)

    response.status_code = 200
    response.json = {"message": "test model successfully deleted"}


@app.route('/update_test/{id:d}', methods=['patch'])
async def update_test(req, resp, id):
    print(id)

    db = get_db()
    data = await req.json()

    try:
        test = db.get(TestModel, id=id)

    except Exception as e:
        resp.status_code = 404
        resp.json = {"message": "test not found."}
        return

    test.name = data['name']
    test.text = data['text']

    db.update(test)

    resp.status_code = 200
    resp.json = {"message": "test model updated.!"}

# app.add_route('/update_test/{id:d}', update_test, methods=['patch'])

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

