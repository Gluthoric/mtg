from database import db
from models.card import Card
from sqlalchemy.sql import func  # Add this import at the top

class Set(db.Model):
    __tablename__ = 'sets'

    id = db.Column(db.Text, primary_key=True)
    code = db.Column(db.Text, unique=True, nullable=False, index=True)
    name = db.Column(db.Text, nullable=False)
    released_at = db.Column(db.Text)
    set_type = db.Column(db.Text)
    card_count = db.Column(db.BigInteger)
    digital = db.Column(db.Boolean)
    foil_only = db.Column(db.Boolean)
    icon_svg_uri = db.Column(db.Text)

    # Relationships
    cards = db.relationship('Card', back_populates='set')

    def to_dict(self):
        collection_count = self.get_collection_count()
        collection_percentage = (collection_count / self.card_count) * 100 if self.card_count else 0
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'released_at': self.released_at,
            'set_type': self.set_type,
            'card_count': self.card_count,
            'digital': self.digital,
            'foil_only': self.foil_only,
            'icon_svg_uri': self.icon_svg_uri,
            'collection_count': collection_count,
            'collection_percentage': collection_percentage
        }

    def get_collection_count(self):
        # Count the number of unique cards in the collection for this set
        return db.session.query(func.count(Card.id)) \
            .filter(Card.set_code == self.code) \
            .filter((Card.quantity_collection_regular > 0) | (Card.quantity_collection_foil > 0)) \
            .scalar() or 0