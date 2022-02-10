from book_library_app import db



#create data base table from class Object relation Maping
class Authors(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>: {self.first_name}{self.last_name}'
