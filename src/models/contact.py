from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    job_title = db.Column(db.String(255))
    department = db.Column(db.String(100))
    seniority_level = db.Column(db.String(50))
    linkedin_url = db.Column(db.String(255))
    twitter_url = db.Column(db.String(255))
    location_country = db.Column(db.String(100))
    location_state = db.Column(db.String(100))
    location_city = db.Column(db.String(100))
    lead_score = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Contact {self.first_name} {self.last_name}>'

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def calculate_lead_score(self):
        """Calculate lead score based on contact attributes"""
        score = 0
        
        # Job title scoring
        if self.job_title:
            title = self.job_title.lower()
            if 'ceo' in title or 'founder' in title or 'president' in title:
                score += 30
            elif 'cto' in title or 'cfo' in title or 'cmo' in title:
                score += 25
            elif 'director' in title or 'vp' in title or 'vice president' in title:
                score += 20
            elif 'manager' in title or 'head' in title:
                score += 15
            elif 'lead' in title or 'senior' in title:
                score += 10
        
        # Department scoring
        if self.department:
            dept = self.department.lower()
            if 'executive' in dept or 'c-suite' in dept:
                score += 20
            elif 'marketing' in dept or 'sales' in dept:
                score += 15
            elif 'engineering' in dept or 'product' in dept:
                score += 10
        
        # Seniority level scoring
        if self.seniority_level:
            seniority = self.seniority_level.lower()
            if 'executive' in seniority or 'c-level' in seniority:
                score += 25
            elif 'senior' in seniority or 'director' in seniority:
                score += 15
            elif 'manager' in seniority:
                score += 10
        
        # Contact info completeness
        if self.email:
            score += 10
        if self.phone:
            score += 5
        if self.linkedin_url:
            score += 5
        
        # Ensure score is between 0 and 100
        return min(100, max(0, score))

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'job_title': self.job_title,
            'department': self.department,
            'seniority_level': self.seniority_level,
            'linkedin_url': self.linkedin_url,
            'twitter_url': self.twitter_url,
            'location_country': self.location_country,
            'location_state': self.location_state,
            'location_city': self.location_city,
            'lead_score': self.lead_score,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'company': self.company.to_dict() if self.company else None
        }

    def to_export_dict(self):
        """Simplified format for CSV/Excel export compatible with Zoho CRM"""
        company_name = self.company.name if self.company else ''
        company_website = self.company.website if self.company else ''
        company_industry = self.company.industry if self.company else ''
        company_size = self.company.company_size if self.company else ''
        
        return {
            'First Name': self.first_name,
            'Last Name': self.last_name,
            'Email': self.email,
            'Phone': self.phone,
            'Job Title': self.job_title,
            'Department': self.department,
            'Seniority Level': self.seniority_level,
            'Company Name': company_name,
            'Company Website': company_website,
            'Company Industry': company_industry,
            'Company Size': company_size,
            'Country': self.location_country,
            'State': self.location_state,
            'City': self.location_city,
            'LinkedIn URL': self.linkedin_url,
            'Twitter URL': self.twitter_url,
            'Lead Score': self.lead_score
        }

