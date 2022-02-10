from book_library_app import db
from marshmallow import Schema, fields


#create data base table from class Object relation Maping
class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>: {self.first_name}{self.last_name}'

class AuthorSchema(Schema):
    id=fields.Integer()
    first_name=fields.String()
    last_name=fields.String()
    birth_date=fields.Date('%d-%m-%Y')

author_schema=AuthorSchema()