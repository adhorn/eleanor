from flask import current_app, g, request, jsonify
from functools import wraps
import json
from datetime import datetime
from eleanor.celery import tasks


def api_error_response(code=404, message="Resource not found", errors=list()):
    response = jsonify(
        dict(code=code, message=message, errors=errors, success=False))
    response.status_code = code
    return response


def bad_json_error_response():
    return api_error_response(
        code=400,
        message="Please provide valid JSON."
    )


class ModelJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return json.JSONEncoder.default(self, obj)


def json_response(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        result = fn(*args, **kwargs)
        if isinstance(result, current_app.response_class):
            return result
        if isinstance(result, (list, tuple)):
            result = {'items': result}
        data = json.dumps(result, cls=ModelJSONEncoder)
        return current_app.response_class(data, mimetype='application/json')
    return wrapped


def addtask(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        result = fn(*args, **kwargs)
        tasks.add.delay(10, 30)
        return result
    return wrapped
