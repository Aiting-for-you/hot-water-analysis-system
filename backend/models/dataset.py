from ..extensions import db
import uuid
from datetime import datetime

class Dataset(db.Model):
    __tablename__ = 'datasets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False) # Should store the unique filename, e.g., UUID.csv
    file_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='datasets')
    # tasks = db.relationship('AnalysisTask', back_populates='dataset', lazy=True, cascade="all, delete-orphan") # No longer needed
    conversion_tasks = db.relationship('ConversionTask', back_populates='original_dataset', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        } 