# main.py
from fastapi import FastAPI, Depends, HTTPException, status # here create fastapi app , depends:Instead of repeating the same code over and over like open a DB connection.. so we write that logic once in a separate function and inject it wherever needed.
# HTTPException :raise custom errors with messages and status codes , statues: Provides readable HTTP status codes (like status.HTTP_404_NOT_FOUND)

from fastapi.middleware.cors import CORSMiddleware # allows the frontend to talk to the backend even if they on diff port
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm #HTTPBearer check Did you bring your (token) with you
#Bearer Token = your secret card 
#HTTPBearer =  checks your card every time you enter 
#HTTPAuthorizationCredentials : it takes out just the token part EX : Authorization: Bearer abc123token , so it will take abc123token
#OAuth2PasswordRequestForm :check if the username and password are correct, and then give a token back if they are
from sqlalchemy.orm import Session #This is how you interact with your tables (query, add, update, delete)
from jose import JWTError, jwt
#jwt(json web token) : 	To make and check special tokens,  you get after logging in successfully , This user is allowed to enter the app 
# jwterror: Catches errors if the token is broken or expired.

from typing import List, Optional # list : use a list, and I want to specify what type of things are inside that list
#optional : A value that can be None (missing)
import models, schemas

from auth import (#go to auth.py and bring this :
    get_password_hash, verify_password, create_access_token,
    SECRET_KEY, ALGORITHM # seceret key : A secret string used to sign the token only server now it
    #algorithm : The method used to encrypt the token
)
from database import SessionLocal, engine, Base

# FastAPI instance

app = FastAPI(title=" To-Do App ") # create fast api app


app.add_middleware( #This allows frontend to talk to the backend safely.
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # here who is allowed 
    allow_credentials=True, # Allows cookies or auth headers to be sent
    allow_methods=["*"],#Allow all types of requests (GET, POST)...
    allow_headers=["*"],# allow any headers
)


# DB Setup

Base.metadata.create_all(bind=engine) #This creates the tables in your database if they don’t already exist

# Security
oauth2_scheme = HTTPBearer() # make sure the user has a key (token) and check it


def get_db():# function give me a connection to DB 
    db = SessionLocal() # open a session 
    try:
        yield db # give the session to any endpoint that need it 
    finally:
        db.close()


def get_current_user( # This function verifies the user from their token
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme), #Automatically grabs the Bearer token from the header
    db: Session = Depends(get_db), #Opens a DB session to find the user in the database
) -> models.User:
    creds_exc = HTTPException( # here what to do if the token is invalid ( bad token or no users)
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try: # decode the token , encode : hidden , decode : open and read what is inside 
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])# here take the token, unlock it using the secret key, and check if it’s valid
        #token.credentials → The actual token from the user
        #SECRET_KEY → The secret code used to sign and verify the token
        #algorithms=[ALGORITHM] → The method used to verify like HS256
        username: Optional[str] = payload.get("sub")#stands for subject ,it’s the user the token is about
        if username is None:
            raise creds_exc
    except JWTError: #if error raised we catch it with this and block the user from accessing the protected route
        raise creds_exc

    user = db.query(models.User).filter(models.User.username == username).first()#checks if a user with that username exists in the DB
    if user is None:
        raise creds_exc

    return user # if every thing work 

# Public routes : pages or actions anyone can use

@app.get("/") #home page route 
def read_root(): #When you open http://127.0.0.1:8000/, it runs this function ( for testing )
    return {"message": "Hello, FastAPI!"}


@app.post("/register", status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):# depends : Gets a database session to run SQL queries.
 #schemas.UserCreate :   class (schema) that created in schemas.py This class tells FastAPI When someone sends data to the /register endpoint, make sure it includes:
