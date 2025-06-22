from passlib.context import CryptContext #help us securely hash passwords
from jose import JWTError, jwt #This is used for JWT (JSON Web Tokens) which is how users stay logged in
from datetime import datetime, timedelta # We use this to set an expiration time for the token 

# Setup
SECRET_KEY = "your_secret_key"#Without it users can’t prove they are who they say they are
ALGORITHM = "HS256" #The method used to encrypt the token
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #This sets up how we’ll hash passwords.using bcrypt which is a strong way to scramble passwords

def get_password_hash(password):#This function takes a plain password  and turns it into scrambled 
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):# checks if a users login password matches the scrambled version saved in the DB
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):#This function creates the token that will be sent to the user after login
    to_encode = data.copy() #Make a copy of the users info before adding extra info
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) #Set the expiration time
    to_encode.update({"exp": expire}) #Add that expiration into the token
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # encode or create the token using the data, secret key, and algorithm
