# Archive Management System (AMS)

The Archive Management System is a Django based web application designed to manage academic archive records such as exams, internship reports, and graduation projects. The system allows authorized users to store, search, borrow, and return archived records while maintaining detailed activity logs and enforcing role-based access control.


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.


## Prerequisites

The following software is required to run the system:

- Python 3.8 or higher

- pip (Python package manager)

- Virtual Studio Code (IDE recommended)

Example

Check your installation:

python --version
Pip --version


## Installing (Windows)

A step-by-step series of instructions to set up the development environment.

### Step 1: Extract the project (e.g, Desktop)

cd Desktop/AMS

### Step 2: Create a virtual environment

python -m venv venv

### Step 3: Activate the virtual environment

venv\Scripts\activate

### Step 4: Install dependencies

Install Django manually:

pip install django

### Step 5: Apply database migrations

python manage.py migrate

### Step 6: Create a superuser (Admin)

python manage.py createsuperuser

### Step 7: Run the development server

python manage.py runserver

### Step 8: Open the application in your browser:

http://127.0.0.1:8000

Example usage

- Log in as an Admin

- Add archive records and physical locations

- Borrow a record as a Lecturer

- Return the record and view activity logs


## Running the Tests

The system is currently tested using manual and functional testing.

### End-to-End Tests

End-to-end tests verify complete user workflows across the system.

These tests ensure:

- Authentication and logout work correctly

- Role-based permissions are enforced

- Records can be added, borrowed, and returned

- Activity logs are recorded accurately


Example

- Log in as Admin

- Add a new archive record

- Borrow the record

- Return the record

- Confirm status updates and log entries


### Coding Style Tests

Coding style checks ensure code clarity and maintainability.

These checks verify:

- Proper separation of models, views, and templates

- Consistent naming conventions

- Use of Django best practices

Example

- Models are defined in models.py

- Business logic is handled in views.py


## Built With

- Django – Web framework

- SQLite – Development database

- Python – Backend language

- HTML / CSS / JavaScript  – Frontend


## Project structure

‘manage.py’ - Django entry point

‘ams/’ - Django project settings

‘archive/’ - core app (tempates, models, views)

‘Db.sqlite3’ = local database (development)


## Authors

- Lama Abbadi 

- Emman Obadi

- Saffet Ozmenek

Girne American University



