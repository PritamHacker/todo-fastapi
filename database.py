# Importing necessary modules from SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database connection URL, specifying the driver, username, password, host, port, and database name
SQL_DB_URL = "mysql+pymysql://root:1234@localhost:3306/todoapp"

# Creating the database engine with the specified URL
engine = create_engine(SQL_DB_URL)

# Creating a sessionmaker instance with autocommit set to False and binding it to the engine
SessionLocal = sessionmaker(autocommit=False, bind=engine)

# Creating a base class for declarative class definitions
Base = declarative_base()
