from sqlalchemy import desc
from book_library_app import db
from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime
from flask_sqlalchemy import BaseQuery
from werkzeug.datastructures import ImmutableDict
# create data base table from class Object relation Maping


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
    def apply_order(querry: BaseQuery, sort_keys: str) -> BaseQuery:
        if sort_keys:
            for key in sort_keys.split(','):
                desc = False
                if key.startswith('-'):
                    key = key[1:]
                    desc = True
                column_attr = getattr(Author, key, None)
                if column_attr is not None:
                    query = querry.order_by(
                        column_attr.desc()) if desc else querry.order_by(column_attr)
        return query

    @staticmethod
    def apply_filter(query: BaseQuery, params: ImmutableDict) -> BaseQuery:
        for param, value in params.items():
            if param not in {'fields', 'sort'}:
                column_attr = getattr(Author, param, None)
                if column_attr is not None:
                    if param == 'birth_date':
                        try:
                            value = datetime.strptime(value, '%d-%m-%Y').date()
                        except ValueError:
                            continue
                    query = query.filter(column_attr == value)
        return query


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
