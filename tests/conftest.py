import pytest
from book_library_app import create_app, db
from book_library_app.commands.db_manage_commands import add_data


@pytest.fixture
def app():
    app = create_app("testing")

    with app.app_context():
        db.create_all()

    yield app

    app.config["DB_FILE_PATH"].unlink(missing_ok=True)


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def user(client):
    user = {"username": "test321", "password": "1234536", "email": "test2@gmail.com"}

    client.post("/api/v1/auth/register", json=user)
    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": user["username"], "password": user["password"]},
    )

    return response.get_json()["token"]


@pytest.fixture
def sample_data(app):
    runner = app.test_cli_runner()
    runner.invoke(add_data)


@pytest.fixture
def author():
    return {"first_name": "George", "last_name": "Orwell", "birth_date": "25-06-1903"}
