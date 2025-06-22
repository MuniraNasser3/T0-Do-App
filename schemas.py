# schemas.py  defines how data is sent to and from your API using Pydantic models.
from pydantic import BaseModel# imported BaseModel because we need it to build  data schemas for user input/output.

# User Schemas
class UserCreate(BaseModel):#Used when someone is registering , This schema  expect a username and password as strings
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):#Used when we send user data back to the frontend
    id: int
    username: str

    class Config: #HHere are some extra rules for how this schema works
        orm_mode = True #orm means: Object Relational Mapper (fancy word for database objects)
       #It’s OK to read data from database objects, not just dicts
       #Without orm_mode = True, Pydantic would only understand normal dictionaries and say “I don’t know how to read this object!
       #With orm_mode = True, it says: “Okay! I know how to read info from objects too.”

# Todo Schemas
class TodoCreate(BaseModel):
    title: str

class TodoRead(BaseModel):#how a To-Do item should look when we return it to the user
    id: int
    title: str
    completed: bool
    user_id: int   # So we know who owns this todo

    class Config:
        orm_mode = True
#we get data from a SQLAlchemy model (object), not just a dictionary 
# It helps FastAPI return the data from the database model as a clean response.

