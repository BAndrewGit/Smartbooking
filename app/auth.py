import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from run import app
from .models import User
from . import db
from .routes import routes_bp

auth_bp = Blueprint('auth', __name__)


@routes_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    # Verifica daca utilizatorul exista deja
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(
        name=name,
        email=email,
        password=hashed_password,
        role='user'
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201


@routes_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


s = URLSafeTimedSerializer(app.config['SECRET_KEY'])


@routes_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()
    if user:
        token = s.dumps(email, salt='password-reset-salt')
        # Trimitere email cu link-ul de resetare a parolei
        # Utilizați un serviciu de email pentru a trimite emailul
        send_email(email, token)  # Trebuie implementată funcția send_email
    return jsonify({'message': 'If your email is registered, you will receive a password reset link'}), 200


@routes_bp.route('/reset_password/<token>', methods=['POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        return jsonify({'message': 'The reset link is invalid or has expired'}), 400

    data = request.get_json()
    new_password = data.get('password')
    user = User.query.filter_by(email=email).first()

    if user and new_password:
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        return jsonify({'message': 'Password updated successfully'}), 200
    else:
        return jsonify({'message': 'User not found or invalid password'}), 400
