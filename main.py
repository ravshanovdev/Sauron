from app import PySauronApp
from middleware import Middleware
app = PySauronApp()
import json

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
