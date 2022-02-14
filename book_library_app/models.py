from datetime import datetime, date
from book_library_app import db
from marshmallow import Schema, fields, validate, validates, ValidationError


# models is responsible for creating and manage data model in db


# create data base table from class Object relation Maping

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    books = db.relationship(
        'Book', back_populates='author', cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>: {self.first_name}{self.last_name}'

    @staticmethod
    def additional_validation(param: str, value: str) -> date:
        if param == 'birth_date':
            try:
                value = datetime.strptime(value, '%d-%m-%Y').date()
            except ValueError:
                value = None
        return value


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    isbn = db.Column(db.BigInteger, nullable=False, unique=True)
    number_of_pages = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey(
        'authors.id'), nullable=False)
    author = db.relationship('Author', back_populates='books')

    def __repr__(self):
        return f'{self.title}-{self.author.first_name} {self.author.last_name} '


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
