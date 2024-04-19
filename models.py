# Importing necessary modules from SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# Importing the Base class from the database module
from database import Base

# Defining a User class that inherits from the Base class
class User(Base):
    # Table name in the database
    __tablename__ = "users"

    # Defining columns for the users table
    id = Column(Integer, primary_key=True, index=True)  # Unique identifier for each user
    username = Column(String(50), unique=True)  # User's username, unique constraint applied
    password = Column(String(255))  # User's password, possibly hashed for security
    todolist = relationship("TodoList", back_populates="user")  # Relationship to the TodoList table

    # Method for creating a new todo item associated with this user
    def create_todo_item(self, title: str, content: str):
        # Creating a new TodoList instance with the provided title, content, and user_id
        todo_item = TodoList(title=title, content=content, user_id=self.id)
        return todo_item

# Defining a TodoList class that inherits from the Base class
class TodoList(Base):
    # Table name in the database
    __tablename__ = "todolist"

    # Defining columns for the todolist table
    id = Column(Integer, primary_key=True, index=True)  # Unique identifier for each todo item
    title = Column(String(150))  # Title of the todo item
    content = Column(String(250))  # Content/description of the todo item
    user_id = Column(Integer, ForeignKey('users.id'))  # Foreign key relationship to the users table

    # Relationship to the User table, specifying the back reference
    user = relationship("User", back_populates="todolist")
