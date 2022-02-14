import re
from functools import wraps
from typing import Tuple
from book_library_app import Config
from flask import request, url_for, current_app
from flask_sqlalchemy import DefaultMeta ,BaseQuery
from werkzeug.exceptions import UnsupportedMediaType
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.expression import BinaryExpression

COMPARISION_OPERATORS_RE = re.compile(r'(.*)\[(gte|gt|lte|lt)\]')


def validate_json_content_type(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.get_json()
        if data is None:
            raise UnsupportedMediaType(
                'Content type must be appliacation/json')
        return func(*args, **kwargs)
    return wrapper


def get_schema_args(model: DefaultMeta) -> dict:
    schema_args = {'many': True}
    fields = request.args.get('fields')
    if fields:
        schema_args['only'] = [field for field in fields.split(
            ',') if field in model.__table__.columns]
    return schema_args


def apply_order(model: DefaultMeta, querry: BaseQuery) -> BaseQuery:
    sort_keys = request.args.get('sort')
    if sort_keys:
        for key in sort_keys.split(','):
            desc = False
            if key.startswith('-'):
                key = key[1:]
                desc = True
            column_attr = getattr(model, key, None)
            if column_attr is not None:
                querry = querry.order_by(
                    column_attr.desc()) if desc else querry.order_by(column_attr)
    return querry


def get_filter_argument(column_name: InstrumentedAttribute, value: str, operator: str) -> BinaryExpression:
    operator_mapping = {
        '==': column_name == value,
        'gte': column_name >= value,
        'gt': column_name > value,
        'lte': column_name <= value,
        'lt': column_name < value
    }
    return operator_mapping[operator]


def apply_filter(model: DefaultMeta, query: BaseQuery) -> BaseQuery:
    for param, value in request.args.items():
        if param not in {'fields', 'sort', 'page', 'limit'}:
            operator = '=='
            match = COMPARISION_OPERATORS_RE.match(param)
            if match is not None:
                param, operator = match.groups()
            column_attr = getattr(model, param, None)
            if column_attr is not None:
                value=model.additional_validation(param,value)
                if value is None:
                    continue                 
                filter_argument = get_filter_argument(
                    column_attr, value, operator)
                query = query.filter(filter_argument)
    return query


def get_pagination(querry: BaseQuery,func_name:str) -> Tuple:
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', current_app.config.get('PER_PAGE',5), type=int)
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
