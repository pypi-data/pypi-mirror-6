import logbook
from flask import abort, request
from sentinels import NOTHING

from ._compat import PY2
from .request_utils import error_abort

_logger = logbook.Logger(__name__)

class _StrictJSON(object):

    def get(self, field, default=None):
        if request.json is None:
            _logger.debug("Request is not JSON")
            _abort_bad_request()
        if not isinstance(field, tuple):
            field = (field, str)
        field_name, field_type = field
        returned = request.json.get(field_name, NOTHING)
        if returned is NOTHING:
            return default
        if field_type is str and PY2:
            field_type = (str, unicode)
        elif not isinstance(field_type, tuple):
            field_type = (field_type,)

        if (field_type is bool and not isinstance(returned, bool)) or not isinstance(returned, field_type):
            _logger.debug("Field {0!r} should be {1.__name__}, but is {2!r}", field_name, field_type[0], type(returned))
            _abort_bad_request()
        return returned

    def __getitem__(self, item):
        returned = self.get(item, NOTHING)
        if returned is NOTHING:
            _logger.debug("Mandatory field {0!r} not specified", item)
            _abort_bad_request()
        return returned

strict_json = _StrictJSON()

def _abort_bad_request():
    error_abort(400, "bad request")
