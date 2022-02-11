from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
app = Flask(__name__)
app.config.from_object(Config)

#creating instance of SQLALCHEMY object and binding it with flask object
db = SQLAlchemy(app)

#configure alembic to work with flask instance and db
migrate=Migrate(app,db)

#authors is responsible to connect logigc and www 
from book_library_app import authors
#models is responsible for creating and manage data model in db
from book_library_app import models 
#manage is custom logic using click framework to execute custom CLI comands 
#responsible for adding or remove sample data from database
from book_library_app import db_manage_commends
#import custom HTTP ERRORS handling 
from book_library_app import errors