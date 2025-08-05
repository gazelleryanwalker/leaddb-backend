from flask import Blueprint
from src.models.company import Company
from src.models.contact import Contact
from src.models.lead_list import LeadList

api_bp = Blueprint('api', __name__)

@api_bp.route('/')
def api_info():
    return {
        'service': 'LeadDB API',
        'version': '1.0.0',
        'endpoints': {
            'stats': '/api/stats',
            'companies': '/api/companies',
            'contacts': '/api/contacts',
            'lead_lists': '/api/lists',
            'lead_generation': '/api/leads',
            'export': '/api/export',
            'health': '/health',
            'init_db': '/api/init-database'
        }
    }

@api_bp.route('/stats')
def get_stats():
    try:
        company_count = Company.query.count()
        contact_count = Contact.query.count()
        lead_list_count = LeadList.query.count()
        
        return {
            'status': 'success',
            'stats': {
                'companies': company_count,
                'contacts': contact_count,
                'campaigns': lead_list_count
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Failed to retrieve stats: {str(e)}'
        }, 500
