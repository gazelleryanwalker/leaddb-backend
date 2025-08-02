from flask import Blueprint, jsonify, request
from sqlalchemy import or_, and_
from src.models.user import db
from src.models.company import Company

companies_bp = Blueprint('companies', __name__)

@companies_bp.route('/companies', methods=['GET'])
def get_companies():
    """Get companies with optional filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Build query with filters
    query = Company.query
    
    # Search filters
    search = request.args.get('search')
    if search:
        query = query.filter(or_(
            Company.name.ilike(f'%{search}%'),
            Company.domain.ilike(f'%{search}%'),
            Company.description.ilike(f'%{search}%')
        ))
    
    # Industry filter
    industry = request.args.get('industry')
    if industry:
        query = query.filter(Company.industry.ilike(f'%{industry}%'))
    
    # Company size filter
    company_size = request.args.get('company_size')
    if company_size:
        query = query.filter(Company.company_size == company_size)
    
    # Location filters
    country = request.args.get('country')
    if country:
        query = query.filter(Company.location_country.ilike(f'%{country}%'))
    
    state = request.args.get('state')
    if state:
        query = query.filter(Company.location_state.ilike(f'%{state}%'))
    
    city = request.args.get('city')
    if city:
        query = query.filter(Company.location_city.ilike(f'%{city}%'))
    
    # Funding status filter
    funding_status = request.args.get('funding_status')
    if funding_status:
        query = query.filter(Company.funding_status.ilike(f'%{funding_status}%'))
    
    # Founded year range
    founded_after = request.args.get('founded_after', type=int)
    if founded_after:
        query = query.filter(Company.founded_year >= founded_after)
    
    founded_before = request.args.get('founded_before', type=int)
    if founded_before:
        query = query.filter(Company.founded_year <= founded_before)
    
    # Technology stack filter
    technology = request.args.get('technology')
    if technology:
        query = query.filter(Company.technology_stack.ilike(f'%{technology}%'))
    
    # Execute paginated query
    companies = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'companies': [company.to_dict() for company in companies.items],
        'total': companies.total,
        'pages': companies.pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': companies.has_next,
        'has_prev': companies.has_prev
    })

@companies_bp.route('/companies', methods=['POST'])
def create_company():
    """Create a new company"""
    data = request.json
    
    company = Company(
        name=data.get('name'),
        domain=data.get('domain'),
        website=data.get('website'),
        industry=data.get('industry'),
        company_size=data.get('company_size'),
        location_country=data.get('location_country'),
        location_state=data.get('location_state'),
        location_city=data.get('location_city'),
        founded_year=data.get('founded_year'),
        funding_status=data.get('funding_status'),
        funding_amount=data.get('funding_amount'),
        technology_stack=data.get('technology_stack'),
        description=data.get('description'),
        linkedin_url=data.get('linkedin_url'),
        phone=data.get('phone')
    )
    
    db.session.add(company)
    db.session.commit()
    
    return jsonify(company.to_dict()), 201

@companies_bp.route('/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """Get a specific company by ID"""
    company = Company.query.get_or_404(company_id)
    return jsonify(company.to_dict())

@companies_bp.route('/companies/<int:company_id>', methods=['PUT'])
def update_company(company_id):
    """Update a company"""
    company = Company.query.get_or_404(company_id)
    data = request.json
    
    # Update fields if provided
    for field in ['name', 'domain', 'website', 'industry', 'company_size', 
                  'location_country', 'location_state', 'location_city', 
                  'founded_year', 'funding_status', 'funding_amount', 
                  'technology_stack', 'description', 'linkedin_url', 'phone']:
        if field in data:
            setattr(company, field, data[field])
    
    db.session.commit()
    return jsonify(company.to_dict())

@companies_bp.route('/companies/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    """Delete a company"""
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    return '', 204

@companies_bp.route('/companies/search', methods=['POST'])
def advanced_company_search():
    """Advanced company search with complex filters"""
    data = request.json
    filters = data.get('filters', {})
    page = data.get('page', 1)
    per_page = data.get('per_page', 20)
    
    query = Company.query
    
    # Apply filters from the request
    if 'industries' in filters and filters['industries']:
        query = query.filter(Company.industry.in_(filters['industries']))
    
    if 'company_sizes' in filters and filters['company_sizes']:
        query = query.filter(Company.company_size.in_(filters['company_sizes']))
    
    if 'countries' in filters and filters['countries']:
        query = query.filter(Company.location_country.in_(filters['countries']))
    
    if 'funding_statuses' in filters and filters['funding_statuses']:
        query = query.filter(Company.funding_status.in_(filters['funding_statuses']))
    
    if 'technologies' in filters and filters['technologies']:
        tech_conditions = []
        for tech in filters['technologies']:
            tech_conditions.append(Company.technology_stack.ilike(f'%{tech}%'))
        query = query.filter(or_(*tech_conditions))
    
    if 'founded_year_range' in filters:
        year_range = filters['founded_year_range']
        if 'min' in year_range:
            query = query.filter(Company.founded_year >= year_range['min'])
        if 'max' in year_range:
            query = query.filter(Company.founded_year <= year_range['max'])
    
    # Execute paginated query
    companies = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'companies': [company.to_dict() for company in companies.items],
        'total': companies.total,
        'pages': companies.pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': companies.has_next,
        'has_prev': companies.has_prev,
        'filters_applied': filters
    })

@companies_bp.route('/companies/bulk', methods=['POST'])
def bulk_create_companies():
    """Bulk create companies"""
    data = request.json
    companies_data = data.get('companies', [])
    
    companies = []
    for company_data in companies_data:
        company = Company(**company_data)
        companies.append(company)
    
    db.session.add_all(companies)
    db.session.commit()
    
    return jsonify({
        'message': f'Successfully created {len(companies)} companies',
        'companies': [company.to_dict() for company in companies]
    }), 201

