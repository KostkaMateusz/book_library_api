from datetime import date, datetime, timedelta
from sqlalchemy import ForeignKey
import jwt
from flask import current_app
from marshmallow import Schema, ValidationError, fields, validate, validates
from werkzeug.security import generate_password_hash, check_password_hash
from book_library_app import db

# models is responsible for creating and manage data model in db


class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    books = db.relationship(
        "Book", back_populates="author", cascade="all, delete-orphan"
    )

    author_average_score = db.Column(db.Float, nullable=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>:{self.first_name}{self.last_name}"

    @staticmethod
    def additional_validation(param: str, value: str) -> date:
        if param == "birth_date":
            try:
                value = datetime.strptime(value, "%d-%m-%Y").date()
            except ValueError:
                value = None
        return value


class AuthorSchema(Schema):
    id = fields.Integer(dump_only=True)
    first_name = fields.String(required=True, validate=validate.Length(max=50))
    last_name = fields.String(required=True, validate=validate.Length(max=50))
    birth_date = fields.Date("%d-%m-%Y", required=True)
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=["author"])))

    author_average_score = fields.Float()

    @validates("birth_date")
    def validate_birth_date(self, value):
        if value > datetime.now().date():
            raise ValidationError(
                f"Birth date must be lower than {datetime.now().date()}"
            )


class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    isbn = db.Column(db.BigInteger, nullable=False, unique=True)
    number_of_pages = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)
    author = db.relationship("Author", back_populates="books")

    number_of_votes = db.Column(db.Integer, nullable=True, default=0)
    score_sum = db.Column(db.Integer, nullable=True, default=0)
    average_book_score = db.Column(db.Float, nullable=True, default=0)

    comment = db.relationship("Votes")

    def __repr__(self):
        return f"{self.title}-{self.author.first_name}-{self.author.last_name}"

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class BookSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(max=50))
    isbn = fields.Integer(required=True)
    number_of_pages = fields.Integer(required=True)
    description = fields.String()
    author_id = fields.Integer(load_only=True)
    author = fields.Nested(lambda: AuthorSchema(only=["id", "first_name", "last_name"]))

    number_of_votes = fields.Integer()
    score_sum = fields.Integer()
    average_book_score = fields.Float()

    # comment = fields.Nested(lambda: VotesSchema(
    #     only=['comment_id', 'points', 'comment_text']))

    @validates("isbn")
    def validate_isbn(self, number):
        if len(str(number)) != 13:
            raise ValidationError("ISBN number must have 13 digits")


class Votes(db.Model):
    __tablename__ = "votes"
    comment_id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer)
    comment_text = db.Column(db.String(255))
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class VotesSchema(Schema):
    comment_id = fields.Integer(dump_only=True)
    points = fields.Integer()
    comment_text = fields.String(validate=validate.Length(max=255))
    book_id = fields.Integer()
    user_id = fields.Integer()

    @validates("points")
    def validate_points(self, points):
        if points < 0 or points > 5:
            raise ValidationError("points number must be between 1 and 5")


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)

    comment = db.relationship("Votes")

    reset_pass = db.relationship("HashResetTable")

    @staticmethod
    def generate_hashed_password(password: str) -> str:
        return generate_password_hash(password)

    def is_password_valid(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def generate_jwt(self):
        payload = {
            "user_id": self.id,
            "exp": datetime.utcnow()
            + timedelta(minutes=current_app.config.get("JWT_EXPIRED_MINUTES", 30)),
        }

        return jwt.encode(payload, current_app.config.get("SECRET_KEY"))


class HashResetTable(db.Model):
    __tablename__ = "hash_reset"
    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    hash_code = db.Column(db.String(255))
    user_id = db.Column(db.Integer, ForeignKey("users.id"))

    def generate_jwt(self):
        payload = {
            "user_id": self.id,
            "exp": datetime.utcnow()
            + timedelta(minutes=current_app.config.get("JWT_EXPIRED_MINUTES", 30)),
        }
        return jwt.encode(payload, current_app.config.get("SECRET_KEY") + "22i7czworek")


class HashResetTableSchema(Schema):
    id = fields.Integer(dumb_only=True)
    creation_date = fields.DateTime(dump_only=True)
    hash_code = fields.String(required=True)


class UserSchema(Schema):
    id = fields.Integer(dumb_only=True)
    username = fields.String(required=True, validate=validate.Length(max=255))
    email = fields.Email(required=True)
    password = fields.String(
        required=True, load_only=True, validate=validate.Length(min=6, max=255)
    )
    creation_date = fields.DateTime(dump_only=True)


class UserPasswordUpdateSchema(Schema):
    current_password = fields.String(
        required=True, load_only=True, validate=validate.Length(min=6, max=255)
    )
    new_password = fields.String(
        required=True, load_only=True, validate=validate.Length(min=6, max=255)
    )


author_schema = AuthorSchema()
book_schema = BookSchema()
user_schema = UserSchema()
user_password_update_schema = UserPasswordUpdateSchema()
votes_schema = VotesSchema()
