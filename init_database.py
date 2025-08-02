#!/usr/bin/env python3
"""
Database Initialization Script for LeadDB
Creates tables and populates with sample data
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import app
from src.models.user import db
from src.models.company import Company
from src.models.contact import Contact
from src.models.lead_list import LeadList, LeadListContact

def create_sample_data():
    """Create sample companies and contacts for demonstration"""
    
    print("🏢 Creating sample companies...")
    
    # Sample companies
    companies_data = [
        {
            "name": "TechVision AI",
            "industry": "Technology",
            "website": "https://techvision.ai",
            "domain": "techvision.ai",
            "company_size": "10-50",
            "location_country": "United States",
            "location_state": "California",
            "location_city": "San Francisco",
            "description": "AI-powered business solutions for modern enterprises",
            "founded_year": 2020,
            "funding_status": "Series A",
            "funding_amount": 5000000,
            "linkedin_url": "https://linkedin.com/company/techvision-ai"
        },
        {
            "name": "GrowthMarketing Pro",
            "industry": "Marketing",
            "website": "https://growthmarketing.pro",
            "domain": "growthmarketing.pro",
            "company_size": "50-100",
            "location_country": "United States",
            "location_state": "Texas",
            "location_city": "Austin",
            "description": "Full-service digital marketing agency",
            "founded_year": 2018,
            "funding_status": "Bootstrapped",
            "linkedin_url": "https://linkedin.com/company/growthmarketing-pro"
        },
        {
            "name": "CloudScale Solutions",
            "industry": "Technology",
            "website": "https://cloudscale.io",
            "domain": "cloudscale.io",
            "company_size": "100-500",
            "location_country": "United States",
            "location_state": "Washington",
            "location_city": "Seattle",
            "description": "Enterprise cloud infrastructure and DevOps services",
            "founded_year": 2019,
            "funding_status": "Series B",
            "funding_amount": 15000000,
            "linkedin_url": "https://linkedin.com/company/cloudscale-solutions"
        },
        {
            "name": "DataInsights Corp",
            "industry": "Analytics",
            "website": "https://datainsights.com",
            "domain": "datainsights.com",
            "company_size": "50-100",
            "location_country": "United States",
            "location_state": "New York",
            "location_city": "New York",
            "description": "Business intelligence and data analytics platform",
            "founded_year": 2017,
            "funding_status": "Series A",
            "funding_amount": 8000000,
            "linkedin_url": "https://linkedin.com/company/datainsights-corp"
        },
        {
            "name": "EcoTech Innovations",
            "industry": "Clean Technology",
            "website": "https://ecotech.green",
            "domain": "ecotech.green",
            "company_size": "10-50",
            "location_country": "United States",
            "location_state": "California",
            "location_city": "Palo Alto",
            "description": "Sustainable technology solutions for businesses",
            "founded_year": 2021,
            "funding_status": "Seed",
            "funding_amount": 2000000,
            "linkedin_url": "https://linkedin.com/company/ecotech-innovations"
        }
    ]
    
    created_companies = []
    for company_data in companies_data:
        company = Company(**company_data)
        db.session.add(company)
        created_companies.append(company)
    
    db.session.flush()  # Get IDs for companies
    print(f"✅ Created {len(created_companies)} companies")
    
    print("👥 Creating sample contacts...")
    
    # Sample contacts
    contacts_data = [
        # TechVision AI contacts
        {
            "company_id": created_companies[0].id,
            "first_name": "Alex",
            "last_name": "Chen",
            "email": "alex.chen@techvision.ai",
            "phone": "+1-555-0101",
            "job_title": "CEO",
            "department": "Executive",
            "seniority_level": "C-Level",
            "linkedin_url": "https://linkedin.com/in/alexchen",
            "location_country": "United States",
            "location_state": "California",
            "location_city": "San Francisco"
        },
        {
            "company_id": created_companies[0].id,
            "first_name": "Maria",
            "last_name": "Rodriguez",
            "email": "maria.rodriguez@techvision.ai",
            "phone": "+1-555-0102",
            "job_title": "CTO",
            "department": "Engineering",
            "seniority_level": "C-Level",
            "linkedin_url": "https://linkedin.com/in/mariarodriguez",
            "location_country": "United States",
            "location_state": "California",
            "location_city": "San Francisco"
        },
        # GrowthMarketing Pro contacts
        {
            "company_id": created_companies[1].id,
            "first_name": "David",
            "last_name": "Kim",
            "email": "david.kim@growthmarketing.pro",
            "phone": "+1-555-0201",
            "job_title": "Founder & CEO",
            "department": "Executive",
            "seniority_level": "C-Level",
            "linkedin_url": "https://linkedin.com/in/davidkim",
            "location_country": "United States",
            "location_state": "Texas",
            "location_city": "Austin"
        },
        {
            "company_id": created_companies[1].id,
            "first_name": "Sarah",
            "last_name": "Johnson",
            "email": "sarah.johnson@growthmarketing.pro",
            "phone": "+1-555-0202",
            "job_title": "VP of Marketing",
            "department": "Marketing",
            "seniority_level": "VP",
            "linkedin_url": "https://linkedin.com/in/sarahjohnson",
            "location_country": "United States",
            "location_state": "Texas",
            "location_city": "Austin"
        },
        # CloudScale Solutions contacts
        {
            "company_id": created_companies[2].id,
            "first_name": "Michael",
            "last_name": "Thompson",
            "email": "michael.thompson@cloudscale.io",
            "phone": "+1-555-0301",
            "job_title": "CEO",
            "department": "Executive",
            "seniority_level": "C-Level",
            "linkedin_url": "https://linkedin.com/in/michaelthompson",
            "location_country": "United States",
            "location_state": "Washington",
            "location_city": "Seattle"
        },
        {
            "company_id": created_companies[2].id,
            "first_name": "Jennifer",
            "last_name": "Lee",
            "email": "jennifer.lee@cloudscale.io",
            "phone": "+1-555-0302",
            "job_title": "VP of Sales",
            "department": "Sales",
            "seniority_level": "VP",
            "linkedin_url": "https://linkedin.com/in/jenniferlee",
            "location_country": "United States",
            "location_state": "Washington",
            "location_city": "Seattle"
        },
        # DataInsights Corp contacts
        {
            "company_id": created_companies[3].id,
            "first_name": "Robert",
            "last_name": "Wilson",
            "email": "robert.wilson@datainsights.com",
            "phone": "+1-555-0401",
            "job_title": "Founder",
            "department": "Executive",
            "seniority_level": "C-Level",
            "linkedin_url": "https://linkedin.com/in/robertwilson",
            "location_country": "United States",
            "location_state": "New York",
            "location_city": "New York"
        },
        {
            "company_id": created_companies[3].id,
            "first_name": "Emily",
            "last_name": "Davis",
            "email": "emily.davis@datainsights.com",
            "phone": "+1-555-0402",
            "job_title": "Head of Product",
            "department": "Product",
            "seniority_level": "Director",
            "linkedin_url": "https://linkedin.com/in/emilydavis",
            "location_country": "United States",
            "location_state": "New York",
            "location_city": "New York"
        },
        # EcoTech Innovations contacts
        {
            "company_id": created_companies[4].id,
            "first_name": "James",
            "last_name": "Green",
            "email": "james.green@ecotech.green",
            "phone": "+1-555-0501",
            "job_title": "CEO",
            "department": "Executive",
            "seniority_level": "C-Level",
            "linkedin_url": "https://linkedin.com/in/jamesgreen",
            "location_country": "United States",
            "location_state": "California",
            "location_city": "Palo Alto"
        },
        {
            "company_id": created_companies[4].id,
            "first_name": "Lisa",
            "last_name": "Brown",
            "email": "lisa.brown@ecotech.green",
            "phone": "+1-555-0502",
            "job_title": "VP of Engineering",
            "department": "Engineering",
            "seniority_level": "VP",
            "linkedin_url": "https://linkedin.com/in/lisabrown",
            "location_country": "United States",
            "location_state": "California",
            "location_city": "Palo Alto"
        }
    ]
    
    created_contacts = []
    for contact_data in contacts_data:
        contact = Contact(**contact_data)
        # Calculate lead score
        contact.lead_score = contact.calculate_lead_score()
        db.session.add(contact)
        created_contacts.append(contact)
    
    db.session.flush()  # Get IDs for contacts
    print(f"✅ Created {len(created_contacts)} contacts")
    
    print("📋 Creating sample lead lists...")
    
    # Create sample lead lists
    lead_lists_data = [
        {
            "name": "Tech CEOs Q1 2025",
            "description": "Technology company CEOs for Q1 outreach campaign"
        },
        {
            "name": "Marketing Decision Makers",
            "description": "Marketing executives and decision makers"
        },
        {
            "name": "High-Value Prospects",
            "description": "High lead score contacts for priority outreach"
        }
    ]
    
    created_lists = []
    for list_data in lead_lists_data:
        lead_list = LeadList(**list_data)
        db.session.add(lead_list)
        created_lists.append(lead_list)
    
    db.session.flush()  # Get IDs for lists
    
    # Add contacts to lists
    # Tech CEOs list - add all CEOs
    ceo_contacts = [c for c in created_contacts if 'CEO' in c.job_title]
    for contact in ceo_contacts:
        list_contact = LeadListContact(list_id=created_lists[0].id, contact_id=contact.id)
        db.session.add(list_contact)
    
    # Marketing Decision Makers - add marketing contacts
    marketing_contacts = [c for c in created_contacts if 'Marketing' in c.department or 'Marketing' in c.job_title]
    for contact in marketing_contacts:
        list_contact = LeadListContact(list_id=created_lists[1].id, contact_id=contact.id)
        db.session.add(list_contact)
    
    # High-Value Prospects - add contacts with lead score > 80
    high_value_contacts = [c for c in created_contacts if c.lead_score > 80]
    for contact in high_value_contacts:
        list_contact = LeadListContact(list_id=created_lists[2].id, contact_id=contact.id)
        db.session.add(list_contact)
    
    print(f"✅ Created {len(created_lists)} lead lists")
    
    return created_companies, created_contacts, created_lists

def main():
    """Initialize database with tables and sample data"""
    print("🚀 Initializing LeadDB Database")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Create all tables
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if data already exists
            existing_companies = Company.query.count()
            if existing_companies > 0:
                print(f"ℹ️  Database already contains {existing_companies} companies")
                print("Skipping sample data creation")
                return
            
            # Create sample data
            companies, contacts, lists = create_sample_data()
            
            # Commit all changes
            db.session.commit()
            
            print("\n🎉 Database initialization completed successfully!")
            print("\n📊 Summary:")
            print(f"   • Companies: {len(companies)}")
            print(f"   • Contacts: {len(contacts)}")
            print(f"   • Lead Lists: {len(lists)}")
            
            print("\n🔗 Next steps:")
            print("   1. Start the Flask server: python src/main.py")
            print("   2. Access the API at: http://localhost:5000")
            print("   3. Test endpoints: http://localhost:5000/api")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    main()

