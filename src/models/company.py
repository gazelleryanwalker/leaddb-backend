from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(255))
    website = db.Column(db.String(255))
    industry = db.Column(db.String(100))
    company_size = db.Column(db.String(50))
    location_country = db.Column(db.String(100))
    location_state = db.Column(db.String(100))
    location_city = db.Column(db.String(100))
    founded_year = db.Column(db.Integer)
    funding_status = db.Column(db.String(100))
    funding_amount = db.Column(db.Numeric(15, 2))
    technology_stack = db.Column(db.Text)
    description = db.Column(db.Text)
    linkedin_url = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with contacts
    contacts = db.relationship('Contact', backref='company', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Company {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'website': self.website,
            'industry': self.industry,
            'company_size': self.company_size,
            'location_country': self.location_country,
            'location_state': self.location_state,
            'location_city': self.location_city,
            'founded_year': self.founded_year,
            'funding_status': self.funding_status,
            'funding_amount': float(self.funding_amount) if self.funding_amount else None,
            'technology_stack': self.technology_stack,
            'description': self.description,
            'linkedin_url': self.linkedin_url,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'contact_count': len(self.contacts) if self.contacts else 0
        }

    def to_export_dict(self):
        """Simplified format for CSV/Excel export"""
        return {
            'Company Name': self.name,
            'Website': self.website,
            'Industry': self.industry,
            'Company Size': self.company_size,
            'Country': self.location_country,
            'State': self.location_state,
            'City': self.location_city,
            'Founded Year': self.founded_year,
            'Funding Status': self.funding_status,
            'LinkedIn URL': self.linkedin_url,
            'Phone': self.phone,
            'Description': self.description
        }

