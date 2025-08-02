from flask import Blueprint, jsonify, request, send_file
import csv
import io
import pandas as pd
from datetime import datetime
from src.models.user import db
from src.models.contact import Contact
from src.models.company import Company
from src.models.lead_list import LeadList

export_bp = Blueprint('export', __name__)

@export_bp.route('/export/contacts/csv', methods=['POST'])
def export_contacts_csv():
    """Export contacts to CSV format for Zoho CRM"""
    data = request.json
    filters = data.get('filters', {})
    list_id = data.get('list_id')
    
    # Build query based on filters or list
    if list_id:
        # Export from specific list
        lead_list = LeadList.query.get_or_404(list_id)
        contacts = lead_list.contacts.all()
    else:
        # Export based on filters
        query = Contact.query.join(Company, Contact.company_id == Company.id, isouter=True)
        
        # Apply the same filters as in advanced search
        if 'job_titles' in filters and filters['job_titles']:
            title_conditions = []
            for title in filters['job_titles']:
                title_conditions.append(Contact.job_title.ilike(f'%{title}%'))
            query = query.filter(db.or_(*title_conditions))
        
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
        
        if 'has_email' in filters and filters['has_email']:
            query = query.filter(Contact.email.isnot(None), Contact.email != '')
        
        if 'has_phone' in filters and filters['has_phone']:
            query = query.filter(Contact.phone.isnot(None), Contact.phone != '')
        
        contacts = query.all()
    
    # Create CSV data
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'First Name', 'Last Name', 'Email', 'Phone', 'Job Title', 
        'Department', 'Seniority Level', 'Company Name', 'Company Website',
        'Company Industry', 'Company Size', 'Country', 'State', 'City',
        'LinkedIn URL', 'Twitter URL', 'Lead Score'
    ])
    
    writer.writeheader()
    for contact in contacts:
        writer.writerow(contact.to_export_dict())
    
    # Create file-like object
    output.seek(0)
    csv_data = output.getvalue()
    output.close()
    
    # Create response
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'leads_export_{timestamp}.csv'
    
    return {
        'csv_data': csv_data,
        'filename': filename,
        'total_contacts': len(contacts),
        'export_timestamp': datetime.now().isoformat()
    }

@export_bp.route('/export/contacts/excel', methods=['POST'])
def export_contacts_excel():
    """Export contacts to Excel format"""
    data = request.json
    filters = data.get('filters', {})
    list_id = data.get('list_id')
    
    # Build query (same logic as CSV export)
    if list_id:
        lead_list = LeadList.query.get_or_404(list_id)
        contacts = lead_list.contacts.all()
    else:
        query = Contact.query.join(Company, Contact.company_id == Company.id, isouter=True)
        
        # Apply filters (same as CSV)
        if 'job_titles' in filters and filters['job_titles']:
            title_conditions = []
            for title in filters['job_titles']:
                title_conditions.append(Contact.job_title.ilike(f'%{title}%'))
            query = query.filter(db.or_(*title_conditions))
        
        if 'has_email' in filters and filters['has_email']:
            query = query.filter(Contact.email.isnot(None), Contact.email != '')
        
        contacts = query.all()
    
    # Create DataFrame
    contact_data = [contact.to_export_dict() for contact in contacts]
    df = pd.DataFrame(contact_data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Leads', index=False)
        
        # Add a summary sheet
        summary_data = {
            'Metric': ['Total Contacts', 'Contacts with Email', 'Contacts with Phone', 'Export Date'],
            'Value': [
                len(contacts),
                len([c for c in contacts if c.email]),
                len([c for c in contacts if c.phone]),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    output.seek(0)
    excel_data = output.getvalue()
    output.close()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'leads_export_{timestamp}.xlsx'
    
    return {
        'excel_data': excel_data.hex(),  # Convert to hex for JSON response
        'filename': filename,
        'total_contacts': len(contacts),
        'export_timestamp': datetime.now().isoformat()
    }

@export_bp.route('/export/lists/<int:list_id>/csv', methods=['GET'])
def export_list_csv(list_id):
    """Export a specific list to CSV"""
    lead_list = LeadList.query.get_or_404(list_id)
    contacts = lead_list.contacts.all()
    
    # Create CSV data
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'First Name', 'Last Name', 'Email', 'Phone', 'Job Title', 
        'Department', 'Seniority Level', 'Company Name', 'Company Website',
        'Company Industry', 'Company Size', 'Country', 'State', 'City',
        'LinkedIn URL', 'Twitter URL', 'Lead Score'
    ])
    
    writer.writeheader()
    for contact in contacts:
        writer.writerow(contact.to_export_dict())
    
    output.seek(0)
    csv_data = output.getvalue()
    output.close()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{lead_list.name.replace(" ", "_")}_{timestamp}.csv'
    
    return {
        'csv_data': csv_data,
        'filename': filename,
        'list_name': lead_list.name,
        'total_contacts': len(contacts),
        'export_timestamp': datetime.now().isoformat()
    }

@export_bp.route('/export/companies/csv', methods=['POST'])
def export_companies_csv():
    """Export companies to CSV format"""
    data = request.json
    filters = data.get('filters', {})
    
    # Build query based on filters
    query = Company.query
    
    if 'industries' in filters and filters['industries']:
        query = query.filter(Company.industry.in_(filters['industries']))
    
    if 'company_sizes' in filters and filters['company_sizes']:
        query = query.filter(Company.company_size.in_(filters['company_sizes']))
    
    if 'countries' in filters and filters['countries']:
        query = query.filter(Company.location_country.in_(filters['countries']))
    
    companies = query.all()
    
    # Create CSV data
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'Company Name', 'Website', 'Industry', 'Company Size', 'Country',
        'State', 'City', 'Founded Year', 'Funding Status', 'LinkedIn URL',
        'Phone', 'Description'
    ])
    
    writer.writeheader()
    for company in companies:
        writer.writerow(company.to_export_dict())
    
    output.seek(0)
    csv_data = output.getvalue()
    output.close()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'companies_export_{timestamp}.csv'
    
    return {
        'csv_data': csv_data,
        'filename': filename,
        'total_companies': len(companies),
        'export_timestamp': datetime.now().isoformat()
    }

@export_bp.route('/export/zoho-template', methods=['GET'])
def get_zoho_template():
    """Get Zoho CRM import template"""
    template_fields = [
        'First Name', 'Last Name', 'Email', 'Phone', 'Job Title',
        'Company Name', 'Company Website', 'Company Industry', 
        'Company Size', 'Country', 'State', 'City', 'LinkedIn URL'
    ]
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=template_fields)
    writer.writeheader()
    
    # Add sample row
    sample_row = {
        'First Name': 'John',
        'Last Name': 'Doe',
        'Email': 'john.doe@example.com',
        'Phone': '+1-555-123-4567',
        'Job Title': 'CEO',
        'Company Name': 'Example Corp',
        'Company Website': 'https://example.com',
        'Company Industry': 'Technology',
        'Company Size': '50-100',
        'Country': 'United States',
        'State': 'California',
        'City': 'San Francisco',
        'LinkedIn URL': 'https://linkedin.com/in/johndoe'
    }
    writer.writerow(sample_row)
    
    output.seek(0)
    csv_data = output.getvalue()
    output.close()
    
    return {
        'csv_data': csv_data,
        'filename': 'zoho_crm_template.csv',
        'description': 'Template for Zoho CRM import with sample data'
    }

