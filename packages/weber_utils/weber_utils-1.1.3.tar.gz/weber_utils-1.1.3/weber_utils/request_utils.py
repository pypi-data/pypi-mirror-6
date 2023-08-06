import functools

import logbook
import werkzeug.exceptions
from flask import make_response, request

from sqlalchemy.orm import class_mapper

from ._compat import httplib, iteritems, PY2

_logger = logbook.Logger(__name__)

class Parameter(object):

    optional = False

    def __init__(self, parameter_types):
        super(Parameter, self).__init__()
        if parameter_types is str and PY2:
            parameter_types = (str, unicode)
        if not isinstance(parameter_types, tuple):
            parameter_types = (parameter_types,)
        self.types = parameter_types

    def coerce(self, value):
        return self.types[0](value)

class Optional(Parameter):
    optional = True

def get_request_input(schema):
    data = request.json
    convert = False
    if data is None:
        data = dict(iteritems(request.form))
        convert = True
    returned = {}
    missing = set()
    for param_name, param in iteritems(schema):
        if not isinstance(param, Parameter):
            param = Parameter(param)
        if param_name not in data and not param.optional:
            missing.add(param_name)
            continue
        param_value = data[param_name]
        if convert:
            try:
                param_value = param.coerce(param_value)
            except ValueError:
                _logger.debug("Cannot coerce parameter {0} ({1!r})", param_name, param_value)
                error_abort_invalid_type(param_name, param_value)
        if not isinstance(param_value, param.types):
            _logger.debug("Parameter {0} is of invalid type {1!r}", param_name, param_value)
            error_abort_invalid_type(param_name, param_value)
        returned[param_name] = param_value

    if missing:
        _logger.debug("The following parameters are missing: {0}", missing)
        error_abort(httplib.BAD_REQUEST, "The following parameters are missing: {}".format(", ".join(sorted(missing))))

    return returned

def error_abort_invalid_type(param_name, param_value):
    error_abort(httplib.BAD_REQUEST, "Invalid parameter value for {}: {!r}".format(param_name, param_value))

def error_abort(code, message):
    raise HTTPException(code, message)

class HTTPException(werkzeug.exceptions.HTTPException):
    def __init__(self, code, message):
        super(HTTPException, self).__init__()
        self.code = code
        self.message = message

    def get_response(self, _): # pragma: nocover
        return make_response((self.message, self.code, {}))

def takes_schema_args(**schema):
    def decorator(func):
        @functools.wraps(func)
        def new_func():
            return func(**get_request_input(schema))
        return new_func
    return decorator

def dictify_model(obj):
    """
    Turns an SQLAlchemy object to a JSON dict
    """
    return {column.key: getattr(obj, column.key) for column in class_mapper(obj.__class__).columns}
