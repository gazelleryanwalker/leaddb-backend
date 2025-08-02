"""
Web Scraping Service for Lead Generation
Scrapes public data sources to find companies and contacts
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import random
from urllib.parse import urljoin, urlparse
import json
from typing import List, Dict, Optional

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def search_companies_by_industry(self, industry: str, location: str = "", limit: int = 50) -> List[Dict]:
        """
        Search for companies by industry using multiple free sources
        """
        companies = []
        
        # Search Yellow Pages
        companies.extend(self._search_yellow_pages(industry, location, limit // 3))
        
        # Search Google My Business (via Google search)
        companies.extend(self._search_google_business(industry, location, limit // 3))
        
        # Search industry directories
        companies.extend(self._search_industry_directories(industry, location, limit // 3))
        
        return companies[:limit]
    
    def _search_yellow_pages(self, industry: str, location: str, limit: int) -> List[Dict]:
        """Search Yellow Pages for companies"""
        companies = []
        try:
            # Yellow Pages search URL
            search_term = f"{industry} {location}".strip()
            url = f"https://www.yellowpages.com/search?search_terms={search_term}&geo_location_terms={location}"
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract business listings
                listings = soup.find_all('div', class_='result')[:limit]
                
                for listing in listings:
                    company = self._extract_company_from_yp_listing(listing)
                    if company:
                        companies.append(company)
                        
            time.sleep(random.uniform(1, 3))  # Rate limiting
            
        except Exception as e:
            print(f"Error searching Yellow Pages: {e}")
            
        return companies
    
    def _search_google_business(self, industry: str, location: str, limit: int) -> List[Dict]:
        """Search Google for business listings"""
        companies = []
        try:
            # Google search for businesses
            search_query = f"{industry} companies {location} site:linkedin.com/company OR site:crunchbase.com"
            url = f"https://www.google.com/search?q={search_query}"
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract search results
                results = soup.find_all('div', class_='g')[:limit]
                
                for result in results:
                    company = self._extract_company_from_google_result(result)
                    if company:
                        companies.append(company)
                        
            time.sleep(random.uniform(2, 4))  # Rate limiting
            
        except Exception as e:
            print(f"Error searching Google: {e}")
            
        return companies
    
    def _search_industry_directories(self, industry: str, location: str, limit: int) -> List[Dict]:
        """Search industry-specific directories"""
        companies = []
        
        # Industry-specific directory URLs
        directories = {
            'technology': [
                'https://www.crunchbase.com',
                'https://angel.co',
                'https://www.inc.com/inc5000'
            ],
            'marketing': [
                'https://clutch.co/agencies',
                'https://www.agencyspotter.com'
            ],
            'healthcare': [
                'https://www.healthgrades.com',
                'https://www.medicare.gov'
            ]
        }
        
        industry_lower = industry.lower()
        if industry_lower in directories:
            for directory_url in directories[industry_lower]:
                try:
                    companies.extend(self._scrape_directory(directory_url, industry, location, limit // len(directories[industry_lower])))
                except Exception as e:
                    print(f"Error scraping {directory_url}: {e}")
                    
        return companies
    
    def _extract_company_from_yp_listing(self, listing) -> Optional[Dict]:
        """Extract company information from Yellow Pages listing"""
        try:
            name_elem = listing.find('a', class_='business-name')
            name = name_elem.text.strip() if name_elem else None
            
            if not name:
                return None
                
            # Extract other details
            address_elem = listing.find('div', class_='street-address')
            address = address_elem.text.strip() if address_elem else ""
            
            phone_elem = listing.find('div', class_='phones')
            phone = phone_elem.text.strip() if phone_elem else ""
            
            website_elem = listing.find('a', class_='track-visit-website')
            website = website_elem.get('href') if website_elem else ""
            
            return {
                'name': name,
                'website': website,
                'phone': phone,
                'address': address,
                'source': 'Yellow Pages'
            }
            
        except Exception as e:
            print(f"Error extracting YP listing: {e}")
            return None
    
    def _extract_company_from_google_result(self, result) -> Optional[Dict]:
        """Extract company information from Google search result"""
        try:
            title_elem = result.find('h3')
            title = title_elem.text.strip() if title_elem else None
            
            if not title:
                return None
                
            link_elem = result.find('a')
            link = link_elem.get('href') if link_elem else ""
            
            snippet_elem = result.find('span', class_='st')
            snippet = snippet_elem.text.strip() if snippet_elem else ""
            
            # Extract company name from title
            company_name = title.split(' - ')[0] if ' - ' in title else title
            
            return {
                'name': company_name,
                'website': link,
                'description': snippet,
                'source': 'Google Search'
            }
            
        except Exception as e:
            print(f"Error extracting Google result: {e}")
            return None
    
    def _scrape_directory(self, directory_url: str, industry: str, location: str, limit: int) -> List[Dict]:
        """Scrape a specific directory for companies"""
        companies = []
        
        # This is a simplified implementation
        # In practice, each directory would need specific scraping logic
        try:
            response = self.session.get(directory_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Generic company extraction (would be customized per directory)
                company_links = soup.find_all('a', href=True)[:limit]
                
                for link in company_links:
                    if 'company' in link.get('href', '').lower():
                        company_name = link.text.strip()
                        if company_name and len(company_name) > 2:
                            companies.append({
                                'name': company_name,
                                'website': link.get('href'),
                                'source': directory_url
                            })
                            
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"Error scraping directory {directory_url}: {e}")
            
        return companies
    
    def find_company_contacts(self, company_website: str) -> List[Dict]:
        """
        Find contacts on a company website
        """
        contacts = []
        
        if not company_website:
            return contacts
            
        try:
            # Common contact pages
            contact_pages = [
                '',  # Homepage
                '/about',
                '/team',
                '/contact',
                '/leadership',
                '/management',
                '/staff'
            ]
            
            for page in contact_pages:
                url = urljoin(company_website, page)
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        page_contacts = self._extract_contacts_from_page(soup, company_website)
                        contacts.extend(page_contacts)
                        
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    print(f"Error scraping {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error finding contacts for {company_website}: {e}")
            
        # Remove duplicates
        unique_contacts = []
        seen_emails = set()
        
        for contact in contacts:
            email = contact.get('email', '')
            if email and email not in seen_emails:
                seen_emails.add(email)
                unique_contacts.append(contact)
                
        return unique_contacts[:10]  # Limit to 10 contacts per company
    
    def _extract_contacts_from_page(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract contact information from a webpage"""
        contacts = []
        
        # Look for email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        page_text = soup.get_text()
        emails = re.findall(email_pattern, page_text)
        
        # Look for names near email addresses
        for email in emails:
            if self._is_valid_business_email(email):
                # Try to find associated name
                name = self._find_name_near_email(soup, email)
                
                contact = {
                    'email': email,
                    'name': name,
                    'source': base_url
                }
                
                # Try to extract job title
                title = self._extract_job_title_near_email(soup, email)
                if title:
                    contact['job_title'] = title
                    
                contacts.append(contact)
                
        # Look for LinkedIn profiles
        linkedin_links = soup.find_all('a', href=re.compile(r'linkedin\.com/in/'))
        for link in linkedin_links:
            linkedin_url = link.get('href')
            name = link.text.strip() or self._extract_name_from_linkedin_url(linkedin_url)
            
            if name:
                contacts.append({
                    'name': name,
                    'linkedin_url': linkedin_url,
                    'source': base_url
                })
                
        return contacts
    
    def _is_valid_business_email(self, email: str) -> bool:
        """Check if email looks like a business email"""
        # Skip common non-business domains
        skip_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'aol.com', 'icloud.com', 'protonmail.com'
        ]
        
        domain = email.split('@')[1].lower()
        return domain not in skip_domains
    
    def _find_name_near_email(self, soup: BeautifulSoup, email: str) -> str:
        """Try to find a name associated with an email address"""
        # Look for text near the email
        email_elem = soup.find(text=re.compile(re.escape(email)))
        if email_elem:
            parent = email_elem.parent
            if parent:
                # Look for name patterns in the same element or nearby
                text = parent.get_text()
                name_match = re.search(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', text)
                if name_match:
                    return name_match.group(1)
                    
        return ""
    
    def _extract_job_title_near_email(self, soup: BeautifulSoup, email: str) -> str:
        """Try to extract job title near an email"""
        # Common job title patterns
        title_patterns = [
            r'\b(CEO|CTO|CFO|COO|VP|Vice President|President|Director|Manager|Lead|Head)\b',
            r'\b(Chief Executive Officer|Chief Technology Officer|Chief Financial Officer)\b',
            r'\b(Senior|Principal|Associate|Assistant)\s+\w+\b'
        ]
        
        email_elem = soup.find(text=re.compile(re.escape(email)))
        if email_elem:
            parent = email_elem.parent
            if parent:
                text = parent.get_text()
                for pattern in title_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        return match.group(0)
                        
        return ""
    
    def _extract_name_from_linkedin_url(self, linkedin_url: str) -> str:
        """Extract name from LinkedIn URL"""
        # LinkedIn URLs often contain the person's name
        # e.g., linkedin.com/in/john-smith-123456
        match = re.search(r'/in/([^/]+)', linkedin_url)
        if match:
            name_slug = match.group(1)
            # Convert slug to name
            name_parts = name_slug.split('-')
            if len(name_parts) >= 2:
                first_name = name_parts[0].capitalize()
                last_name = name_parts[1].capitalize()
                return f"{first_name} {last_name}"
                
        return ""

