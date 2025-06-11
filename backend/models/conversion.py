from ..extensions import db
from datetime import datetime
import uuid

class ConversionTask(db.Model):
    __tablename__ = 'conversion_tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key to the original uploaded dataset
    original_dataset_id = db.Column(db.String(36), db.ForeignKey('datasets.id'), nullable=False)
    
    status = db.Column(db.String(64), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to the generated CSV datasets
    converted_datasets = db.relationship('ConvertedDataset', back_populates='task', lazy=True, cascade="all, delete-orphan")
    original_dataset = db.relationship('Dataset')

    def to_dict(self):
        return {
            'id': self.id,
            'original_dataset_id': self.original_dataset_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'converted_datasets': [d.to_dict() for d in self.converted_datasets]
        }

class ConvertedDataset(db.Model):
    __tablename__ = 'converted_datasets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False) # e.g., building name like '1栋'
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Key to the conversion task
    task_id = db.Column(db.Integer, db.ForeignKey('conversion_tasks.id'), nullable=False)
    
    # Relationship
    task = db.relationship('ConversionTask', back_populates='converted_datasets')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat()
        } 