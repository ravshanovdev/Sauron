from app import PySauronApp
import pytest


@pytest.fixture
def app():
    return PySauronApp()


@pytest.fixture
def test_client(app):
    return app.test_session()
