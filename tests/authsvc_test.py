import pytest

from flask import Flask
from flask.testing import FlaskClient
from auth-svc import create_app


@pytest.fixture
def client() -> FlaskClient
    app= create_app()
    app.testing = True

    with app.test_client() as client:
        yield client


        
