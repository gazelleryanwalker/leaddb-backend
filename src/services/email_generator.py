"""
Email Generation and Verification Service
Generates email patterns and verifies email addresses
"""

import re
import dns.resolver
import smtplib
import socket
from typing import List, Dict, Optional, Tuple
import time
import random

class EmailGenerator:
    def __init__(self):
        self.common_patterns = [
            "{first}.{last}@{domain}",
            "{first}{last}@{domain}",
            "{first}@{domain}",
            "{first}.{last_initial}@{domain}",
            "{first_initial}.{last}@{domain}",
            "{first_initial}{last}@{domain}",
            "{first}{last_initial}@{domain}",
            "{last}.{first}@{domain}",
            "{last}{first}@{domain}",
            "{last}@{domain}",
            "{first_initial}{last_initial}@{domain}",
        ]
        
        # Cache for domain patterns
        self.domain_patterns = {}
        
    def generate_email_patterns(self, first_name: str, last_name: str, domain: str) -> List[str]:
        """
        Generate possible email patterns for a person at a company
        """
        if not all([first_name, last_name, domain]):
            return []
            
        # Clean inputs
        first = self._clean_name(first_name)
        last = self._clean_name(last_name)
        domain = self._clean_domain(domain)
        
        if not all([first, last, domain]):
            return []
            
        # Generate variations
        emails = []
        
        # Check if we know the pattern for this domain
        known_pattern = self.domain_patterns.get(domain)
        if known_pattern:
            email = self._apply_pattern(known_pattern, first, last, domain)
            if email:
                emails.append(email)
        
        # Generate all common patterns
        for pattern in self.common_patterns:
            email = self._apply_pattern(pattern, first, last, domain)
            if email and email not in emails:
                emails.append(email)
                
        return emails
    
    def _clean_name(self, name: str) -> str:
        """Clean and normalize a name"""
        if not name:
            return ""
            
        # Remove special characters, keep only letters
        cleaned = re.sub(r'[^a-zA-Z]', '', name.strip())
        return cleaned.lower()
    
    def _clean_domain(self, domain: str) -> str:
        """Clean and normalize a domain"""
        if not domain:
            return ""
            
        # Remove protocol and www
        domain = re.sub(r'^https?://', '', domain)
        domain = re.sub(r'^www\.', '', domain)
        
        # Remove path
        domain = domain.split('/')[0]
        
        return domain.lower()
    
    def _apply_pattern(self, pattern: str, first: str, last: str, domain: str) -> str:
        """Apply an email pattern to generate an email address"""
        try:
            first_initial = first[0] if first else ""
            last_initial = last[0] if last else ""
            
            email = pattern.format(
                first=first,
                last=last,
                first_initial=first_initial,
                last_initial=last_initial,
                domain=domain
            )
            
            # Validate email format
            if self._is_valid_email_format(email):
                return email
                
        except (IndexError, KeyError):
            pass
            
        return ""
    
    def _is_valid_email_format(self, email: str) -> bool:
        """Check if email has valid format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def verify_email_addresses(self, emails: List[str]) -> List[Dict[str, any]]:
        """
        Verify a list of email addresses
        Returns list of dicts with email and verification status
        """
        results = []
        
        for email in emails:
            verification = self.verify_single_email(email)
            results.append({
                'email': email,
                'is_valid': verification['is_valid'],
                'confidence': verification['confidence'],
                'method': verification['method']
            })
            
            # Rate limiting
            time.sleep(random.uniform(0.1, 0.3))
            
        return results
    
    def verify_single_email(self, email: str) -> Dict[str, any]:
        """
        Verify a single email address using multiple methods
        """
        if not self._is_valid_email_format(email):
            return {
                'is_valid': False,
                'confidence': 0,
                'method': 'format_check'
            }
        
        domain = email.split('@')[1]
        
        # Method 1: DNS MX Record Check
        mx_valid = self._check_mx_record(domain)
        if not mx_valid:
            return {
                'is_valid': False,
                'confidence': 10,
                'method': 'mx_record'
            }
        
        # Method 2: SMTP Check (basic)
        smtp_result = self._check_smtp_basic(email)
        
        # Method 3: Pattern Analysis
        pattern_score = self._analyze_email_pattern(email)
        
        # Combine results
        confidence = 30  # Base confidence for valid format + MX
        
        if smtp_result['deliverable']:
            confidence += 40
        elif smtp_result['unknown']:
            confidence += 20
            
        confidence += pattern_score
        
        is_valid = confidence >= 50
        
        return {
            'is_valid': is_valid,
            'confidence': min(confidence, 95),  # Cap at 95%
            'method': 'combined'
        }
    
    def _check_mx_record(self, domain: str) -> bool:
        """Check if domain has MX record"""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            return len(mx_records) > 0
        except:
            return False
    
    def _check_smtp_basic(self, email: str) -> Dict[str, bool]:
        """
        Basic SMTP check (without actually sending)
        """
        domain = email.split('@')[1]
        
        try:
            # Get MX record
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_record = str(mx_records[0].exchange)
            
            # Connect to SMTP server
            server = smtplib.SMTP(timeout=10)
            server.connect(mx_record, 25)
            server.helo()
            
            # Check if email exists (some servers respond)
            code, message = server.rcpt(email)
            server.quit()
            
            if code == 250:
                return {'deliverable': True, 'unknown': False}
            elif code in [450, 451, 452]:
                return {'deliverable': False, 'unknown': True}
            else:
                return {'deliverable': False, 'unknown': False}
                
        except:
            return {'deliverable': False, 'unknown': True}
    
    def _analyze_email_pattern(self, email: str) -> int:
        """
        Analyze email pattern to estimate likelihood of being real
        """
        score = 0
        local_part = email.split('@')[0]
        
        # Common business patterns get higher scores
        if '.' in local_part:
            score += 15  # firstname.lastname is common
            
        if len(local_part) >= 4:
            score += 10  # Reasonable length
            
        # Avoid obvious fake patterns
        if re.search(r'\d{3,}', local_part):
            score -= 20  # Too many numbers
            
        if local_part in ['info', 'contact', 'admin', 'support']:
            score += 5  # Generic but real
            
        return max(0, min(score, 30))
    
    def find_company_email_pattern(self, known_emails: List[str], domain: str) -> Optional[str]:
        """
        Analyze known emails to determine company's email pattern
        """
        if not known_emails:
            return None
            
        patterns = {}
        
        for email in known_emails:
            if not email or '@' not in email:
                continue
                
            local_part = email.split('@')[0]
            
            # Try to identify the pattern
            if '.' in local_part and len(local_part.split('.')) == 2:
                parts = local_part.split('.')
                if len(parts[0]) > 1 and len(parts[1]) > 1:
                    patterns['{first}.{last}@{domain}'] = patterns.get('{first}.{last}@{domain}', 0) + 1
                elif len(parts[0]) == 1:
                    patterns['{first_initial}.{last}@{domain}'] = patterns.get('{first_initial}.{last}@{domain}', 0) + 1
                elif len(parts[1]) == 1:
                    patterns['{first}.{last_initial}@{domain}'] = patterns.get('{first}.{last_initial}@{domain}', 0) + 1
            
            elif len(local_part) > 3 and not '.' in local_part:
                patterns['{first}{last}@{domain}'] = patterns.get('{first}{last}@{domain}', 0) + 1
        
        # Return most common pattern
        if patterns:
            most_common = max(patterns, key=patterns.get)
            self.domain_patterns[domain] = most_common
            return most_common
            
        return None
    
    def generate_and_verify_emails(self, first_name: str, last_name: str, domain: str, 
                                 max_attempts: int = 5) -> List[Dict[str, any]]:
        """
        Generate email patterns and verify them, returning best candidates
        """
        # Generate possible emails
        possible_emails = self.generate_email_patterns(first_name, last_name, domain)
        
        if not possible_emails:
            return []
        
        # Limit attempts
        emails_to_check = possible_emails[:max_attempts]
        
        # Verify emails
        verified_emails = self.verify_email_addresses(emails_to_check)
        
        # Sort by confidence
        verified_emails.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Return only likely valid emails
        valid_emails = [e for e in verified_emails if e['confidence'] >= 50]
        
        return valid_emails
    
    def extract_domain_from_website(self, website: str) -> str:
        """Extract email domain from website URL"""
        if not website:
            return ""
            
        domain = self._clean_domain(website)
        
        # Remove common subdomains
        parts = domain.split('.')
        if len(parts) >= 3 and parts[0] in ['www', 'mail', 'email']:
            domain = '.'.join(parts[1:])
            
        return domain
    
    def bulk_email_generation(self, contacts: List[Dict], company_domain: str) -> List[Dict]:
        """
        Generate emails for multiple contacts at once
        """
        results = []
        
        # First, try to find company email pattern from any known emails
        known_emails = [c.get('email') for c in contacts if c.get('email')]
        if known_emails:
            self.find_company_email_pattern(known_emails, company_domain)
        
        for contact in contacts:
            first_name = contact.get('first_name', '')
            last_name = contact.get('last_name', '')
            
            # Skip if we already have an email
            if contact.get('email'):
                results.append({
                    **contact,
                    'generated_emails': [],
                    'email_confidence': 100
                })
                continue
            
            # Generate and verify emails
            generated_emails = self.generate_and_verify_emails(
                first_name, last_name, company_domain, max_attempts=3
            )
            
            # Use best email if available
            best_email = None
            confidence = 0
            
            if generated_emails:
                best_email = generated_emails[0]['email']
                confidence = generated_emails[0]['confidence']
            
            results.append({
                **contact,
                'email': best_email or contact.get('email', ''),
                'generated_emails': generated_emails,
                'email_confidence': confidence
            })
            
        return results

