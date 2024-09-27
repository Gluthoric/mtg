from database import db

class SetCollectionCount(db.Model):
    __tablename__ = 'set_collection_counts'

    set_code = db.Column(db.Text, primary_key=True)
    collection_count = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<SetCollectionCount {self.set_code}: {self.collection_count}>'
