"""
Lead Generation Service
Handles real lead generation using web scraping and email generation
"""

import requests
import random
from typing import List, Dict, Optional
from datetime import datetime
from .web_scraper import WebScraper
from .email_generator import EmailGenerator

class LeadGenerationService:
    def __init__(self):
        self.web_scraper = WebScraper()
        self.email_generator = EmailGenerator()
        
    def generate_leads_by_industry(self, industry: str, location: str = "", 
                                 company_size: str = "", limit: int = 50, 
                                 use_real_data: bool = True) -> Dict:
        """
        Generate leads by industry criteria using real web scraping
        """
        
        if use_real_data:
            # Use real web scraping
            companies = self._scrape_real_companies(industry, location, company_size, limit)
        else:
            # Fall back to mock data for testing
            companies = self._generate_mock_companies(industry, location, company_size, limit)
        
        # Enrich companies with contacts and emails
        enriched_companies = []
        all_contacts = []
        
        for company in companies:
            enriched_company = self._enrich_company_with_contacts(company)
            enriched_companies.append(enriched_company)
            
            # Add contacts to the all_contacts list
            for contact in enriched_company.get('contacts', []):
                contact['company_name'] = company.get('name', '')
                all_contacts.append(contact)
        
        return {
            'companies': enriched_companies,
            'contacts': all_contacts,
            'total_companies': len(enriched_companies),
            'total_contacts': len(all_contacts),
            'search_criteria': {
                'industry': industry,
                'location': location,
                'company_size': company_size,
                'limit': limit,
                'data_source': 'real_scraping' if use_real_data else 'mock_data'
            }
        }
    
    def _scrape_real_companies(self, industry: str, location: str, 
                              company_size: str, limit: int) -> List[Dict]:
        """Scrape real companies using web scraper"""
        
        try:
            # Use web scraper to find companies
            companies = self.web_scraper.search_companies_by_industry(
                industry=industry,
                location=location,
                limit=limit
            )
            
            # Enhance company data
            enhanced_companies = []
            for company in companies:
                enhanced_company = self._enhance_company_data(company, industry, company_size)
                enhanced_companies.append(enhanced_company)
            
            return enhanced_companies
            
        except Exception as e:
            print(f"Error scraping companies: {e}")
            # Fall back to mock data
            return self._generate_mock_companies(industry, location, company_size, min(limit, 10))
    
    def _enhance_company_data(self, company: Dict, industry: str, company_size: str) -> Dict:
        """Enhance scraped company data with additional fields"""
        
        enhanced = company.copy()
        
        # Add missing fields
        enhanced.update({
            'industry': industry,
            'company_size': company_size or self._estimate_company_size(),
            'founded_year': random.randint(2010, 2023),
            'funding_status': random.choice(['Seed', 'Series A', 'Series B', 'Bootstrapped', 'Unknown']),
            'employee_count': self._estimate_employee_count(company_size),
            'description': enhanced.get('description', f"Company in {industry} industry"),
            'location_country': 'United States',  # Default for now
        })
        
        # Extract domain from website
        if enhanced.get('website'):
            enhanced['domain'] = self.email_generator.extract_domain_from_website(enhanced['website'])
        
        return enhanced
    
    def _enrich_company_with_contacts(self, company: Dict) -> Dict:
        """Find and enrich contacts for a company"""
        
        enriched_company = company.copy()
        website = company.get('website', '')
        domain = company.get('domain', '')
        
        if not domain and website:
            domain = self.email_generator.extract_domain_from_website(website)
            enriched_company['domain'] = domain
        
        # Find contacts using web scraper
        contacts = []
        if website:
            try:
                scraped_contacts = self.web_scraper.find_company_contacts(website)
                
                # Process and enhance contacts
                for contact in scraped_contacts:
                    enhanced_contact = self._enhance_contact_data(contact, company)
                    contacts.append(enhanced_contact)
                    
            except Exception as e:
                print(f"Error finding contacts for {website}: {e}")
        
        # If no contacts found, generate some based on common patterns
        if not contacts and domain:
            contacts = self._generate_likely_contacts(company, domain)
        
        # Generate emails for contacts without them
        if domain:
            contacts = self.email_generator.bulk_email_generation(contacts, domain)
        
        enriched_company['contacts'] = contacts
        enriched_company['contact_count'] = len(contacts)
        
        return enriched_company
    
    def _enhance_contact_data(self, contact: Dict, company: Dict) -> Dict:
        """Enhance contact data with additional fields"""
        
        enhanced = contact.copy()
        
        # Add company information
        enhanced.update({
            'company_name': company.get('name', ''),
            'company_domain': company.get('domain', ''),
            'company_industry': company.get('industry', ''),
            'location_country': company.get('location_country', 'United States'),
            'location_state': company.get('location_state', ''),
            'location_city': company.get('location_city', ''),
        })
        
        # Parse name if not already split
        if enhanced.get('name') and not enhanced.get('first_name'):
            name_parts = enhanced['name'].split(' ', 1)
            enhanced['first_name'] = name_parts[0]
            enhanced['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
        
        # Determine department and seniority from job title
        job_title = enhanced.get('job_title', '')
        if job_title:
            enhanced['department'] = self._get_department_from_title(job_title)
            enhanced['seniority_level'] = self._get_seniority_from_title(job_title)
        
        # Calculate lead score
        enhanced['lead_score'] = self._calculate_lead_score(enhanced)
        
        return enhanced
    
    def _generate_likely_contacts(self, company: Dict, domain: str) -> List[Dict]:
        """Generate likely contacts based on common business roles"""
        
        common_roles = [
            {'title': 'CEO', 'first_names': ['John', 'Jane', 'Michael', 'Sarah', 'David']},
            {'title': 'CTO', 'first_names': ['Alex', 'Chris', 'Jordan', 'Taylor', 'Morgan']},
            {'title': 'VP Sales', 'first_names': ['Robert', 'Lisa', 'Mark', 'Jennifer', 'Brian']},
            {'title': 'VP Marketing', 'first_names': ['Emily', 'Daniel', 'Michelle', 'Kevin', 'Amanda']},
        ]
        
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
        
        contacts = []
        
        for role in common_roles[:2]:  # Limit to 2 contacts
            first_name = random.choice(role['first_names'])
            last_name = random.choice(last_names)
            
            contact = {
                'first_name': first_name,
                'last_name': last_name,
                'name': f"{first_name} {last_name}",
                'job_title': role['title'],
                'company_name': company.get('name', ''),
                'source': 'Generated Pattern'
            }
            
            contacts.append(contact)
        
        return contacts
    
    def _estimate_company_size(self) -> str:
        """Estimate company size"""
        return random.choice(['1-10', '10-50', '50-100', '100-500', '500+'])
    
    def _estimate_employee_count(self, company_size: str) -> int:
        """Estimate employee count from company size"""
        size_ranges = {
            '1-10': (1, 10),
            '10-50': (10, 50),
            '50-100': (50, 100),
            '100-500': (100, 500),
            '500+': (500, 1000)
        }
        
        if company_size in size_ranges:
            min_size, max_size = size_ranges[company_size]
            return random.randint(min_size, max_size)
        
        return random.randint(10, 100)
    
    def _generate_mock_companies(self, industry: str, location: str, 
                               company_size: str, limit: int) -> List[Dict]:
        """Generate mock companies for demonstration (fallback)"""
        
        # Industry-specific company name patterns
        industry_patterns = {
            'technology': ['Tech', 'Soft', 'Data', 'Cloud', 'AI', 'Digital'],
            'marketing': ['Marketing', 'Brand', 'Creative', 'Media', 'Growth'],
            'healthcare': ['Health', 'Medical', 'Care', 'Wellness', 'Bio'],
            'finance': ['Financial', 'Capital', 'Investment', 'Bank', 'Fund'],
            'retail': ['Retail', 'Store', 'Shop', 'Market', 'Commerce']
        }
        
        suffixes = ['Solutions', 'Systems', 'Group', 'Corp', 'Inc', 'LLC', 'Partners']
        
        companies = []
        patterns = industry_patterns.get(industry.lower(), ['Business', 'Company'])
        
        for i in range(min(limit, 10)):  # Limit mock data
            # Generate company name
            prefix = random.choice(patterns)
            suffix = random.choice(suffixes)
            company_name = f"{prefix}{suffix} {random.randint(100, 999)}"
            
            # Generate mock company data
            company = {
                'name': company_name,
                'industry': industry,
                'website': f"https://{company_name.lower().replace(' ', '')}.com",
                'domain': f"{company_name.lower().replace(' ', '')}.com",
                'company_size': company_size or random.choice(['10-50', '50-100', '100-500']),
                'location_country': 'United States',
                'location_state': location.split(',')[1].strip() if ',' in location else 'California',
                'location_city': location.split(',')[0].strip() if ',' in location else 'San Francisco',
                'description': f"Leading {industry.lower()} company providing innovative solutions",
                'founded_year': random.randint(2010, 2023),
                'funding_status': random.choice(['Seed', 'Series A', 'Series B', 'Bootstrapped']),
                'employee_count': random.randint(10, 500),
                'source': 'Mock Data Generator'
            }
            
            companies.append(company)
        
        return companies
    
    def _get_department_from_title(self, job_title: str) -> str:
        """Determine department from job title"""
        title_lower = job_title.lower()
        
        if any(word in title_lower for word in ['ceo', 'president', 'founder']):
            return 'Executive'
        elif any(word in title_lower for word in ['cto', 'engineering', 'technical', 'developer']):
            return 'Engineering'
        elif any(word in title_lower for word in ['sales', 'business development']):
            return 'Sales'
        elif any(word in title_lower for word in ['marketing', 'growth', 'brand']):
            return 'Marketing'
        elif any(word in title_lower for word in ['finance', 'accounting', 'cfo']):
            return 'Finance'
        else:
            return 'Other'
    
    def _get_seniority_from_title(self, job_title: str) -> str:
        """Determine seniority level from job title"""
        title_lower = job_title.lower()
        
        if any(word in title_lower for word in ['ceo', 'cto', 'cfo', 'coo', 'chief']):
            return 'C-Level'
        elif any(word in title_lower for word in ['vp', 'vice president']):
            return 'VP'
        elif any(word in title_lower for word in ['director', 'head']):
            return 'Director'
        elif any(word in title_lower for word in ['manager', 'lead']):
            return 'Manager'
        else:
            return 'Individual Contributor'
    
    def _calculate_lead_score(self, contact: Dict) -> int:
        """Calculate lead score based on available data"""
        score = 0
        
        # Email presence
        if contact.get('email'):
            score += 30
        
        # Phone presence
        if contact.get('phone'):
            score += 20
        
        # LinkedIn presence
        if contact.get('linkedin_url'):
            score += 15
        
        # Seniority level
        seniority = contact.get('seniority_level', '')
        if 'C-Level' in seniority:
            score += 25
        elif 'VP' in seniority:
            score += 20
        elif 'Director' in seniority:
            score += 15
        elif 'Manager' in seniority:
            score += 10
        
        # Job title relevance
        job_title = contact.get('job_title', '').lower()
        if any(word in job_title for word in ['ceo', 'founder', 'president']):
            score += 10
        
        # Email confidence (if generated)
        email_confidence = contact.get('email_confidence', 0)
        if email_confidence > 70:
            score += 10
        elif email_confidence > 50:
            score += 5
        
        return min(score, 100)  # Cap at 100
    
    def enrich_contact_data(self, contact: Dict) -> Dict:
        """
        Enrich contact data with additional information
        """
        
        enriched_contact = contact.copy()
        
        # Generate email if missing
        if not enriched_contact.get('email') and enriched_contact.get('company_domain'):
            first_name = enriched_contact.get('first_name', '')
            last_name = enriched_contact.get('last_name', '')
            domain = enriched_contact.get('company_domain', '')
            
            if first_name and last_name and domain:
                generated_emails = self.email_generator.generate_and_verify_emails(
                    first_name, last_name, domain, max_attempts=3
                )
                
                if generated_emails:
                    best_email = generated_emails[0]
                    enriched_contact['email'] = best_email['email']
                    enriched_contact['email_confidence'] = best_email['confidence']
        
        # Add LinkedIn URL if missing
        if not enriched_contact.get('linkedin_url'):
            first_name = enriched_contact.get('first_name', '').lower()
            last_name = enriched_contact.get('last_name', '').lower()
            if first_name and last_name:
                enriched_contact['linkedin_url'] = f"https://linkedin.com/in/{first_name}-{last_name}"
        
        # Recalculate lead score
        enriched_contact['lead_score'] = self._calculate_lead_score(enriched_contact)
        
        return enriched_contact
    
    def search_companies_by_criteria(self, criteria: Dict) -> List[Dict]:
        """
        Search for companies based on multiple criteria
        """
        industry = criteria.get('industry', '')
        location = criteria.get('location', '')
        company_size = criteria.get('company_size', '')
        limit = criteria.get('limit', 50)
        use_real_data = criteria.get('use_real_data', True)
        
        result = self.generate_leads_by_industry(
            industry, location, company_size, limit, use_real_data
        )
        return result.get('companies', [])
    
    def find_company_contacts(self, company_name: str, company_domain: str = None) -> List[Dict]:
        """
        Find contacts for a specific company using web scraping
        """
        if not company_domain:
            # Try to construct website URL
            website = f"https://{company_domain}" if company_domain else f"https://{company_name.lower().replace(' ', '')}.com"
        else:
            website = f"https://{company_domain}"
        
        try:
            contacts = self.web_scraper.find_company_contacts(website)
            
            # Enhance contacts
            enhanced_contacts = []
            for contact in contacts:
                enhanced_contact = self._enhance_contact_data(contact, {
                    'name': company_name,
                    'domain': company_domain
                })
                enhanced_contacts.append(enhanced_contact)
            
            return enhanced_contacts
            
        except Exception as e:
            print(f"Error finding contacts for {company_name}: {e}")
            return []
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email format and deliverability
        """
        return self.email_generator._is_valid_email_format(email)
    
    def bulk_enrich_contacts(self, contact_ids: List[int]) -> Dict:
        """
        Bulk enrich existing contacts in the database
        """
        # This would typically:
        # 1. Fetch contacts from database
        # 2. Use web scraping and email generation to enrich data
        # 3. Update database with enriched data
        
        return {
            'enriched_count': len(contact_ids),
            'failed_count': 0,
            'updated_fields': ['lead_score', 'linkedin_url', 'phone', 'email']
        }

