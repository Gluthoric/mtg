from database import db
from models.card import Card
from models.set_collection_count import SetCollectionCount
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class Set(db.Model):
    __tablename__ = 'sets'

    code = db.Column(db.Text, primary_key=True)
    id = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    released_at = db.Column(db.DateTime)
    set_type = db.Column(db.Text)
    card_count = db.Column(db.BigInteger)
    digital = db.Column(db.Boolean)
    foil_only = db.Column(db.Boolean)
    icon_svg_uri = db.Column(db.Text)

    # Relationships
    cards = relationship('Card', back_populates='set')
    
    # Updated relationship with explicit foreign key handling
    set_collection_count = relationship('SetCollectionCount', back_populates='set', uselist=False, 
                                        primaryjoin="Set.code == foreign(SetCollectionCount.set_code)")

    def to_dict(self):
        # Use set_collection_count here to avoid confusion with 'collection_count'
        collection_count = self.get_collection_count()
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
            'collection_percentage': (collection_count / self.card_count) * 100 if self.card_count and collection_count > 0 else 0
        }

    def get_collection_count(self):
        # Use set_collection_count instead of collection_count
        if self.set_collection_count:
            return self.set_collection_count.collection_count
        return 0

    @classmethod
    def get_sets_with_collection_counts(cls):
        # Renaming for clarity and ensuring correct join usage
        return db.session.query(cls, SetCollectionCount.collection_count) \
            .outerjoin(SetCollectionCount, cls.code == SetCollectionCount.set_code) \
            .order_by(cls.released_at.desc()) \
            .all()

    @classmethod
    def update_collection_counts(cls):
        try:
            SetCollectionCount.refresh()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error refreshing materialized view: {e}")
            raise e  # or handle accordingly
