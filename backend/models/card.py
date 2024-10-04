from database import db
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from sqlalchemy import event, Index
from sqlalchemy.orm import Session
from sqlalchemy import func

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
    released_at = db.Column(db.DateTime, index=True)
    uri = db.Column(db.Text)
    scryfall_uri = db.Column(db.Text)
    layout = db.Column(db.Text)
    highres_image = db.Column(db.Boolean)
    image_status = db.Column(db.Text)
    image_uris = db.Column(JSONB)
    mana_cost = db.Column(db.Text)
    cmc = db.Column(db.Float, index=True)
    type_line = db.Column(db.Text, index=True)
    oracle_text = db.Column(db.Text)
    colors = db.Column(JSONB)
    color_identity = db.Column(JSONB)
    keywords = db.Column(JSONB)
    produced_mana = db.Column(JSONB)
    legalities = db.Column(JSONB)
    games = db.Column(JSONB)
    reserved = db.Column(db.Boolean, index=True)
    foil = db.Column(db.Boolean)
    nonfoil = db.Column(db.Boolean)
    finishes = db.Column(JSONB)
    oversized = db.Column(db.Boolean)
    promo = db.Column(db.Boolean, index=True)
    full_art = db.Column(db.Boolean)
    textless = db.Column(db.Boolean)
    booster = db.Column(db.Boolean)
    story_spotlight = db.Column(db.Boolean)
    reprint = db.Column(db.Boolean, index=True)
    variation = db.Column(db.Boolean)
    set_code = db.Column(db.Text, db.ForeignKey('sets.code'), index=True)
    set_name = db.Column(db.Text)
    collector_number = db.Column(db.Text, nullable=False)
    digital = db.Column(db.Boolean)
    rarity = db.Column(db.Text, index=True)
    card_back_id = db.Column(db.Text)
    artist = db.Column(db.Text, index=True)
    artist_ids = db.Column(JSONB)
    illustration_id = db.Column(db.Text)
    border_color = db.Column(db.Text)
    frame = db.Column(db.Text)
    frame_effects = db.Column(JSONB)
    prices = db.Column(JSONB)
    related_uris = db.Column(JSONB)
    purchase_uris = db.Column(JSONB)
    promo_types = db.Column(JSONB)
    usd_price = db.Column(db.Numeric)
    usd_foil_price = db.Column(db.Numeric)
    quantity_regular = db.Column(db.BigInteger, default=0)
    quantity_foil = db.Column(db.BigInteger, default=0)
    quantity_kiosk_regular = db.Column(db.BigInteger, default=0)
    quantity_kiosk_foil = db.Column(db.BigInteger, default=0)

    # Relationships
    set = db.relationship('Set', back_populates='cards')

    # Additional indexes
    __table_args__ = (
        Index('idx_card_collection_quantities', 'quantity_regular', 'quantity_foil'),
        Index('idx_card_kiosk_quantities', 'quantity_kiosk_regular', 'quantity_kiosk_foil'),
    )

    def to_dict(self, quantity_type='collection'):
        """Serialize the card object to a dictionary."""
        data = {
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
            'frame_effects': self.frame_effects,
            'promo_types': self.promo_types,
            'promo': self.promo,
            'reprint': self.reprint,
            'variation': self.variation,
            'oversized': self.oversized,
            'keywords': self.keywords,
            'full_art': self.full_art,
            'textless': self.textless,
            'booster': self.booster,
            'story_spotlight': self.story_spotlight,
        }
        if quantity_type == 'collection':
            data['quantity_regular'] = self.quantity_regular
            data['quantity_foil'] = self.quantity_foil
        elif quantity_type == 'kiosk':
            data['quantity_regular'] = self.quantity_kiosk_regular
            data['quantity_foil'] = self.quantity_kiosk_foil
        else:
            data['quantity_regular'] = 0
            data['quantity_foil'] = 0
        return data

@event.listens_for(Session, 'after_flush')
def after_flush(session, flush_context):
    updated_set_codes = set()
    for instance in session.new.union(session.dirty).union(session.deleted):
        if isinstance(instance, Card):
            updated_set_codes.add(instance.set_code)

    if updated_set_codes:
        # Import SetCollectionCount here to avoid circular import
        from models.set_collection_count import SetCollectionCount
        SetCollectionCount.refresh()
