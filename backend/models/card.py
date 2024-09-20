from database import db
from sqlalchemy.dialects.postgresql import JSONB

class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Text, primary_key=True)
    oracle_id = db.Column(db.Text, index=True)
    multiverse_ids = db.Column(JSONB)
    mtgo_id = db.Column(db.BigInteger)
    arena_id = db.Column(db.BigInteger)
    tcgplayer_id = db.Column(db.BigInteger)
    name = db.Column(db.Text, nullable=False, index=True)
    lang = db.Column(db.Text)
    released_at = db.Column(db.Text)
    uri = db.Column(db.Text)
    scryfall_uri = db.Column(db.Text)
    layout = db.Column(db.Text)
    highres_image = db.Column(db.Boolean)
    image_status = db.Column(db.Text)
    image_uris = db.Column(JSONB)
    mana_cost = db.Column(db.Text)
    cmc = db.Column(db.Float)
    type_line = db.Column(db.Text, index=True)
    oracle_text = db.Column(db.Text)
    colors = db.Column(JSONB)
    color_identity = db.Column(JSONB)
    keywords = db.Column(JSONB)
    produced_mana = db.Column(JSONB)
    legalities = db.Column(JSONB)
    games = db.Column(JSONB)
    reserved = db.Column(db.Boolean)
    foil = db.Column(db.Boolean)
    nonfoil = db.Column(db.Boolean)
    finishes = db.Column(JSONB)
    oversized = db.Column(db.Boolean)
    promo = db.Column(db.Boolean)
    reprint = db.Column(db.Boolean)
    variation = db.Column(db.Boolean)
    set_code = db.Column(db.Text, db.ForeignKey('sets.code'), index=True)
    set_name = db.Column(db.Text)
    collector_number = db.Column(db.Text)
    digital = db.Column(db.Boolean)
    rarity = db.Column(db.Text, index=True)
    card_back_id = db.Column(db.Text)
    artist = db.Column(db.Text)
    artist_ids = db.Column(JSONB)
    illustration_id = db.Column(db.Text)
    border_color = db.Column(db.Text)
    frame = db.Column(db.Text)
    full_art = db.Column(db.Boolean)
    textless = db.Column(db.Boolean)
    booster = db.Column(db.Boolean)
    story_spotlight = db.Column(db.Boolean)
    prices = db.Column(JSONB)
    related_uris = db.Column(JSONB)
    purchase_uris = db.Column(JSONB)

    # Relationships
    set = db.relationship('Set', back_populates='cards')
    collection = db.relationship('Collection', back_populates='card', uselist=False, cascade='all, delete-orphan')
    kiosk = db.relationship('Kiosk', back_populates='card', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'set_name': self.set_name,
            'set_code': self.set_code,
            'collector_number': self.collector_number,
            'type_line': self.type_line,
            'rarity': self.rarity,
            'mana_cost': self.mana_cost,
            'cmc': self.cmc,
            'oracle_text': self.oracle_text,
            'colors': self.colors,
            'image_uris': self.image_uris,
            'prices': self.prices,
            'collection': self.collection.to_dict() if self.collection else None,
            'kiosk': self.kiosk.to_dict() if self.kiosk else None
        }