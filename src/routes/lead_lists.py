from flask import Blueprint, jsonify, request
from src.models.user import db
from src.models.lead_list import LeadList, LeadListContact, SavedSearch
from src.models.contact import Contact

lead_lists_bp = Blueprint('lead_lists', __name__)

@lead_lists_bp.route('/lists', methods=['GET'])
def get_lead_lists():
    """Get all lead lists"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    lists = LeadList.query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'lists': [lead_list.to_dict() for lead_list in lists.items],
        'total': lists.total,
        'pages': lists.pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': lists.has_next,
        'has_prev': lists.has_prev
    })

@lead_lists_bp.route('/lists', methods=['POST'])
def create_lead_list():
    """Create a new lead list"""
    data = request.json
    
    lead_list = LeadList(
        name=data.get('name'),
        description=data.get('description'),
        created_by=data.get('created_by', 'system')
    )
    
    db.session.add(lead_list)
    db.session.commit()
    
    return jsonify(lead_list.to_dict()), 201

@lead_lists_bp.route('/lists/<int:list_id>', methods=['GET'])
def get_lead_list(list_id):
    """Get a specific lead list with its contacts"""
    lead_list = LeadList.query.get_or_404(list_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    contacts = lead_list.contacts.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'list': lead_list.to_dict(),
        'contacts': [contact.to_dict() for contact in contacts.items],
        'total_contacts': contacts.total,
        'pages': contacts.pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': contacts.has_next,
        'has_prev': contacts.has_prev
    })

@lead_lists_bp.route('/lists/<int:list_id>', methods=['PUT'])
def update_lead_list(list_id):
    """Update a lead list"""
    lead_list = LeadList.query.get_or_404(list_id)
    data = request.json
    
    lead_list.name = data.get('name', lead_list.name)
    lead_list.description = data.get('description', lead_list.description)
    
    db.session.commit()
    return jsonify(lead_list.to_dict())

@lead_lists_bp.route('/lists/<int:list_id>', methods=['DELETE'])
def delete_lead_list(list_id):
    """Delete a lead list"""
    lead_list = LeadList.query.get_or_404(list_id)
    db.session.delete(lead_list)
    db.session.commit()
    return '', 204

@lead_lists_bp.route('/lists/<int:list_id>/contacts', methods=['POST'])
def add_contacts_to_list(list_id):
    """Add contacts to a lead list"""
    lead_list = LeadList.query.get_or_404(list_id)
    data = request.json
    contact_ids = data.get('contact_ids', [])
    
    added_count = 0
    for contact_id in contact_ids:
        # Check if contact exists
        contact = Contact.query.get(contact_id)
        if not contact:
            continue
            
        # Check if already in list
        existing = LeadListContact.query.filter_by(
            list_id=list_id, 
            contact_id=contact_id
        ).first()
        
        if not existing:
            list_contact = LeadListContact(
                list_id=list_id,
                contact_id=contact_id
            )
            db.session.add(list_contact)
            added_count += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'Added {added_count} contacts to list',
        'list': lead_list.to_dict()
    })

@lead_lists_bp.route('/lists/<int:list_id>/contacts/<int:contact_id>', methods=['DELETE'])
def remove_contact_from_list(list_id, contact_id):
    """Remove a contact from a lead list"""
    list_contact = LeadListContact.query.filter_by(
        list_id=list_id, 
        contact_id=contact_id
    ).first_or_404()
    
    db.session.delete(list_contact)
    db.session.commit()
    
    return '', 204

@lead_lists_bp.route('/lists/<int:list_id>/contacts/bulk', methods=['DELETE'])
def bulk_remove_contacts_from_list(list_id):
    """Bulk remove contacts from a lead list"""
    data = request.json
    contact_ids = data.get('contact_ids', [])
    
    removed_count = LeadListContact.query.filter(
        LeadListContact.list_id == list_id,
        LeadListContact.contact_id.in_(contact_ids)
    ).delete(synchronize_session=False)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Removed {removed_count} contacts from list'
    })

# Saved Searches endpoints
@lead_lists_bp.route('/searches', methods=['GET'])
def get_saved_searches():
    """Get all saved searches"""
    searches = SavedSearch.query.all()
    return jsonify([search.to_dict() for search in searches])

@lead_lists_bp.route('/searches', methods=['POST'])
def save_search():
    """Save a search filter configuration"""
    data = request.json
    
    search = SavedSearch(
        name=data.get('name'),
        filters=data.get('filters'),
        created_by=data.get('created_by', 'system')
    )
    
    db.session.add(search)
    db.session.commit()
    
    return jsonify(search.to_dict()), 201

@lead_lists_bp.route('/searches/<int:search_id>', methods=['DELETE'])
def delete_saved_search(search_id):
    """Delete a saved search"""
    search = SavedSearch.query.get_or_404(search_id)
    db.session.delete(search)
    db.session.commit()
    return '', 204

@lead_lists_bp.route('/lists/stats', methods=['GET'])
def get_list_stats():
    """Get lead list statistics"""
    total_lists = LeadList.query.count()
    total_list_contacts = LeadListContact.query.count()
    
    # Top lists by contact count
    top_lists = db.session.query(
        LeadList.name,
        db.func.count(LeadListContact.contact_id).label('contact_count')
    ).join(LeadListContact).group_by(LeadList.id, LeadList.name).order_by(
        db.func.count(LeadListContact.contact_id).desc()
    ).limit(10).all()
    
    return jsonify({
        'total_lists': total_lists,
        'total_list_contacts': total_list_contacts,
        'top_lists': [{'name': stat[0], 'contact_count': stat[1]} for stat in top_lists]
    })

