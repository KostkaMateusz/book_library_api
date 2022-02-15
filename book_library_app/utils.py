import re
from functools import wraps
from typing import Tuple
from flask import request, url_for, current_app
from flask_sqlalchemy import DefaultMeta, BaseQuery
from werkzeug.exceptions import UnsupportedMediaType
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.expression import BinaryExpression
from book_library_app.debug import debug
from flask import abort
import jwt

COMPARISION_OPERATORS_RE = re.compile(r'(.*)\[(gte|gt|lte|lt)\]')


def validate_json_content_type(func):
    """Custom decorator check if send data from request is in json data format"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.get_json()
        if data is None:
            raise UnsupportedMediaType(
                'Content type must be appliacation/json')
        return func(*args, **kwargs)
    return wrapper


@debug
def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = None
        auth = request.headers.get('Authorization')
        if auth:
            token = auth.split(' ')[1]
        if token is None:
            abort(401, description='Missing token. Please login or register')

        try:
            payload = jwt.decode(token, current_app.config.get(
                'SECRET_KEY'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            abort(401, description='Token expired. Please login to get new token')
        except jwt.InvalidTokenError:
            abort(401, description='Invalid token. Please login or register')
        else:
            return func(payload['user_id'], *args, **kwargs)
    return wrapper


def get_schema_args(model: DefaultMeta) -> dict:
    """Which fields are to be displayed"""
    schema_args = {'many': True}
    fields = request.args.get('fields')
    # here we dynamicly build arguments to a only parameter in Schema object in form of dict
    if fields is not None:
        schema_args['only'] = [field for field in fields.split(
            ',') if field in model.__table__.columns]
    return schema_args


def apply_order(model: DefaultMeta, querry: BaseQuery) -> BaseQuery:
    """Get sort arguments from request"""
    sort_keys = request.args.get('sort')
    if sort_keys is not None:
        for key in sort_keys.split(','):
            desc = False
            if key.startswith('-'):
                key = key[1:]
                desc = True
            column_attr = getattr(model, key, None)
            if column_attr is not None:
                # specify sort based of what column if desc True sort in desc order
                querry = querry.order_by(
                    column_attr.desc()) if desc else querry.order_by(column_attr)
    return querry


def get_filter_argument(column_name: InstrumentedAttribute, value: str, operator: str) -> BinaryExpression:
    """Change http arguments to a boolean expresion"""
    operator_mapping = {
        '==': column_name == value,
        'gte': column_name >= value,
        'gt': column_name > value,
        'lte': column_name <= value,
        'lt': column_name < value
    }
    return operator_mapping[operator]


def apply_filter(model: DefaultMeta, query: BaseQuery) -> BaseQuery:
    """Show entry which meet requirments from request"""
    for param, value in request.args.items():

        # all parameters that are not in fields, sort,page and limit are filtering arguments
        if param not in {'fields', 'sort', 'page', 'limit'}:
            # defoult operator if none argument passed
            operator = '=='
            # return what symbols patch pre-compiled pattern
            match = COMPARISION_OPERATORS_RE.match(param)
            if match is not None:
                # param-what is not matched, operator-what is matched e.g birth_date: gte
                param, operator = match.groups()
            column_attr = getattr(model, param, None)

            if column_attr is not None:
                # field birth_date required additional validation, all data object must have implemented addidional validation function
                value = model.additional_validation(param, value)
                if value is None:
                    continue
                filter_argument = get_filter_argument(
                    column_attr, value, operator)
                query = query.filter(filter_argument)
    return query


def get_pagination(querry: BaseQuery, func_name: str) -> Tuple:
    """Return divided data to pages with adres for next and previous page"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get(
        'limit', current_app.config.get('PER_PAGE', 5), type=int)
    # in order to paginate pages save their origin parameters save it to a variabla and built page with them
    params = {key: value for key, value in request.args.items()
              if key != 'page'}

    paginate_object = querry.paginate(page, limit, False)
    pagination = {
        'total_pages': paginate_object.pages,
        'total_records': paginate_object.total,
        'current_page': url_for(func_name, page=page, **params)
    }
    if paginate_object.has_next:
        pagination['next_page'] = url_for(
            func_name, page=page+1, **params)

    if paginate_object.has_prev:
        pagination['previous_page'] = url_for(
            func_name, page=page-1)

    return paginate_object.items, pagination
