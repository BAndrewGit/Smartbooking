import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from itsdangerous import URLSafeTimedSerializer
from run import app
from .models import User
from . import db
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

auth_bp = Blueprint('auth', __name__)


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
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


s = URLSafeTimedSerializer(app.config['SECRET_KEY'])


# Forgot password
def send_email(to_email, token):
    from_email = 'your_email@gmail.com'
    from_password = 'your_password'

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = 'Reset Your Password'

    reset_url = f'http://yourdomain.com/reset_password/{token}'
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
        token = s.dumps(email, salt='password-reset-salt')
        # Send email with reset link
        # Use an email service to send the email
        send_email(email, token)  
    return jsonify({'message': 'If your email is registered, you will receive a password reset link'}), 200


# Reset password
@auth_bp.route('/reset_password/<token>', methods=['POST'])
def reset_password(token):
    try:
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
