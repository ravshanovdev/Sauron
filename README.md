#PyLord: Python Web Framework built for creating  APIs

![purpose](https://img.shields.io/badge/:Purpose-learning-green)

![PyPI - Version](https://img.shields.io/pypi/v/pylord)



PyLord is a Python web framework built for learning purpose

It's a WSGI framework and can be used with any WSGI application server such as Gunicorn/Waitress


```shell
pip install pylord
```

## How to use it 

### Basic Usage

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


@app.route("/create_product", allowed_methods=['post'])
def create_product(req, resp):
    db = get_db()
    db.create(Product)
    data = req.json

    try:

        user = db.get(User, data['user'])
        if not user:
            resp.status_code = 404
            resp.json = {"error": "User not found"}
            return

        product = Product(
            user=user,
            name=data["name"],
            price=data['price']
        )

        db.save(product)

        resp.status_code = 201
        resp.json = {"id": product.id, "user": user.username, "name": product.name, "price": product.price}

    except Exception as e:
        resp.status_code = 500
        resp.json = {"error": str(e)}


@app.route("/get_product/{id:d}", allowed_methods=['get'])
def get_product(req, resp, id):
    db = get_db()

    product = db.get(Product, id=id)

    if not product:
        resp.status_code = 404
        resp.json = {"error": "Product not found"}
        return

    resp.status_code = 200
    resp.json = {"user": product.user.username, "name": product.name, "price": product.price}


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

