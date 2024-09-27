from database import db
from models.card import Card
from models.set_collection_count import SetCollectionCount
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload
from datetime import datetime

class Set(db.Model):
    __tablename__ = 'sets'

    id = db.Column(db.Text, primary_key=True)
    code = db.Column(db.Text, unique=True, nullable=False, index=True)
    name = db.Column(db.Text, nullable=False)
    released_at = db.Column(db.DateTime)
    set_type = db.Column(db.Text)
    card_count = db.Column(db.BigInteger)
    digital = db.Column(db.Boolean)
    foil_only = db.Column(db.Boolean)
    icon_svg_uri = db.Column(db.Text)

    # Relationships
    cards = db.relationship('Card', back_populates='set')
    collection_count = db.relationship('SetCollectionCount', uselist=False, back_populates='set', lazy='joined')

    def to_dict(self):
        # Ensure collection_count is already loaded
        if self.collection_count is None:
            db.session.refresh(self)
        
        collection_count = self.collection_count.collection_count if self.collection_count else 0
        collection_percentage = (collection_count / self.card_count) * 100 if self.card_count else 0
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'released_at': self.released_at.isoformat() if self.released_at else None,
            'set_type': self.set_type,
            'card_count': self.card_count,
            'digital': self.digital,
            'foil_only': self.foil_only,
            'icon_svg_uri': self.icon_svg_uri,
            'collection_count': collection_count,
            'collection_percentage': collection_percentage
        }
