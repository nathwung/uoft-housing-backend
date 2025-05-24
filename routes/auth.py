from flask import Blueprint, request, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from routes.listings import update_poster_info_internal
from flask_cors import cross_origin
from routes.messages import update_sender_name_internal
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from models.user import User
from models import db

auth_bp = Blueprint('auth', __name__)

def generate_confirmation_token(email):
    s = URLSafeTimedSerializer(os.getenv('JWT_SECRET', 'your-secret-key'))
    return s.dumps(email, salt='email-confirm')

def send_verification_email(to_email, user_name, confirm_url):
    message = Mail(
        from_email='uofthousing@outlook.com',
        to_emails=to_email,
        subject='Confirm Your UofT Housing Account',
        html_content=f"""
        <p>Hi {user_name},</p>
        <p>Thanks for registering for UofT Housing! Please confirm your email address by clicking the link below:</p>
        <a href="{confirm_url}">Confirm Email</a>
        <p>This link will expire in 1 hour.</p>
        """,
    )
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        print("STATUS:", response.status_code)
        print("BODY:", response.body)
        print("HEADERS:", response.headers)
    except Exception as e:
        print(f"Error sending verification email: {e}")

@auth_bp.route('/verify')
def verify_email():
    token = request.args.get('token')
    s = URLSafeTimedSerializer(os.getenv('JWT_SECRET', 'your-secret-key'))

    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return "Verification link expired", 400
    except BadSignature:
        return "Invalid or tampered token", 400

    # Query user from the DB
    user = User.query.filter_by(email=email).first()
    if user:
        user.verified = True
        db.session.commit()

        # Auto-login after verification
        jwt_token = jwt.encode({
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, os.getenv('JWT_SECRET', 'your-secret-key'), algorithm='HS256')

        redirect_url = (
            f"https://uoft-housing.vercel.app/verified?"
            f"token={jwt_token}&"
            f"name={user.name}&"
            f"email={user.email}&"
            f"avatar=/default-avatar.png&"
            f"program={user.program}&"
            f"year={user.year}"
        )

        return redirect(redirect_url)

    return "User not found", 404

def send_confirmation_email(to_email, user_name):
    message = Mail(
        from_email='uofthousing@outlook.com',  # Must be the same email you verified in SendGrid
        to_emails=to_email,
        subject='UofT Housing: Login Confirmation',
        plain_text_content=f"Hi {user_name},\n\nYou just signed in to UofT Housing.\n\nIf this wasn’t you, please secure your account.",
    )

    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        sg.send(message)
        print(f"Confirmation email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ['name', 'email', 'password', 'program', 'year']

    if not all(field in data and data[field] for field in required_fields):
        return jsonify({'error': 'Please fill out all required fields'}), 400

    email = data['email']
    if not email.endswith('@mail.utoronto.ca'):
        return jsonify({'error': 'Email must be a @mail.utoronto.ca address'}), 400

    # Check DB if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User already exists'}), 400

    hashed_password = generate_password_hash(data['password'])

    new_user = User(
        name=data['name'],
        email=email,
        password=hashed_password,
        program=data['program'],
        year=data['year'],
        verified=False
    )

    db.session.add(new_user)
    db.session.commit()

    # Generate verification token + send email like before
    token = generate_confirmation_token(email)
    confirm_url = f"https://uoft-housing-backend.onrender.com/api/verify?token={token}"
    send_verification_email(email, data['name'], confirm_url)

    return jsonify({'message': 'Verification email sent. Please check your inbox to activate your account.'})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.verified:
        return jsonify({'error': 'Email not verified. Please check your inbox.'}), 403

    # Send login confirmation email
    send_confirmation_email(user.email, user.name)

    token = jwt.encode({
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, os.getenv('JWT_SECRET', 'your-secret-key'), algorithm='HS256')

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'name': user.name,
            'email': user.email,
            'avatar': '/default-avatar.png',
            'program': user.program,
            'year': user.year
        }
    })

@auth_bp.route('/update-profile', methods=['POST'])
@cross_origin(origins=["http://localhost:3000", "http://localhost:3002"])
def update_profile():
    data = request.get_json()
    email = data.get('email')

    # Find user by email in the database
    user = User.query.filter_by(email=email).first()
    if user:
        # Update user fields (only if new values provided)
        user.name = data.get('name', user.name)
        user.program = data.get('program', user.program)
        user.year = data.get('year', user.year)

        db.session.commit()  # Save changes to the DB

        # Update listings and messages
        update_poster_info_internal({
            'email': email,
            'name': user.name,
            'program': user.program,
            'year': user.year,
            'avatar': '/default-avatar.png'
        })

        update_sender_name_internal(
            old_name=data.get('original_name', data['name']),
            new_name=user.name
        )

        return jsonify({
            'message': 'Profile updated',
            'user': {
                'name': user.name,
                'email': user.email,
                'avatar': '/default-avatar.png',
                'program': user.program,
                'year': user.year
            }
        })

    return jsonify({'error': 'User not found'}), 404

# Forgot Password Endpoint
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'No user with that email'}), 404

    token = generate_confirmation_token(email)
    reset_link = f"http://localhost:3000/reset-password?token={token}"

    message = Mail(
        from_email='uofthousing@outlook.com',
        to_emails=email,
        subject='Reset Your UofT Housing Password',
        html_content=f"""
        <p>Hi {user.name},</p>
        <p>Click below to reset your password:</p>
        <a href="{reset_link}">Reset Password</a>
        <p>This link expires in 1 hour.</p>
        """,
    )
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        sg.send(message)
        return jsonify({'message': 'Reset link sent'})
    except Exception as e:
        print(f"Error sending reset email: {e}")
        return jsonify({'error': 'Failed to send email'}), 500


# Reset Password Endpoint
@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        s = URLSafeTimedSerializer(os.getenv('JWT_SECRET', 'your-secret-key'))
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return jsonify({'error': 'Token expired'}), 400
    except BadSignature:
        return jsonify({'error': 'Invalid token'}), 400

    data = request.get_json()
    new_password = generate_password_hash(data.get('password'))

    user = User.query.filter_by(email=email).first()
    if user:
        user.password = new_password
        db.session.commit()
        return jsonify({'message': 'Password updated'})
    return jsonify({'error': 'User not found'}), 404