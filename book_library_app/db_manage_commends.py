from book_library_app import app
from book_library_app import db
from book_library_app.models import Authors
import json
from pathlib import Path
from datetime import datetime

@app.cli.group()
def db_manage():
    """Database managment commends"""
    pass

@db_manage.command()
def add_data():
    """Add sample data to database"""
    try:
        authors_path=Path(__file__).parent/'samples'/'authors.json'
        with open(authors_path) as file:
            data_json=json.load(file)
        for item in data_json:
            item['birth_date']=datetime.strptime(item['birth_date'],'%d-%m-%Y').date()
            author=Authors(**item)
            db.session.add(author)
        db.session.commit()
        print('Data has been sucessfully added to database')
    except Exception as exc:
        print(f'Unexcepted error: {exc}')


@db_manage.command()
def remove_data():
    """Remove all data from database"""
    try:
        db.session.execute('TRUNCATE TABLE authors')
        print('Data has been sucessfully removed from database')
        db.session.commit()
    except Exception as exc:
        print(f'Unexcepted error: {exc}')