from app import PySauronApp
import pytest


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


