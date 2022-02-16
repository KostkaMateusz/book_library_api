import os
from pathlib import Path
from dotenv import load_dotenv

# look for parent folder so Path to __file__ from which is launch then parent
# according to 12 steps of web programing we should not have secret key in git

base_dir = Path(__file__).parent
# from parent dir to file
env_file = base_dir/'.env'
# accualy loading env to enviroment
load_dotenv(env_file)


class Config:
    # DEBUG=True
    # os can now take from loaded env our key
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # from enviromant take URI to database
    SQLALCHEMY_DATABASE_URI = ''
    # if set to true sql alchemy will track modyfication to the object
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # variable with number of records in site using pagination
    PER_PAGE = 5
    JWT_EXPIRED_MINUTES=30


class DevelpmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')


class TestingConfig(Config):
    DB_FILE_PATH=base_dir/'tests'/'test.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_FILE_PATH}'
    DEBUG=True
    TESTING=True

config={
    'development':DevelpmentConfig,
    'testing':TestingConfig
}
    