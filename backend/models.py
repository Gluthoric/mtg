from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Double, ForeignKeyConstraint, Index, Numeric, PrimaryKeyConstraint, Table, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

Base = declarative_base()
metadata = Base.metadata


t_set_collection_counts = Table(
    'set_collection_counts', metadata,
    Column('set_code', Text),
    Column('collection_count', Numeric)
)


class Sets(Base):
    __tablename__ = 'sets'
    __table_args__ = (
        PrimaryKeyConstraint('code', name='sets_pkey'),
        UniqueConstraint('id', name='sets_id_key')
    )

    id = mapped_column(Text, nullable=False)
    code = mapped_column(Text)
    name = mapped_column(Text, nullable=False)
    released_at = mapped_column(DateTime)
    set_type = mapped_column(Text)
    card_count = mapped_column(BigInteger)
    digital = mapped_column(Boolean)
    foil_only = mapped_column(Boolean)
    icon_svg_uri = mapped_column(Text)

    cards: Mapped[List['Cards']] = relationship('Cards', uselist=True, back_populates='sets')


t_total_collection_value = Table(
    'total_collection_value', metadata,
    Column('total_value', Double(53))
)


t_unique_cards_count = Table(
    'unique_cards_count', metadata,
    Column('unique_cards', BigInteger)
)


class Cards(Base):
    __tablename__ = 'cards'
    __table_args__ = (
        ForeignKeyConstraint(['set_code'], ['sets.code'], name='cards_set_code_fkey'),
        PrimaryKeyConstraint('id', name='cards_pkey'),
        Index('idx_cards_frame_effects', 'frame_effects'),
        Index('idx_cards_kiosk_inventory', 'quantity_kiosk_regular', 'quantity_kiosk_foil'),
        Index('idx_cards_promo_types', 'promo_types'),
        Index('idx_cards_set_code', 'set_code'),
        Index('ix_cards_name', 'name'),
        Index('ix_cards_oracle_id', 'oracle_id'),
        Index('ix_cards_type_line', 'type_line')
    )

    id = mapped_column(Text)
    name = mapped_column(Text, nullable=False)
    collector_number = mapped_column(Text, nullable=False)
    oracle_id = mapped_column(Text)
    multiverse_ids = mapped_column(JSONB)
    mtgo_id = mapped_column(BigInteger)
    arena_id = mapped_column(BigInteger)
    tcgplayer_id = mapped_column(BigInteger)
    lang = mapped_column(Text)
    released_at = mapped_column(DateTime)
    uri = mapped_column(Text)
    scryfall_uri = mapped_column(Text)
    layout = mapped_column(Text)
    highres_image = mapped_column(Boolean)
    image_status = mapped_column(Text)
    image_uris = mapped_column(JSONB)
    mana_cost = mapped_column(Text)
    cmc = mapped_column(Double(53))
    type_line = mapped_column(Text)
    oracle_text = mapped_column(Text)
    colors = mapped_column(JSONB)
    color_identity = mapped_column(JSONB)
    keywords = mapped_column(JSONB)
    produced_mana = mapped_column(JSONB)
    legalities = mapped_column(JSONB)
    games = mapped_column(JSONB)
    reserved = mapped_column(Boolean)
    foil = mapped_column(Boolean)
    nonfoil = mapped_column(Boolean)
    finishes = mapped_column(JSONB)
    oversized = mapped_column(Boolean)
    promo = mapped_column(Boolean)
    reprint = mapped_column(Boolean)
    variation = mapped_column(Boolean)
    set_code = mapped_column(Text)
    set_name = mapped_column(Text)
    digital = mapped_column(Boolean)
    rarity = mapped_column(Text)
    card_back_id = mapped_column(Text)
    artist = mapped_column(Text)
    artist_ids = mapped_column(JSONB)
    illustration_id = mapped_column(Text)
    border_color = mapped_column(Text)
    frame = mapped_column(Text)
    full_art = mapped_column(Boolean)
    textless = mapped_column(Boolean)
    booster = mapped_column(Boolean)
    story_spotlight = mapped_column(Boolean)
    prices = mapped_column(JSONB)
    related_uris = mapped_column(JSONB)
    purchase_uris = mapped_column(JSONB)
    usd_price = mapped_column(Numeric)
    usd_foil_price = mapped_column(Numeric)
    quantity_kiosk_regular = mapped_column(BigInteger, server_default=text('0'))
    quantity_kiosk_foil = mapped_column(BigInteger, server_default=text('0'))
    frame_effects = mapped_column(JSONB)
    promo_types = mapped_column(JSONB)
    quantity_regular = mapped_column(BigInteger)
    quantity_foil = mapped_column(BigInteger)

    sets: Mapped[Optional['Sets']] = relationship('Sets', back_populates='cards')
