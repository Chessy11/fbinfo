# read .env file and give variables to the json file
import os 
#import dotenv
from dotenv import load_dotenv
from os.path import join, dirname


class Config:
    # get username and password from .env file
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    username = os.environ.get("username")
    password = os.environ.get("password")
    print(username)
    
    