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
            'health': '/health'
        }
    }

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

