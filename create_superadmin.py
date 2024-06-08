import requests
from flask import Flask
from app import db, create_app
from app.models import User

app = create_app()
app.app_context().push()

def delete_user(email):
    user = User.query.filter_by(email=email).first()
    if user:
        db.session.delete(user)
        db.session.commit()

def register_user(name, email, password):
    registration_data = {
        'name': name,
        'email': email,
        'password': password
    }
    response = requests.post('http://localhost:5000/auth/register', json=registration_data)
    if response.status_code != 201:
        print(f"Error during registration: {response.json()}")
        return None
    return response.json()

def login_user(email, password):
    login_data = {
        'email': email,
        'password': password
    }
    response = requests.post('http://localhost:5000/auth/login', json=login_data)
    if response.status_code != 200:
        print(f"Error during login: {response.json()}")
        return None
    return response.json()['access_token']

def update_user_role(email, new_role):
    user = User.query.filter_by(email=email).first()
    if user:
        user.role = new_role
        db.session.commit()
        print(f"User role updated to {new_role}")

def create_superadmin():
    email = 'admin.andrew@gmail.com'
    password = 'supersecretpassword'
    name = 'Andrew Admin'

    # Șterge utilizatorul existent
    delete_user(email)

    # Înregistrează un nou utilizator
    register_response = register_user(name, email, password)
    if not register_response:
        return

    # Autentifică utilizatorul pentru a obține un token de acces
    access_token = login_user(email, password)
    if not access_token:
        return

    # Actualizează rolul utilizatorului la superadmin
    update_user_role(email, 'superadmin')
    print("Superadmin created and role updated successfully")

if __name__ == "__main__":
    create_superadmin()
