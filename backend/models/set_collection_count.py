from database import db
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class SetCollectionCount(db.Model):
    __tablename__ = 'set_collection_counts'
    __table_args__ = {'info': dict(is_view=True)}

    set_code = db.Column(db.Text, ForeignKey('sets.code'), primary_key=True)
    collection_count = db.Column(db.Integer, nullable=False)

    # Define relationship with explicit foreign key handling
    set = relationship('Set', back_populates='set_collection_count')

    def __repr__(self):
        return f'<SetCollectionCount {self.set_code}: {self.collection_count}>'

    @classmethod
    def refresh(cls):
        db.session.execute(text('REFRESH MATERIALIZED VIEW set_collection_counts'))
        db.session.commit()
