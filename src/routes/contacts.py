from flask import Blueprint, jsonify, request
from sqlalchemy import or_, and_, join
from src.models.user import db
from src.models.contact import Contact
from src.models.company import Company

contacts_bp = Blueprint('contacts', __name__)

@contacts_bp.route('/contacts', methods=['GET'])
def get_contacts():
    """Get contacts with optional filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Build query with joins
    query = Contact.query.join(Company, Contact.company_id == Company.id, isouter=True)
    
    # Search filters
    search = request.args.get('search')
    if search:
        query = query.filter(or_(
            Contact.first_name.ilike(f'%{search}%'),
            Contact.last_name.ilike(f'%{search}%'),
            Contact.email.ilike(f'%{search}%'),
            Contact.job_title.ilike(f'%{search}%'),
            Company.name.ilike(f'%{search}%')
        ))
    
    # Job title filter
    job_title = request.args.get('job_title')
    if job_title:
        query = query.filter(Contact.job_title.ilike(f'%{job_title}%'))
    
    # Department filter
    department = request.args.get('department')
    if department:
        query = query.filter(Contact.department.ilike(f'%{department}%'))
    
    # Seniority level filter
    seniority = request.args.get('seniority_level')
    if seniority:
        query = query.filter(Contact.seniority_level == seniority)
    
    # Location filters
    country = request.args.get('country')
    if country:
        query = query.filter(Contact.location_country.ilike(f'%{country}%'))
    
    state = request.args.get('state')
    if state:
        query = query.filter(Contact.location_state.ilike(f'%{state}%'))
    
    city = request.args.get('city')
    if city:
        query = query.filter(Contact.location_city.ilike(f'%{city}%'))
    
    # Company filters
    company_name = request.args.get('company_name')
    if company_name:
        query = query.filter(Company.name.ilike(f'%{company_name}%'))
    
    company_industry = request.args.get('company_industry')
    if company_industry:
        query = query.filter(Company.industry.ilike(f'%{company_industry}%'))
    
    company_size = request.args.get('company_size')
    if company_size:
        query = query.filter(Company.company_size == company_size)
    
    # Lead score filter
    min_score = request.args.get('min_score', type=int)
    if min_score:
        query = query.filter(Contact.lead_score >= min_score)
    
    max_score = request.args.get('max_score', type=int)
    if max_score:
        query = query.filter(Contact.lead_score <= max_score)
    
    # Email availability filter
    has_email = request.args.get('has_email')
    if has_email == 'true':
        query = query.filter(Contact.email.isnot(None), Contact.email != '')
    elif has_email == 'false':
        query = query.filter(or_(Contact.email.is_(None), Contact.email == ''))
    
    # Phone availability filter
    has_phone = request.args.get('has_phone')
    if has_phone == 'true':
        query = query.filter(Contact.phone.isnot(None), Contact.phone != '')
    elif has_phone == 'false':
        query = query.filter(or_(Contact.phone.is_(None), Contact.phone == ''))
    
    # Execute paginated query
    contacts = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'contacts': [contact.to_dict() for contact in contacts.items],
        'total': contacts.total,
        'pages': contacts.pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': contacts.has_next,
        'has_prev': contacts.has_prev
    })

@contacts_bp.route('/contacts', methods=['POST'])
def create_contact():
    """Create a new contact"""
    data = request.json
    
    contact = Contact(
        company_id=data.get('company_id'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        job_title=data.get('job_title'),
        department=data.get('department'),
        seniority_level=data.get('seniority_level'),
        linkedin_url=data.get('linkedin_url'),
        twitter_url=data.get('twitter_url'),
        location_country=data.get('location_country'),
        location_state=data.get('location_state'),
        location_city=data.get('location_city'),
        lead_score=data.get('lead_score', 0)
    )
    
    db.session.add(contact)
    db.session.commit()
    
    return jsonify(contact.to_dict()), 201

@contacts_bp.route('/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get a specific contact by ID"""
    contact = Contact.query.get_or_404(contact_id)
    return jsonify(contact.to_dict())

