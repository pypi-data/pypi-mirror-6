import itertools
import random
from uuid import uuid1

import requests
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_loopback import FlaskLoopback
from urlobject import URLObject

import pytest
from weber_utils.pagination import paginated_view
from weber_utils.sorting import sorted_view


class App(object):

    def __init__(self, flask_app):
        super(App, self).__init__()
        self.flask_app = flask_app
        self.loopback = FlaskLoopback(self.flask_app)
        self.hostname = str(uuid1())
        self.url = URLObject("http://{0}".format(self.hostname))

    def activate(self):
        self.loopback.activate_address((self.hostname, 80))

    def deactivate(self):
        self.loopback.deactivate_address((self.hostname, 80))

    def get_page(self, page_size, page, path=None):
        if path is None:
            path = "objects"
        response = requests.get(self.url.add_path(path).set_query_param("page", str(page)).set_query_param("page_size", str(page_size)))
        response.raise_for_status()
        data = response.json()
        assert data["metadata"]["page"] == page
        assert data["metadata"]["page_size"] == page_size
        return data["result"]

    def get_all_paged(self, page_size, path=None):
        return list(itertools.chain.from_iterable(self.get_page(page_size, page, path=path) for page in range(1, int(self.num_objects / page_size) + 5)))


@pytest.fixture
def webapp(request):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["PROPAGATE_EXCEPTIONS"] = True

    db = SQLAlchemy(app)

    class Object(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        field1 = db.Column(db.Integer)
        field2 = db.Column(db.Integer)

    db.create_all()

    @app.route("/objects")
    @paginated_view
    @sorted_view(allowed_fields=["id", "field1"])
    def view_objects():
        return Object.query

    @app.route("/objects_different_renderer")
    @paginated_view(renderer=lambda obj: {"id_value": obj.id})
    def view_objects_different_renderer():
        return Object.query

    @app.route("/objects_limited_page_size")
    @paginated_view(max_page_size=10, default_page_size=5)
    def view_objects_limited_page_size():
        return Object.query

    @app.route("/objects_by_field2")
    @paginated_view
    @sorted_view(default="-field2")
    def view_objects_by_field2():
        return Object.query


    num_objects = 100
    field1_values = list(range(num_objects))
    random.shuffle(field1_values)
    field2_values = list(range(num_objects))
    random.shuffle(field2_values)

    for field1_value, field2_value in zip(field1_values, field2_values):
        db.session.add(Object(field1=field1_value, field2=field2_value))

    db.session.commit()

    returned = App(app)
    returned.num_objects = num_objects
    returned.activate()
    request.addfinalizer(returned.deactivate)

    return returned

@pytest.fixture(params=[1, 10, 50])
def page_size(request):
    return request.param
