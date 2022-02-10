from book_library_app import app
from book_library_app import db
from book_library_app.models import Authors
import json
from pathlib import Path
from datetime import datetime


#flask cli group 
@app.cli.group()
def db_manage():
    """Database managment commends"""
    pass


#function to add data to database from sample 
@db_manage.command()
def add_data():
    """Add sample data to database"""
    #connecting with db in case something went wrong with connection
    try:
        authors_path=Path(__file__).parent/'samples'/'authors.json'
        with open(authors_path) as file:
            data_json=json.load(file)
        for item in data_json:
            # in sample data there date is in dd-mm-yyyy 
            item['birth_date']=datetime.strptime(item['birth_date'],'%d-%m-%Y').date()
            #to create instance of a Author from key world argument
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
        #SQL comant to deleta date from db 
        db.session.execute('TRUNCATE TABLE authors')
        print('Data has been sucessfully removed from database')
        db.session.commit()
    except Exception as exc:
        print(f'Unexcepted error: {exc}')