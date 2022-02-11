from flask import request
from werkzeug.exceptions import UnsupportedMediaType
from functools import wraps

def validate_json_content_type(func):
    @wraps(func)
    def wrapper(*args,**keargs):
        data=request.get_json()
        if data is None:
            raise   UnsupportedMediaType('Content type must be appliacation/json')
        return finc(*args,**kwargs)
    return wrapper