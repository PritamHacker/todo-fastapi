from fastapi import FastAPI, Depends, HTTPException, status  
from sqlalchemy.orm import Session  # Import Session class for database operations
from database import SessionLocal, Base, engine  
import models 
from jose import jwt  
from datetime import datetime, timedelta  
from passlib.context import CryptContext  # Import password hashing library
from pydantic import BaseModel  
  


SECRET_KEY = "MyPersonalSecretKey"  # Secret key for JWT encoding and decoding
ALGORITHM = "HS256"  # Algorithm used for JWT encoding and decoding
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Expiry time for access tokens in minutes

app = FastAPI()  # Create an instance of FastAPI
# Create all tables in the database
Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Password hashing context

# Function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to create an access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()  # Create a copy of the data dictionary to encode
    if expires_delta:
        expire = datetime.utcnow() + expires_delta  # Calculate token expiration time
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # Default expiration time if not provided
    to_encode.update({"exp": expire})  # Update token with expiration time
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Encode token using JWT
    return encoded_jwt  # Return the encoded JWT access token


# Dependency to get the database session
def get_db():
    db = SessionLocal()  # Create a database session
    try:
        yield db  # Provide the database session to the request
    finally:
        db.close()  # Close the database session after the request is processed

# Dependency to authenticate user and generate token
def authenticate(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()  # Query the user from the database
    if not user or not verify_password(password, user.password):  # Check if user exists and password is correct
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # Return unauthorized status code
            detail="Incorrect username or password",  # Error message for incorrect credentials
            headers={"WWW-Authenticate": "Bearer"},  # Provide authentication method in headers
        )
    return user  # Return the authenticated user


# Token data model
class TokenData(BaseModel):
    username: str  # Username stored in the token

# POST operation for user login
@app.post("/login")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = authenticate(username, password, db)  # Authenticate user with provided credentials
    if user:
        # Generate JWT token
        access_token = create_access_token(data={"sub": username})  # Create JWT token for the user
        return {"access_token": access_token, "token_type": "bearer"}  # Return the token and its type
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")  # Raise exception for incorrect credentials



# POST operation to create a todo list item
@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo_item(
    title: str,
    content: str,
    current_user: models.User = Depends(authenticate),  # Authenticate the current user
    db: Session = Depends(get_db)  # Dependency to get the database session
):
    try:
        todo_item = current_user.create_todo_item(title=title, content=content)  # Create a new todo item for the current user
        db.add(todo_item)  # Add the todo item to the database
        db.commit()  # Commit the transaction
        db.refresh(todo_item)  # Refresh todo_item to get updated values
        return todo_item  # Return the created todo item
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))



# GET operation to retrieve all todo list items for a specific user
@app.get("/todo/{username}")
async def get_todo_items(username: str, current_user: models.User = Depends(authenticate), db: Session = Depends(get_db)):
    try:
        # Check if the current user is the same as the requested user
        if current_user.username != username:  # Ensure the current user is authorized to access this resource
            raise HTTPException(status_code=403, detail="You are not authorized to access this resource")  # Return forbidden status if not authorized

        # Retrieve the user from the database
        user = db.query(models.User).filter(models.User.username == username).first()  # Query the user by username
        if not user:  # If user not found, raise exception
            raise HTTPException(status_code=404, detail="User not found")  # Return not found status if user not found

        # Retrieve todo list items for the specified user
        todo_items = db.query(models.TodoList).filter(models.TodoList.user_id == user.id).all()  # Query todo items by user id
        return todo_items  # Return todo items for the specified user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# PUT operation to modify a todo list item
@app.put("/todo/{todo_id}")
async def modify_todo_item(todo_id: int, title: str, content: str, current_user: models.User = Depends(authenticate), db: Session = Depends(get_db)):
    try:
        # Check if the todo item exists
        todo_item = db.query(models.TodoList).filter(models.TodoList.id == todo_id).first()  # Query the todo item by id
        if not todo_item:  # If todo item not found, raise exception
            raise HTTPException(status_code=404, detail="Todo item not found")  # Return not found status if todo item not found

        # Check if the authenticated user is the owner of the todo item
        if todo_item.user_id != current_user.id:  # Ensure current user is authorized to modify this todo item
            raise HTTPException(status_code=403, detail="You are not authorized to modify this todo item")  # Return forbidden status if not authorized

        # Update the todo item
        todo_item.title = title  # Update todo item title
        todo_item.content = content  # Update todo item content
        db.commit()  # Commit changes to the database
        db.refresh(todo_item)  # Refresh todo_item to get updated values

        return todo_item  # Return modified todo item
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# DELETE operation to delete a todo list item
@app.delete("/todo/{todo_id}")
async def delete_todo_item(todo_id: int, current_user: models.User = Depends(authenticate), db: Session = Depends(get_db)):
    try:
        # Check if the todo item exists
        todo_item = db.query(models.TodoList).filter(models.TodoList.id == todo_id).first()  # Query the todo item by id
        if not todo_item:  # If todo item not found, raise exception
            raise HTTPException(status_code=404, detail="Todo item not found")  # Return not found status if todo item not found

        # Check if the authenticated user is the owner of the todo item
        if todo_item.user_id != current_user.id:  # Ensure current user is authorized to delete this todo item
            raise HTTPException(status_code=403, detail="You are not authorized to delete this todo item")  # Return forbidden status if not authorized

        # Delete the todo item
        db.delete(todo_item)  # Delete the todo item from the database
        db.commit()  # Commit changes

        return {"message": "Todo item deleted successfully"}  # Return success message
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# POST operation to create a new user
@app.post("/users/")
async def create_user(username: str, password: str, db: Session = Depends(get_db)):
    try:
        # Check if the user already exists
        existing_user = db.query(models.User).filter(models.User.username == username).first()  # Query the database for existing user
        if existing_user:  # If user already exists, raise exception
            raise HTTPException(status_code=400, detail="User already exists")  # Return bad request status if user already exists

        # Hash the password
        hashed_password = pwd_context.hash(password)  # Hash the password using the hashing context

        # Create and add the new user
        new_user = models.User(username=username, password=hashed_password)  # Create a new user instance
        db.add(new_user)  # Add the new user to the database
        db.commit()  # Commit changes
        db.refresh(new_user)  # Refresh new_user to get updated values

        return new_user  # Return the created user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))