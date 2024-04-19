*Technologies used:-
	Framework - FastAPI
	Database - MySQL
	Authentication - JWT
	Algorithm for Encoding and Decoding Password - HS256


Download Zip file of my Repo then follow these steps

*Steps to Test TodoApp API

step 1 - create database/schema in MySQL (Database Name - "todoapp")
step 2 - open "database.py"
step 3 - in SQL_DB_URL change "root" with you MySQL username and "1234" with your MySQL Password
step 4 - open "Wobot Assign Submit"
step 5 - right click and open terminal
step 6 - type "cd env/Scripts"
step 7 - press enter
step 8 - type "activate" and press enter (activates virtual environment)
step 9 - type "cd.." and press enter, again type "cd.." and press enter
step 10 - type "pip install -r requirements.txt" and press enter (installs all required dependencies)
step 11 - type "uvicorn main:app --reload" and press enter (start the fastapi)
step 12 - open browser and type "http://127.0.0.1:8000/docs"
step 13 - now test my API

*Features:-
	CRUD operations on Todo Lists
	User Authentication on every Todo
	view all todos of specific user
