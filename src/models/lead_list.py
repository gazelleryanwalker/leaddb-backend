from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class LeadList(db.Model):
    __tablename__ = 'lead_lists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Many-to-many relationship with contacts
    contacts = db.relationship('Contact', secondary='lead_list_contacts', backref='lead_lists', lazy='dynamic')

    def __repr__(self):
        return f'<LeadList {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'contact_count': self.contacts.count()
        }

class LeadListContact(db.Model):
    __tablename__ = 'lead_list_contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('lead_lists.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate entries
    __table_args__ = (db.UniqueConstraint('list_id', 'contact_id', name='unique_list_contact'),)

    def __repr__(self):
        return f'<LeadListContact list_id={self.list_id} contact_id={self.contact_id}>'

class SavedSearch(db.Model):
    __tablename__ = 'saved_searches'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    filters = db.Column(db.JSON)
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SavedSearch {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'filters': self.filters,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

