 from database import db
 from sqlalchemy.dialects.postgresql import JSONB
 from datetime import datetime

 class ImportRecord(db.Model):
     __tablename__ = 'import_records'

     id = db.Column(db.String, primary_key=True)
     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
     summary = db.Column(JSONB)

     # Relationship
     cards = db.relationship('Card', back_populates='import_record')

     def __repr__(self):
         return f'<ImportRecord {self.id}: {self.timestamp}>'