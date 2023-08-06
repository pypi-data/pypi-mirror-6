from flask import Flask

import pytest


@pytest.fixture
def flask_app(request):
    returned = Flask(__name__)
    return returned
