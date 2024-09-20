from database import db

class Kiosk(db.Model):
    __tablename__ = 'kiosk'

    id = db.Column(db.BigInteger, primary_key=True)
    card_id = db.Column(db.Text, db.ForeignKey('cards.id'), nullable=False)
    quantity_regular = db.Column(db.BigInteger, default=0)
    quantity_foil = db.Column(db.BigInteger, default=0)

    # Relationship
    card = db.relationship('Card', back_populates='kiosk')

    def to_dict(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'quantity_regular': self.quantity_regular,
            'quantity_foil': self.quantity_foil
        }