@contacts_bp.route('/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update a contact"""
    contact = Contact.query.get_or_404(contact_id)
    data = request.json
    
    # Update fields if provided
    for field in ['company_id', 'first_name', 'last_name', 'email', 'phone', 
                  'job_title', 'department', 'seniority_level', 'linkedin_url', 
                  'twitter_url', 'location_country', 'location_state', 
                  'location_city', 'lead_score']:
        if field in data:
            setattr(contact, field, data[field])
    
    db.session.commit()
    return jsonify(contact.to_dict())

@contacts_bp.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete a contact"""
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return '', 204

@contacts_bp.route('/contacts/search', methods=['POST'])
def advanced_contact_search():
    """Advanced contact search with complex filters"""
    data = request.json
    filters = data.get('filters', {})
    page = data.get('page', 1)
    per_page = data.get('per_page', 20)
    
    query = Contact.query.join(Company, Contact.company_id == Company.id, isouter=True)
    
    # Apply filters from the request
    if 'job_titles' in filters and filters['job_titles']:
        title_conditions = []
        for title in filters['job_titles']:
            title_conditions.append(Contact.job_title.ilike(f'%{title}%'))
        query = query.filter(or_(*title_conditions))
    
    if 'departments' in filters and filters['departments']:
        query = query.filter(Contact.department.in_(filters['departments']))
    
    if 'seniority_levels' in filters and filters['seniority_levels']:
        query = query.filter(Contact.seniority_level.in_(filters['seniority_levels']))
    
    if 'countries' in filters and filters['countries']:
        query = query.filter(Contact.location_country.in_(filters['countries']))
    
    if 'company_industries' in filters and filters['company_industries']:
        query = query.filter(Company.industry.in_(filters['company_industries']))
    
    if 'company_sizes' in filters and filters['company_sizes']:
        query = query.filter(Company.company_size.in_(filters['company_sizes']))
    
    if 'lead_score_range' in filters:
        score_range = filters['lead_score_range']
        if 'min' in score_range:
            query = query.filter(Contact.lead_score >= score_range['min'])
        if 'max' in score_range:
            query = query.filter(Contact.lead_score <= score_range['max'])
    
    if 'has_email' in filters:
        if filters['has_email']:
            query = query.filter(Contact.email.isnot(None), Contact.email != '')
        else:
            query = query.filter(or_(Contact.email.is_(None), Contact.email == ''))
    
    if 'has_phone' in filters:
        if filters['has_phone']:
            query = query.filter(Contact.phone.isnot(None), Contact.phone != '')
        else:
            query = query.filter(or_(Contact.phone.is_(None), Contact.phone == ''))
    
    # Execute paginated query
    contacts = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'contacts': [contact.to_dict() for contact in contacts.items],
        'total': contacts.total,
        'pages': contacts.pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': contacts.has_next,
        'has_prev': contacts.has_prev,
        'filters_applied': filters
    })

@contacts_bp.route('/contacts/bulk', methods=['POST'])
def bulk_create_contacts():
    """Bulk create contacts"""
    data = request.json
    contacts_data = data.get('contacts', [])
    
    contacts = []
    for contact_data in contacts_data:
        contact = Contact(**contact_data)
        contacts.append(contact)
    
    db.session.add_all(contacts)
    db.session.commit()
    
    return jsonify({
        'message': f'Successfully created {len(contacts)} contacts',
        'contacts': [contact.to_dict() for contact in contacts]
    }), 201

@contacts_bp.route('/contacts/stats', methods=['GET'])
def get_contact_stats():
    """Get contact database statistics"""
    total_contacts = Contact.query.count()
    contacts_with_email = Contact.query.filter(Contact.email.isnot(None), Contact.email != '').count()
    contacts_with_phone = Contact.query.filter(Contact.phone.isnot(None), Contact.phone != '').count()
    
    # Top industries
    industry_stats = db.session.query(
        Company.industry, 
        db.func.count(Contact.id).label('contact_count')
    ).join(Contact).group_by(Company.industry).order_by(db.func.count(Contact.id).desc()).limit(10).all()
    
    # Top job titles
    title_stats = db.session.query(
        Contact.job_title, 
        db.func.count(Contact.id).label('count')
    ).group_by(Contact.job_title).order_by(db.func.count(Contact.id).desc()).limit(10).all()
    
    return jsonify({
        'total_contacts': total_contacts,
        'contacts_with_email': contacts_with_email,
        'contacts_with_phone': contacts_with_phone,
        'email_coverage': round((contacts_with_email / total_contacts * 100), 2) if total_contacts > 0 else 0,
        'phone_coverage': round((contacts_with_phone / total_contacts * 100), 2) if total_contacts > 0 else 0,
        'top_industries': [{'industry': stat[0], 'count': stat[1]} for stat in industry_stats],
        'top_job_titles': [{'title': stat[0], 'count': stat[1]} for stat in title_stats]
    })

