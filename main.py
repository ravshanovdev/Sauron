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


class Category(Table):
    name = Column(str)


class Blog(Table):
    category = ForeignKey(Category)
    name = Column(str)
    description = Column(str)


# db.create(Category)
# db.create(Blog)


@app.route("/create_category", allowed_methods=["post"])
def create_category(req, resp):
    db = get_db()
    db.create(Category)
    category = Category(**req.POST)
    db.save(category)

    resp.status_code = 201
    resp.json = {"name": category.name}


@app.route("/get_all_category", allowed_methods=["get"])
def get_all_category(req, resp):
    db = get_db()
    category = db.all(Category)

    resp.status_code = 200
    resp.json = [{"category_id": cat.id, "category_name": cat.name} for cat in category]


@app.route("/create_blog", allowed_methods=['post'])
def crete_blog(req, resp):
    db = get_db()
    db.create(Blog)
    data = req.json
    category = db.get(Category, data["category"])
    if not category:
        resp.status_code = 404
        resp.json = {"error": "Category Not Found"}
        return

    blog = Blog(
        category=category,
        name=data["name"],
        description=['description'],

    )

    resp.status_code = 201
    resp.json = {
        "blog_id": blog.id,
        "blog_category": str(blog.category),
        "blog_name": blog.name,
        "blog_description": blog.description

    }


@app.route("/all_blog", allowed_methods=['get'])
def get_all_blog(req, resp):
    db = get_db()
    blogs = db.all(Blog)

    resp.status_code = 200
    resp.json = [{"blog_id": blog.id, "blog_category": blog.category, "blog_name": blog.name, "blog_description": blog.description} for blog in blogs]

