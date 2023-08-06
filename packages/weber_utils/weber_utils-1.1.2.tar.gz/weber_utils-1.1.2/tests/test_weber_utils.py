import json

import flask
import weber_utils
from weber_utils._compat import string_types
from weber_utils._compat import httplib
from werkzeug.exceptions import HTTPException

from . import TestCase


class GetRequestInputTest(TestCase):

    def setUp(self):
        super(GetRequestInputTest, self).setUp()
        self.app = flask.Flask(__name__)

    def test_request_input_json(self):
        data = {"a": 2, "b": "c"}
        with self.app.test_request_context(method="POST", data=json.dumps(data), content_type="application/json"):
            self.assertEquals(weber_utils.get_request_input({"a": int, "b": string_types}), data)

    def test_request_input_form(self):
        data = {"a": "2", "b": "c"}
        with self.app.test_request_context(method="POST", data=data):
            self.assertEquals(weber_utils.get_request_input({"a": int, "b": string_types}), {"a": 2, "b": "c"})

    def test_missing_fields(self):
        self._assert_bad_request({"a": 2}, {"b": int})

    def test_invalid_value(self):
        self._assert_bad_request({"a": "hello"}, {"a": int})
        self._assert_bad_request({"a": "hello"}, {"a": int}, as_json=True)

    def test_takes_schema_args(self):
        echo = lambda **kwargs: kwargs

        data = {"a": 2, "b": "c"}

        with self.app.test_request_context(method="POST", data=data):
            result = weber_utils.takes_schema_args(a=int, b=string_types)(echo)()
            self.assertEquals(result, data)

    def _assert_bad_request(self, data, schema, as_json=False):
        if as_json:
            data = json.dumps(data)
        with self.app.test_request_context(method="POST", data=data, content_type="application/json" if as_json else None):
            with self.assertRaises(HTTPException) as caught:
                weber_utils.get_request_input(schema)
            self.assertEquals(caught.exception.code, httplib.BAD_REQUEST)
