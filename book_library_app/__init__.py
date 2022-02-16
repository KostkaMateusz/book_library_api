from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# creating instance of SQLALCHEMY object and binding it with flask object
db = SQLAlchemy()

# configure alembic to work with flask instance and db
migrate = Migrate()


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)

    # manage is custom logic using click framework to execute custom CLI comands
    # responsible for adding or remove sample data from database
    from book_library_app.commands import db_manage_bp
    # import custom HTTP ERRORS handling
    from book_library_app.errors import errors_bp
    # authors is responsible to connect logigc and www
    from book_library_app.authors import authors_bp
    from book_library_app.books import books_bp
    from book_library_app.auth import auth_bp

    app.register_blueprint(db_manage_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(authors_bp, url_prefix='/api/v1')
    app.register_blueprint(books_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

    return app
