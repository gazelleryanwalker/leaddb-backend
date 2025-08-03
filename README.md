# LeadDB Backend

Apollo.io alternative lead database system - Backend API

## Features
- Flask REST API with PostgreSQL
- Lead and company management
- Contact database with lead scoring
- CRM export (Zoho, HubSpot)
- Sample data included

## Deployment
- Deploy to Railway.app
- Add PostgreSQL database
- Set environment variables
- Run database initialization

## Environment Variables
```
SECRET_KEY=your-secret-key
FLASK_ENV=production
DATABASE_URL=postgresql://... (auto-set by Railway)
```

## API Endpoints
- GET /health - Health check
- GET /api/leads - Get all leads
- POST /api/leads - Create lead
- GET /api/companies - Get companies
- GET /api/contacts - Get contacts

Ready for Railway deployment!
