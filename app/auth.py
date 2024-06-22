import os
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_refresh_token
import bcrypt
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from itsdangerous import URLSafeTimedSerializer
from .models import User, RevokedToken
from . import db
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

auth_bp = Blueprint('auth', __name__)

load_dotenv(dotenv_path='Keys.env')


# Register user
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_user = User(
        name=name,
        email=email,
        password=hashed_password,
        role='user'
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201


# Login user
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        additional_claims = {"role": user.role}
        access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


# Forgot password
def send_email(to_email, token):
    from_email = os.getenv('EMAIL_COMPANY')
    from_password = os.getenv('EMAIL_PASS')

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = 'Reset Your Password'

    reset_url = f'http://127.0.0.1:5000/reset_password/{token}'
    body = f'Click the following link to reset your password: {reset_url}'
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print('Email sent successfully')
    except Exception as e:
        print(f'Failed to send email: {e}')


@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()
    if user:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = s.dumps(email, salt='password-reset-salt')
        send_email(email, token)
    return jsonify({'message': 'If your email is registered, you will receive a password reset link'}), 200


@auth_bp.route('/reset_password/<token>', methods=['POST'])
def reset_password(token):
    try:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception:
        return jsonify({'message': 'The reset link is invalid or has expired'}), 400

    data = request.get_json()
    new_password = data.get('password')
    user = User.query.filter_by(email=email).first()

    if user and new_password:
        user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.session.commit()
        return jsonify({'message': 'Password updated successfully'}), 200
    else:
        return jsonify({'message': 'User not found or invalid password'}), 400


# Refresh route
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({'access_token': new_access_token}), 200


# Logout route
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    revoked_token = RevokedToken(jti=jti)
    revoked_token.save_to_db()
    return jsonify({"msg": "Successfully logged out"}), 200