#a username , a password  ,And don't accept anything extra or invalid.  

    if db.query(models.User).filter(models.User.username == user.username).first():#Check if username already exists . first() here only get the first result
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = models.User(
        username=user.username,
        hashed_password=get_password_hash(user.password),# turns the password into a secure hashed version so it’s not stored in plain text.
    )
    db.add(new_user) # save the new user , Add to the session
    db.commit() # Save to the database
    db.refresh(new_user)  # Reload the user with updated info
    return {"message": "User registered successfully"}


@app.post("/login") #This is a POST endpoint that gets triggered when a user submits the login form.
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),#Automatically reads the form data (username and password) from the request body
    db: Session = Depends(get_db),#Gives me access to the database for querying
):
    user = ( # Check if the user exists
        db.query(models.User)
        .filter(models.User.username == form_data.username)
        .first()
    )
    if not user or not verify_password(form_data.password, user.hashed_password): #If no user exists OR password check fails using verify_password()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(data={"sub": user.username}) #If the login was successful, create a JWT token with the username 
    #This token will be used later for authentication
    return {"access_token": access_token, "token_type": "bearer"} #This token is saved in the browser or frontend and sent with every future request to prove the user is logged in.


@app.get("/profile", response_model=schemas.UserRead)#It allows a logged-in user to see their own profile 
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

# Protected To-Do Endpoints
@app.post("/todos/", response_model=schemas.TodoRead) #create a new to-do item, and it requires the user to be logged in
def create_todo(#It creates a new task for the currently logged-in user and saves it to the database
    todo: schemas.TodoCreate,

    current_user: models.User = Depends(get_current_user),#Extracts the logged-in user based on the Bearer token sent in the header.
    db: Session = Depends(get_db),#depends:Gets a database session so we can interact with the DB (add, query, commit,...
):
    db_todo = models.Todo(#Creates a new Todo object using the data from the request.
        title=todo.title,
        completed=False,
        user_id=current_user.id,
    )
    db.add(db_todo)#adds the new todo to the session.
    db.commit()# saves the change to the database.
    db.refresh(db_todo)# updates the Python object with the latest data from the database 
    return db_todo# sends  the newly created task back to the user in the response


@app.get("/todos/", response_model=List[schemas.TodoRead])#return a list of tasks
def read_todos(
    current_user: models.User = Depends(get_current_user),#vFastAPI automatically gets the logged-in user by checking the token.
    db: Session = Depends(get_db),#Creates a database session for querying data.
):
    return (
        db.query(models.Todo)#Start a database query on the Todo table
        .filter(models.Todo.user_id == current_user.id) #Filter only the tasks that belong to the currently logged-in user.
        .all()
    )


@app.put("/todos/{todo_id}", response_model=schemas.TodoRead)#It expects a todo_id in the URL
def mark_complete(
    todo_id: int, # The ID of the to-do to update 
    current_user: models.User = Depends(get_current_user), # Gets the currently logged-in user (token-based).
    db: Session = Depends(get_db), #Database session used to interact with the database.
):
    todo = ( #Queries the DB for a to-do with this specific id AND that belongs to the current user.
        db.query(models.Todo)
        .filter(
            models.Todo.id == todo_id,
            models.Todo.user_id == current_user.id,
        )
        .first()
    )
    if not todo:
        raise HTTPException(status_code=404, detail="task not found")

    todo.completed = True #Marks the task as completed
    db.commit() #Saves the change to the db
    db.refresh(todo) 
    return todo #Sends the updated task back as a response


@app.delete("/todos/{todo_id}") # task id to delete
def delete_todo(
    todo_id: int,
    current_user: models.User = Depends(get_current_user), #Uses the token to get the logged-in user
    db: Session = Depends(get_db),
):
    todo = (#Looks for a task with that todo_id, and checks if it belongs to the current user.
        db.query(models.Todo)
        .filter(
            models.Todo.id == todo_id,
            models.Todo.user_id == current_user.id,
        )
        .first()
    )
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(todo)
    db.commit()
    return {"message": "Task deleted"}





