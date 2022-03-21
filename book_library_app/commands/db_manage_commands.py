from book_library_app import db
from book_library_app.models import Author, Book, User, Votes
import json
from pathlib import Path
from datetime import datetime
from book_library_app.commands import db_manage_bp
from book_library_app.utils import calculate_stats


def load_json_data(file_name: str) -> list:
    authors_path = Path(__file__).parent.parent / "samples" / file_name
    with open(authors_path) as file:
        data_json = json.load(file)
    return data_json


# flask cli group
@db_manage_bp.cli.group()
def db_manage():
    """Database management commends"""
    pass


# function to add data to database from sample
@db_manage.command()
def add_data():
    """Add sample data to database"""
    # connecting with db in case something went wrong with connection
    try:
        data_json = load_json_data("authors.json")
        for item in data_json:
            # in sample data there date is in dd-mm-yyyy
            item["birth_date"] = datetime.strptime(
                item["birth_date"], "%d-%m-%Y"
            ).date()
            # to create instance of a Author from key world argument
            author = Author(**item)
            db.session.add(author)

        data_json = load_json_data("books.json")
        for item in data_json:
            book = Book(**item)
            db.session.add(book)

        data_json = load_json_data("users.json")
        for item in data_json:
            item["password"] = User.generate_hashed_password(item["password"])
            user = User(**item)
            db.session.add(user)

        data_json = load_json_data("votes.json")
        for item in data_json:

            vote = Votes(**item)
            db.session.add(vote)

        db.session.commit()

        calculate_stats([id for id in range(1, len(Book.query.all()))])
        print("Data has been sucessfully added to database")
    except Exception as exc:
        print(f"Unexcepted error: {exc}")


@db_manage.command()
def remove_data():
    """Remove all data from database"""
    try:
        # SQL comant to deleta date from db
        db.session.execute("TRUNCATE TABLE authors RESTART IDENTITY CASCADE;")
        db.session.commit()
        print("Data has been sucessfully removed from database")
    except Exception as exc:
        print(f"Unexcepted error: {exc}")
