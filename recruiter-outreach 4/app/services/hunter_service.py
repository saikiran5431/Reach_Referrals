"""
app/services/hunter_service.py — WHY IT EXISTS
================================================
All Hunter.io API logic lives here (not in routes).
Separation of concerns: routes handle HTTP, services handle business logic.

Hunter.io free tier: 25 email finder requests/month.
Endpoint used: /v2/email-finder (finds email by name + domain)

Two strategies:
  1. Direct API call with first + last name → Hunter finds the best match
  2. If that fails, generate patterns locally (firstname.lastname@, f.lastname@)
     and return them as "guesses" with low confidence

Domain inference: "Google" → "google.com", "Stripe" → "stripe.com"
(basic heuristic — user can always override with company_domain field)
"""

import httpx
import re
from typing import Optional, Tuple


# Common company → domain mappings for well-known companies
# Extend this list as needed
KNOWN_DOMAINS = {
    "google": "google.com",
    "microsoft": "microsoft.com",
    "amazon": "amazon.com",
    "meta": "meta.com",
    "facebook": "meta.com",
    "apple": "apple.com",
    "netflix": "netflix.com",
    "stripe": "stripe.com",
    "airbnb": "airbnb.com",
    "uber": "uber.com",
    "lyft": "lyft.com",
    "twitter": "twitter.com",
    "x": "x.com",
    "linkedin": "linkedin.com",
    "salesforce": "salesforce.com",
    "adobe": "adobe.com",
    "oracle": "oracle.com",
    "ibm": "ibm.com",
    "intel": "intel.com",
    "nvidia": "nvidia.com",
}


def infer_domain(company: str) -> str:
    """
    Converts a company name to its likely domain.
    
    Logic:
    1. Check known domains dict (case-insensitive)
    2. Otherwise: lowercase, remove special chars, append .com
       "OpenAI Technologies" → "openaitechnologies.com" (rough guess)
    
    Users should set company_domain manually for accuracy.
    """
    key = company.lower().strip()
    
    # Check known companies first
    if key in KNOWN_DOMAINS:
        return KNOWN_DOMAINS[key]
    
    # Generic: strip non-alphanumeric, lowercase, add .com
    clean = re.sub(r'[^a-z0-9]', '', key)
    return f"{clean}.com"


def generate_email_patterns(first: str, last: str, domain: str) -> list[dict]:
    """
    Generates the two most common corporate email patterns.
    Used as fallback when Hunter.io doesn't find a result.
    
    Returns list of dicts so we can track which pattern each email uses.
    """
    first = first.lower().strip()
    last = last.lower().strip()
    
    return [
        {
            "email": f"{first}.{last}@{domain}",
            "pattern": "firstname.lastname",
            "confidence": 0,  # 0 = guessed, not verified
        },
        {
            "email": f"{first[0]}.{last}@{domain}",
            "pattern": "f.lastname",
            "confidence": 0,
        },
    ]


async def find_email_hunter(
    first_name: str,
    last_name: str,
    domain: str,
    api_key: str,
) -> Tuple[Optional[str], Optional[str], int]:
    """
    Calls Hunter.io Email Finder API.
    
    Returns: (email, pattern, confidence)
      - email: found email address or None
      - pattern: which pattern Hunter used
      - confidence: 0-100 (Hunter's score) or 0 if not found
    
    Hunter.io API docs: https://hunter.io/api-documentation/v2#email-finder
    
    httpx is an async HTTP client (like requests but async-compatible).
    We use 'async with' so the connection is always properly closed.
    """
    url = "https://api.hunter.io/v2/email-finder"
    
    params = {
        "domain":     domain,
        "first_name": first_name,
        "last_name":  last_name,
        "api_key":    api_key,
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # timeout=10.0 → give up after 10 seconds (don't hang forever)
        response = await client.get(url, params=params)
        
        # 402 = Payment Required (free tier exhausted)
        if response.status_code == 402:
            raise ValueError("Hunter.io free tier limit reached (25/month). Check hunter.io dashboard.")
        
        # 4xx/5xx = something went wrong
        response.raise_for_status()
        
        data = response.json()
        
        # Hunter returns {"data": {"email": "...", "score": 90, ...}, "meta": {...}}
        email_data = data.get("data", {})
        email      = email_data.get("email")
        score      = email_data.get("score", 0)
        
        if not email:
            return None, None, 0
        
        # Extract which pattern Hunter used from the email itself
        # Compare against generated patterns to label it
        first_lower = first_name.lower()
        last_lower  = last_name.lower()
        
        if email.startswith(f"{first_lower}.{last_lower}@"):
            pattern = "firstname.lastname"
        elif email.startswith(f"{first_lower[0]}.{last_lower}@"):
            pattern = "f.lastname"
        elif email.startswith(f"{first_lower}@"):
            pattern = "firstname"
        else:
            pattern = "other"
        
        return email, pattern, score
