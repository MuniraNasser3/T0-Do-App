from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text 
from database import Base #A base class from database.py that all models must inherit from to register the table with SQLAlchemy

class User(Base): # define table named users , User class represents each row in that table
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True) #primary_key=True: Automatically increments and identifies each user uniquely.
    username = Column(String, unique=True, index=True)#unique=True: No two users can have the same username.
    # index=True: Makes searching faster
    hashed_password = Column(String) #Stores the hashed version of the password

class Todo(Base): #Defines a table named todos
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True) #Unique ID for each to-do task.
    title = Column(Text, index=True)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))  # Link each task to a user

