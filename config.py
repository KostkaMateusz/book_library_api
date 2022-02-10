import os
from pathlib import Path
from dotenv import load_dotenv

#look for parent folder so Path to __file__ from which is launch then parent
#according to 12 steps of programing we should not have secret key in git

base_dir=Path(__file__).parent 
#from parent dir to file
env_file=base_dir/'.env'
#accualy loading env to enviroment
load_dotenv(env_file)


class Config:
    #DEBUG=True
    #os can now take from loaded env our key
    SECRET_KEY=os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS=False

