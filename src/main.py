import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database and models
from src.models.user import db
from src.models.company import Company
from src.models.contact import Contact
from src.models.lead_list import LeadList, LeadListContact, SavedSearch

# Import all route blueprints
from src.routes.user import user_bp
from src.routes.companies import companies_bp
from src.routes.contacts import contacts_bp
from src.routes.lead_lists import lead_lists_bp
from src.routes.export import export_bp
from src.routes.lead_generation import lead_gen_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration - supports both PostgreSQL (production) and SQLite (development)
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Production: Use PostgreSQL from Railway/Render
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Development: Use SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for all routes
CORS(app, origins=['*'])

# Initialize database
db.init_app(app)

# Register all blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(companies_bp, url_prefix='/api')
app.register_blueprint(contacts_bp, url_prefix='/api')
app.register_blueprint(lead_lists_bp, url_prefix='/api')
app.register_blueprint(export_bp, url_prefix='/api')
app.register_blueprint(lead_gen_bp, url_prefix='/api/leads')

# Health check endpoint
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'service': 'leaddb-backend'}

# API info endpoint
@app.route('/api')
def api_info():
    return {
        'service': 'LeadDB API',
        'version': '1.0.0',
        'endpoints': {
            'companies': '/api/companies',
            'contacts': '/api/contacts',
            'lead_lists': '/api/lists',
            'lead_generation': '/api/leads',
            'export': '/api/export',
            'health': '/health',
            'init_db': '/api/init-database'
        }
    }

# Database initialization endpoint
@app.route('/api/init-database', methods=['POST', 'GET'])
def init_database():
    try:
        # Check if data already exists
        existing_companies = Company.query.count()
        existing_contacts = Contact.query.count()
        
        if existing_companies > 0 or existing_contacts > 0:
            return {
                'status': 'already_initialized',
                'message': f'Database already has {existing_companies} companies and {existing_contacts} contacts',
                'companies': existing_companies,
                'contacts': existing_contacts
            }
        
        # Create sample companies
        companies_data = [
            {
                'name': 'TechCorp Solutions',
                'domain': 'techcorp.com',
                'website': 'https://techcorp.com',
                'industry': 'Technology',
                'size': '100-500',
                'location': 'San Francisco, CA',
                'funding': 'Series B',
                'description': 'Leading software development company'
            },
            {
                'name': 'HVAC Masters Inc',
                'domain': 'hvacmasters.com',
                'website': 'https://hvacmasters.com',
                'industry': 'HVAC',
                'size': '50-100',
                'location': 'Miami, FL',
                'funding': 'Bootstrapped',
                'description': 'Professional HVAC installation and repair services'
            },
            {
                'name': 'Green Energy Solutions',
                'domain': 'greenenergy.com',
                'website': 'https://greenenergy.com',
                'industry': 'Energy',
                'size': '200-1000',
                'location': 'Austin, TX',
                'funding': 'Series A',
                'description': 'Renewable energy consulting and installation'
            },
            {
                'name': 'DataFlow Analytics',
                'domain': 'dataflow.com',
                'website': 'https://dataflow.com',
                'industry': 'Technology',
                'size': '10-50',
                'location': 'New York, NY',
                'funding': 'Seed',
                'description': 'Business intelligence and data analytics platform'
            },
            {
                'name': 'Florida HVAC Pro',
                'domain': 'flhvacpro.com',
                'website': 'https://flhvacpro.com',
                'industry': 'HVAC',
                'size': '20-50',
                'location': 'Orlando, FL',
                'funding': 'Bootstrapped',
                'description': 'Commercial and residential HVAC services'
            }
        ]
        
        created_companies = []
        for comp_data in companies_data:
            company = Company(**comp_data)
            db.session.add(company)
            created_companies.append(company)
        
        db.session.flush()  # Get company IDs
        
        # Create sample contacts
        contacts_data = [
            {
                'name': 'John Smith',
                'email': 'john.smith@techcorp.com',
                'phone': '+1-555-0101',
                'job_title': 'CEO',
                'department': 'Executive',
                'seniority': 'Executive',
                'company_id': created_companies[0].id
            },
            {
                'name': 'Sarah Johnson',
                'email': 'sarah.johnson@techcorp.com',
                'phone': '+1-555-0102',
                'job_title': 'VP of Sales',
                'department': 'Sales',
                'seniority': 'VP',
                'company_id': created_companies[0].id
            },
            {
                'name': 'Mike Rodriguez',
                'email': 'mike@hvacmasters.com',
                'phone': '+1-555-0201',
                'job_title': 'Owner',
                'department': 'Executive',
                'seniority': 'Executive',
                'company_id': created_companies[1].id
            },
            {
                'name': 'Lisa Chen',
                'email': 'lisa.chen@greenenergy.com',
                'phone': '+1-555-0301',
                'job_title': 'Director of Operations',
                'department': 'Operations',
                'seniority': 'Director',
                'company_id': created_companies[2].id
            },
            {
                'name': 'David Wilson',
                'email': 'david@dataflow.com',
                'phone': '+1-555-0401',
                'job_title': 'CTO',
                'department': 'Technology',
                'seniority': 'Executive',
                'company_id': created_companies[3].id
            },
            {
                'name': 'Maria Garcia',
                'email': 'maria@flhvacpro.com',
                'phone': '+1-555-0501',
                'job_title': 'Service Manager',
                'department': 'Operations',
                'seniority': 'Manager',
                'company_id': created_companies[4].id
            }
        ]
        
        created_contacts = []
        for contact_data in contacts_data:
            contact = Contact(**contact_data)
            created_contacts.append(contact)
            db.session.add(contact)
        
        # Create a sample lead list
        lead_list = LeadList(
            name='HVAC Prospects',
            description='Potential HVAC companies for outreach',
            created_by=1  # Assuming user ID 1 exists
        )
        db.session.add(lead_list)
        db.session.flush()
        
        # Add HVAC contacts to the lead list
        for contact in created_contacts:
            if 'hvac' in contact.email.lower():
                lead_list_contact = LeadListContact(
                    lead_list_id=lead_list.id,
                    contact_id=contact.id
                )
                db.session.add(lead_list_contact)
        
        db.session.commit()
        
        return {
            'status': 'success',
            'message': 'Database initialized successfully',
            'companies_created': len(created_companies),
            'contacts_created': len(created_contacts),
            'lead_lists_created': 1
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'status': 'error',
            'message': f'Failed to initialize database: {str(e)}'
        }, 500

# Serve React frontend (if built files are present)
@app.route('/')
def serve_frontend():
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except:
        return {
            'message': 'LeadDB Backend API',
            'status': 'running',
            'frontend': 'not_deployed',
            'api_docs': '/api'
        }

@app.route('/<path:path>')
def serve_static_files(path):
    try:
        return send_from_directory(app.static_folder, path)
    except:
        # If file not found, serve index.html for React Router
        try:
            return send_from_directory(app.static_folder, 'index.html')
        except:
            return {'error': 'File not found'}, 404

# Create database tables
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

