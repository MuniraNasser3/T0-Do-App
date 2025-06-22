from sqlalchemy import create_engine #import create engine function 
# sqlalchemy its a python library used to interact with DB lets you write Python code instead of SQL queries to interact with your database.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker 

import os #Used here to read environment variables, like  database URL from the .env file

from dotenv import load_dotenv # here we load the .env file and set env variable

load_dotenv()# here we load the .env file and set env variable

DATABASE_URL = os.getenv("DATABASE_URL") # here we read the variable 

engine = create_engine(DATABASE_URL)#oppen a connection between the python app and the DB
SessionLocal = sessionmaker(bind=engine) # create session to intract with DB
Base = declarative_base() # It creates a starting point that other classes tables can build on to become real db tables
# so when we dont add base it will consider it as normal class which does nothing in the db
