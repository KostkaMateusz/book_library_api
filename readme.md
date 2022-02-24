# Book Library REST API

## REST API for online library 
---
### It supports:
- authors of books 
- books resources
- user voting system 
- authentication(JWT TOKEN)
- reset password via email

---
The **documentation** can be found in **documentation.html** or [here](https://documenter.getpostman.com/view/17812835/UVknuwQM)

---

### Setup

- clone repository
`git clone https://github.com/KostkaMateusz/flask_start.git`

- create database and user

- rename env.example to .env and set your values (exapmle of .env)
`SECRET_KEY='SOMERANDOMSTRING'`
`SQLALCHEMY_DATABASE_URI=sqlite:///${app_dir}`
`email_password='password for dev mail'`
`sender_email='dev mail'`
- creat a virtual enviroment
`python -m venv venv`

- instal pacages from requirements.txt
`pip install -r requirements.txt`

- Run migration to a database
`flask db upgrade`

- Start flask server
`flask run` 


### Note
You can import sample data from book_library_api/samples
- To import sample data to a database:
`flaks db-manage add-data`
- To delete sample data from database:
`flaks db-manage remove-data`

### Tests
In order to execute test locaten in test run 
`python -m pytest tests/`

### Techonolgies/Tools:
- Flask
- SQLAlchemy
- marshmallow
- alembic
- PyJWT
- gunicorn
- psycopg2
- pytest

### Objects Relation Model(ORM):
![Objects Relation Model](/db_diagram.png "Objects Relation Model")