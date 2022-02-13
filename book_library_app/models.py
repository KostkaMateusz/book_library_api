# models is responsible for creating and manage data model in db


from sqlalchemy import desc
from book_library_app import db
from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime
from flask_sqlalchemy import BaseQuery
import re
from typing import Tuple
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.expression import BinaryExpression
from flask import request, url_for
from book_library_app import Config
#from book_library_app.authors import get_authors


# create data base table from class Object relation Maping
COMPARISION_OPERATORS_RE = re.compile(r'(.*)\[(gte|gt|lte|lt)\]')


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>: {self.first_name}{self.last_name}'

    @staticmethod
    def get_schema_args(fields: str) -> dict:
        schema_args = {'many': True}
        if fields:
            schema_args['only'] = [field for field in fields.split(
                ',') if field in Author.__table__.columns]
        return schema_args

    @staticmethod
    def apply_order(querry: BaseQuery) -> BaseQuery:
        sort_keys = request.args.get('sort')
        if sort_keys:
            for key in sort_keys.split(','):
                desc = False
                if key.startswith('-'):
                    key = key[1:]
                    desc = True
                column_attr = getattr(Author, key, None)
                if column_attr is not None:
                    querry = querry.order_by(
                        column_attr.desc()) if desc else querry.order_by(column_attr)
        return querry

    @staticmethod
    def get_filter_argument(column_name: InstrumentedAttribute, value: str, operator: str) -> BinaryExpression:
        operator_mapping = {
            '==': column_name == value,
            'gte': column_name >= value,
            'gt': column_name > value,
            'lte': column_name <= value,
            'lt': column_name < value
        }
        return operator_mapping[operator]

    @staticmethod
    def apply_filter(query: BaseQuery) -> BaseQuery:
        for param, value in request.args.items():
            if param not in {'fields', 'sort', 'page', 'limit'}:
                operator = '=='
                match = COMPARISION_OPERATORS_RE.match(param)
                if match is not None:
                    param, operator = match.groups()
                column_attr = getattr(Author, param, None)
                if column_attr is not None:
                    if param == 'birth_date':
                        try:
                            value = datetime.strptime(value, '%d-%m-%Y').date()
                        except ValueError:
                            continue
                    filter_argument = Author.get_filter_argument(
                        column_attr, value, operator)
                    query = query.filter(filter_argument)
        return query

    @staticmethod
    def get_pagination(querry: BaseQuery) -> Tuple:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', Config.PER_PAGE, type=int)
        params = {key: value for key, value in request.args.items()
                  if key != 'page'}
        paginate_object = querry.paginate(page, limit, False)
        pagination = {
            'total_pages': paginate_object.pages,
            'total_records': paginate_object.total,
            'current_page': url_for('authors.get_authors', page=page, **params)
        }
        if paginate_object.has_next:
            pagination['next_page'] = url_for(
                'authors.get_authors', page=page+1, **params)

        if paginate_object.has_prev:
            pagination['previous_page'] = url_for(
                'authors.get_authors', page=page-1)

        return paginate_object.items, pagination


class AuthorSchema(Schema):
    id = fields.Integer(dump_only=True)
    first_name = fields.String(required=True, validate=validate.Length(max=50))
    last_name = fields.String(required=True, validate=validate.Length(max=50))
    birth_date = fields.Date('%d-%m-%Y', required=True)

    @validates('birth_date')
    def validate_birth_date(self, value):
        if value > datetime.now().date():
            raise ValidationError(
                f'Birth date must be lower than {datetime.now().date()}')


author_schema = AuthorSchema()
