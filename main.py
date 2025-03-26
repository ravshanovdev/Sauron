from pylord.app import PyLordApp
from pylord.middleware import Middleware
from pylord.orm import ForeignKey, Table, Column, Database
import threading

threading_local = threading.local()


def get_db():
    if not hasattr(threading_local, "db"):
        threading_local.db = Database("./test_main.db")
    return threading_local.db


app = PyLordApp()


@app.route("/home", allowed_methods=["get"])
def home(request, response):
    response.text = "hi this is home page"


@app.route("/about")
def about(request, response):
    response.text = 'hi this is about page'


@app.route("/hello/{name}")
def generating(request, response, name):
    response.text = f"hello {name}"


@app.route("/book")
class Books:
    def get(self, request, response):
        response.text = "this is get method"

    def post(self, request, response):
        response.text = "endpoint to create a book"


def new_handler(req, resp):
    resp.text = "New Handler"


app.add_route("/new_handler", new_handler)


@app.route("/template")
def template_handler(req, resp):
    resp.body = app.template(
        "home.html",
        context={
            "new_title": "Best_title213",
            "new_body": "Best_body123"
        }
    )


def on_exception(req, resp, exc):
    resp.text = str(exc)


app.add_exception_handler(on_exception)


@app.route("/exception")
def exception_throwing_handler(req, resp):
    raise AttributeError("some exception")


class LoggingMiddleware(Middleware):
    def process_request(self, req):
        print("request is being called", req.url)

    def process_response(self, req, resp):
        print("response has been generated", req.url)


app.add_middleware(LoggingMiddleware)


@app.route("/json")
def json_handler(req, resp):
    response_data = {"name": "asasa"}
    resp.json = response_data


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


@app.route("/get_product_by_name/{name}", allowed_methods=['get'])
def get_product_by_name(req, resp, name: str):
    db = get_db()

    product = db.get_by_field(Product, field_name="name", value=name)

    if not product:
        resp.status_code = 404
        resp.json = {"product": "Product Not Found"}
        return

    resp.status_code = 200
    resp.json = {"user": product.user.username, "name": product.name, "price": product.price}


