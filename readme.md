# Book Library REST API

## REST API for online library 
---
### It supports
- authors of books 
- books resources
- user voting system 
- authentication(JWT TOKEN)
- image media handling
- password reset via email
- CI/CD pipeline
---
### The api is hosted [here](https://book-library-app-project.herokuapp.com//api/v1/authors?fields=id,first_name,birth_date&sort=birth_date&birth_date[gte]=21-06-1948&page=1&limit=4). 

---
The **documentation** can be found in **documentation.html** or [here](https://documenter.getpostman.com/view/17812835/UVknuwQM)

---
### Setup with Docker Compose

- clone repository\
`git clone https://github.com/KostkaMateusz/flask_start.git`

- navigate to folder with project

- run command\
`docker compose -f .\docker-compose-dev.yml up`

- in order to stop container and clear all data\
`docker compose -f .\docker-compose-dev.yml down --rmi all --volumes` 

### Setup

- clone repository\
`git clone https://github.com/KostkaMateusz/flask_start.git`

- create database and user or use [sample database](#sample-database)

- rename env.example to .env and set your values (exapmle of .env file)
```ini
SECRET_KEY='SOMERANDOMSTRING'
SQLALCHEMY_DATABASE_URI=sqlite:///${app_dir}
email_password='password for dev mail'
sender_email='dev mail'
```

- create virtual environment\
`python -m venv venv`

- for Ubuntu you also might want to install libpq-dev\
`sudo apt-get install libpq-dev`

- install packages from requirements.txt\
`pip install -r requirements.txt`

- Run migration to a database\
`flask db upgrade`

- Start flask server\
`flask run` 


### Sample data
You can import sample data from book_library_api/samples
- To import sample data to a database:\
`flask db-manage add-data`

- To delete sample data from database:\
`flask db-manage remove-data`

### Tests
In order to execute test locaten in test run\
`python -m pytest tests/`

### Techonolgies/Tools:
- Flask
- AWS S3
- SQLAlchemy
- marshmallow
- alembic
- PyJWT
- gunicorn
- psycopg2
- pytest


### Objects Relation Model(ORM):
![Objects Relation Model](/db_diagram.png "Objects Relation Model")