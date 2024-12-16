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

