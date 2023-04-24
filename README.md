# python-task-2

 
# User Management App

This is a Flask/MongoDB user management app that allows you to create, update, and manage users and organizations. The app has the following endpoints:

## Endpoints

- POST /users: creates a new user with an ID, name, and email address.
- GET /users: retrieves a list of all users in the system, with the option to filter by name and paginate the results.
- GET /users/<user_id>: retrieves a single user by ID.
- POST /organizations: creates a new organization with a unique name.
- POST /permissions: creates or updates permissions for a user on one or more organizations.
- DELETE /organisations/<org_id>/users/<user_id> : Deletes user permissions from the given organisations


## Setup

To set up the app, you will need to have Python 3.x and MongoDB installed on your system. Once you have these dependencies installed, you can follow these steps:

- Clone the repository to your local machine.
- Install the required Python packages by running pip install -r requirements.txt in the project root directory.
- Start the MongoDB server by running mongod in a separate terminal window.
- Start the Flask app by running python main.py in the project root directory.

