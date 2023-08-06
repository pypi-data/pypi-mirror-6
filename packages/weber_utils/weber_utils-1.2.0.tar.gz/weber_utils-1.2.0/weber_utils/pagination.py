import functools

from flask import jsonify, request

from ._compat import httplib
from .request_utils import dictify_model, error_abort


def paginate_query(query, default_page_size=100, renderer=dictify_model, max_page_size=100):
    try:
        page_size = int(request.args.get("page_size", default_page_size))
        page = int(request.args.get("page", 1))
    except ValueError:
        error_abort(httplib.BAD_REQUEST, "Invalid integer value")

    if page_size == 0 or page_size > max_page_size:
        error_abort(httplib.BAD_REQUEST, "Invalid page size")

    num_objects = query.count()

    return {
            "metadata": {
                "total_num_objects": num_objects,
                "total_num_pages": _ceil_div(num_objects, page_size) or 1,
                "page": page,
                "page_size": page_size,
            },
            "result": [renderer(obj) for obj in query.offset((page-1)*page_size).limit(page_size)],
        }

def _ceil_div(value, divisor):
    returned = float(value) / divisor
    if int(returned) != returned:
        return int(returned) + 1
    return int(returned)

def paginated_view(func=None, **pagination_kwargs):
    if func is None:
        return functools.partial(paginated_view, **pagination_kwargs)
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        returned = func(*args, **kwargs)
        return jsonify(paginate_query(returned, **pagination_kwargs))

    return new_func
