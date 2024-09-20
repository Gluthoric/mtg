from database import db

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
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'released_at': self.released_at,
            'set_type': self.set_type,
            'card_count': self.card_count,
            'digital': self.digital,
            'foil_only': self.foil_only,
            'icon_svg_uri': self.icon_svg_uri
        }