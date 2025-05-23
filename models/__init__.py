from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models here to register them
from .listing import Listing
from .message import Message
