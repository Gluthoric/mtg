# Database initialization and models

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models here to avoid circular imports
from models.card import Card
from models.set import Set