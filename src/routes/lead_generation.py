from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.company import Company
from src.models.contact import Contact
from src.services.lead_generation import LeadGenerationService
from datetime import datetime

lead_gen_bp = Blueprint('lead_generation', __name__)
lead_service = LeadGenerationService()

@lead_gen_bp.route('/generate/industry', methods=['POST'])
def generate_leads_by_industry():
    """Generate leads for a specific industry"""
    try:
        data = request.get_json()
        industry = data.get('industry')
        location = data.get('location')
        limit = data.get('limit', 50)
        save_to_db = data.get('save_to_db', True)
        
        if not industry:
            return jsonify({'error': 'Industry is required'}), 400
        
        # Generate leads
        results = lead_service.generate_leads_by_industry(industry, location, limit)
        
        saved_companies = []
        saved_contacts = []
        
        if save_to_db:
            # Save companies to database
            for company_data in results['companies']:
                # Check if company already exists
                existing_company = Company.query.filter_by(name=company_data['name']).first()
                if not existing_company:
                    company = Company(
                        name=company_data['name'],
                        industry=company_data.get('industry'),
                        website=company_data.get('website'),
                        domain=company_data.get('domain'),
                        location_country=company_data.get('location_country'),
                        location_city=company_data.get('location_city'),
                        company_size=company_data.get('company_size'),
                        description=company_data.get('description'),
                        founded_year=company_data.get('founded_year'),
                        funding_status=company_data.get('funding_status'),
                        funding_amount=company_data.get('funding_amount'),
                        linkedin_url=company_data.get('linkedin_url'),
                        technology_stack=company_data.get('technology_stack')
                    )
                    db.session.add(company)
                    db.session.flush()  # Get the ID
                    saved_companies.append(company.to_dict())
                else:
                    saved_companies.append(existing_company.to_dict())
            
            # Save contacts to database
            for contact_data in results['contacts']:
                # Find the company
                company = Company.query.filter_by(name=contact_data['company_name']).first()
                if company:
                    # Check if contact already exists
                    existing_contact = Contact.query.filter_by(
                        email=contact_data.get('email'),
                        company_id=company.id
                    ).first()
                    
                    if not existing_contact:
                        contact = Contact(
                            company_id=company.id,
                            first_name=contact_data['first_name'],
                            last_name=contact_data['last_name'],
                            email=contact_data.get('email'),
                            phone=contact_data.get('phone'),
                            job_title=contact_data.get('job_title'),
                            department=contact_data.get('department'),
                            seniority_level=contact_data.get('seniority_level'),
                            linkedin_url=contact_data.get('linkedin_url'),
                            location_country=contact_data.get('location_country'),
                            location_city=contact_data.get('location_city'),
                            lead_score=contact_data.get('lead_score', 0)
                        )
                        db.session.add(contact)
                        saved_contacts.append(contact.to_dict())
            
            db.session.commit()
        
        return jsonify({
            'success': True,
            'generated': {
                'companies': len(results['companies']),
                'contacts': len(results['contacts'])
            },
            'saved': {
                'companies': len(saved_companies),
                'contacts': len(saved_contacts)
            },
            'data': {
                'companies': saved_companies if save_to_db else results['companies'],
                'contacts': saved_contacts if save_to_db else results['contacts']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lead_gen_bp.route('/enrich/company/<int:company_id>', methods=['POST'])
def enrich_company(company_id):
    """Enrich a specific company's data"""
    try:
        company = Company.query.get_or_404(company_id)
        
        # Get current company data
        company_data = company.to_dict()
        
        # Enrich the data
        enriched_data = lead_service.enrich_company_data(company_data)
        
        # Update company with enriched data
        for key, value in enriched_data.items():
            if hasattr(company, key) and value is not None:
                setattr(company, key, value)
        
        company.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'company': company.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lead_gen_bp.route('/enrich/contact/<int:contact_id>', methods=['POST'])
def enrich_contact(contact_id):
    """Enrich a specific contact's data"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        
        # Get current contact data
        contact_data = contact.to_dict()
        
        # Enrich the data
        enriched_data = lead_service.enrich_contact_data(contact_data)
        
        # Update contact with enriched data
        for key, value in enriched_data.items():
            if hasattr(contact, key) and value is not None:
                setattr(contact, key, value)
        
        contact.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'contact': contact.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lead_gen_bp.route('/enrich/bulk', methods=['POST'])
def bulk_enrich():
    """Bulk enrich multiple contacts"""
    try:
        data = request.get_json()
        contact_ids = data.get('contact_ids', [])
        
        if not contact_ids:
            return jsonify({'error': 'Contact IDs are required'}), 400
        
        enriched_count = 0
        failed_count = 0
        
        for contact_id in contact_ids:
            try:
                contact = Contact.query.get(contact_id)
                if contact:
                    # Enrich contact data
                    contact_data = contact.to_dict()
                    enriched_data = lead_service.enrich_contact_data(contact_data)
                    
                    # Update contact
                    for key, value in enriched_data.items():
                        if hasattr(contact, key) and value is not None:
                            setattr(contact, key, value)
                    
                    contact.updated_at = datetime.utcnow()
                    enriched_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                print(f"Error enriching contact {contact_id}: {e}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'enriched_count': enriched_count,
            'failed_count': failed_count,
            'total_processed': len(contact_ids)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lead_gen_bp.route('/search/companies', methods=['POST'])
def search_companies():
    """Search for companies based on criteria"""
    try:
        data = request.get_json()
        criteria = {
            'industry': data.get('industry'),
            'location': data.get('location'),
            'company_size': data.get('company_size'),
            'keywords': data.get('keywords', []),
            'funding_status': data.get('funding_status'),
            'limit': data.get('limit', 20)
        }
        
        # Remove empty criteria
        criteria = {k: v for k, v in criteria.items() if v}
        
        companies = lead_service.search_companies_by_criteria(criteria)
        
        return jsonify({
            'success': True,
            'companies': companies,
            'total': len(companies),
            'criteria': criteria
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lead_gen_bp.route('/find/contacts', methods=['POST'])
def find_company_contacts():
    """Find contacts for a specific company"""
    try:
        data = request.get_json()
        company_name = data.get('company_name')
        company_domain = data.get('company_domain')
        
        if not company_name:
            return jsonify({'error': 'Company name is required'}), 400
        
        contacts = lead_service.find_company_contacts(company_name, company_domain)
        
        return jsonify({
            'success': True,
            'contacts': contacts,
            'total': len(contacts),
            'company_name': company_name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lead_gen_bp.route('/validate/email', methods=['POST'])
def validate_email():
    """Validate email addresses"""
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        
        if not emails:
            return jsonify({'error': 'Email addresses are required'}), 400
        
        results = []
        for email in emails:
            is_valid = lead_service.validate_email(email)
            results.append({
                'email': email,
                'is_valid': is_valid
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_checked': len(emails),
            'valid_count': sum(1 for r in results if r['is_valid'])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

