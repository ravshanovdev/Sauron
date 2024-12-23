from pylord.app import PyLordApp
import pytest


@pytest.fixture
def app():
    return PyLordApp()


@pytest.fixture
def test_client(app):
    return app.test_session()
