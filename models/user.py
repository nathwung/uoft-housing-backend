from models import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    program = db.Column(db.String(100))
    year = db.Column(db.String(10))
    verified = db.Column(db.Boolean, default=False)
