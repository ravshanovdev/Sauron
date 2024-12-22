from app import PySauronApp
import pytest
from middleware import Middleware


def test_basic_rout_adding(app):
    @app.route("/home")
    def home(req, resp):
        resp.text = "hi babe"


def test_duplicate_routes_throws_exception(app):
    @app.route("/home")
    def home(req, resp):
        resp.text = "hi babe"

    with pytest.raises(AssertionError):
        @app.route("/home")
        def home2(req, resp):
            resp.text = "hi babe2"


def test_requests_can_be_sent_by_client(app, test_client):
    @app.route("/home")
    def home(req, resp):
        resp.text = "hi babe"

    response = test_client.get("http://testserver/home")

    assert response.text == "hi babe"


def test_parameterized_routes(app, test_client):
    @app.route("/hello/{name}")
    def generating(request, response, name):
        response.text = f"hello {name}"

    assert test_client.get("http://testserver/hello/kamoliddin").text == "hello kamoliddin"
    assert test_client.get("http://testserver/hello/dagon").text == "hello dagon"


def test_default_response(test_client):
    response = test_client.get("http://testserver/kkkkkkkk")

    assert response.text == "Not Found"
    assert response.status_code == 404


def test_class_based_get(app, test_client):
    @app.route("/book")
    class Books:
        def get(self, req, resp):
            resp.text = 'this is get method'

    assert test_client.get("http://testserver/book").text == "this is get method"


def test_class_based_post(app, test_client):
    @app.route("/book")
    class Books:
        def post(self, req, resp):
            resp.text = 'endpoint to create a book'

    assert test_client.post("http://testserver/book").text == "endpoint to create a book"


def test_class_based_not_allowed(app, test_client):
    @app.route("/book")
    class Books:
        def post(self, req, resp):
            resp.text = 'endpoint to create a book'

    response = test_client.get("http://testserver/book")

    assert response.text == "Method not allowed"
    assert response.status_code == 405


def test_alternative_rout_adding(app, test_client):
    def new_handler(req, resp):
        resp.text = "New Handler"

    app.add_route("/new_handler", new_handler)

    assert test_client.get("http://testserver/new_handler").text == "New Handler"


def test_template_handler(app, test_client):
    @app.route("/template")
    def template(req, resp):
        resp.body = app.template(
            "home.html",
            context={
                "new_title": "Best_title",
                "new_body": "Best_body"
            }
        )

    response = test_client.get("http://testserver/template")

    assert "Best_body" in response.text
    assert "new_title" in response.text
    assert "text/html" in response.headers["Content-Type"]


def test_custom_exception_handler(app, test_client):
    def on_exception(req, resp, exc):
        resp.text = "something bad happened"

    app.add_exception_handler(on_exception)

    @app.route("/exception")
    def exception_throwing_handler(req, resp):
        raise AttributeError("some exception")

    response = test_client.get("http://testserver/exception")

    assert response.text == "something bad happened"


def test_non_existent_static_files(test_client):
    assert test_client.get("http://testserver/nonexitent.css").status_code == 404


def test_serving_static_file(test_client):
    response = test_client.get("http://testserver/static/test.css")

    assert response.text == "body {background-color: lightblue;}"


def test_middleware(app, test_client):
    process_request_called = False
    process_response_called = False

    class SimpleMiddleWare(Middleware):
        def __init__(self, app):
            super().__init__(app)

        def process_request(self, req):
            nonlocal process_request_called
            process_request_called = True

        def process_response(self, req, resp):
            nonlocal process_response_called
            process_response_called = True

    app.add_middleware(SimpleMiddleWare)

    @app.route("/home")
    def index(req, resp):
        resp.text = "from handler"

    test_client.get("http://testserver/home")

    assert process_request_called is True
    assert process_response_called is True


def test_allowed_method_for_function_based_handlers(app, test_client):
    @app.route("/home", allowed_methods=["post"])
    def home(req, res):
        resp.text = "hi this is home page"

    resp = test_client.get("http://testserver/home")

    assert resp.status_code == 405
    assert resp.text == "Method not allowed"


def test_json_response_helper(app, test_client):
    @app.route("/json")
    def json_handler(req, resp):
        resp.json = {"name": "pysauron"}

    resp = test_client.get("http://testserver/json")
    resp_data = resp.json()

    assert resp.headers["Content-Type"] == "application/json"
    assert resp_data["name"] == "pysauron"


def test_text_response_handler(app, test_client):
    @app.route("/text")
    def text_handler(req, resp):
        resp.text = "plain text"

    response = test_client.get("http://testserver/text")

    assert "text/plain" in response.headers["Content-Type"]
    assert response.text == "plain text"


def test_html_helper(app, test_client):

    @app.route("/html")
    def html_handler(req, resp):
        resp.html = app.template(
            "home.html",
            context={
                "new_title": "Best_title",
                "new_body": "Best_body"
            }
        )

    response = test_client.get("http://testserver/html")

    assert "text/html" in response.headers["Content-Type"]
    assert "new_title" in response.text
    assert "Best_body" in response.text






