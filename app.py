from flask import Flask, jsonify, request
from flask_cors import CORS
from routes.auth import auth_bp
import jwt
from functools import wraps
import os
from routes.listings import listings_bp
from models import db
from routes.messages import messages_bp
from models.favorite import Favorite
from routes.favorites import favorites_bp
from dotenv import load_dotenv
from models.user import User

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://localhost:3002"]}})

# Use a secure secret key (load from .env in real app)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'your-secret-key')

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api')

app.register_blueprint(listings_bp)

# PostgreSQL DB config
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:nath1234@localhost:5432/uoft_housing'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(messages_bp)
app.register_blueprint(favorites_bp)

# JWT token-required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

# Example protected route
@app.route('/api/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({'message': 'You are authorized to see this!'})

# Do not include app.run() when deploying with gunicorn on Render
