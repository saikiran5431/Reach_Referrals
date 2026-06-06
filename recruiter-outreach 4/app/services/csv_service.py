"""
app/services/csv_service.py — WHY IT EXISTS
=============================================
Handles bulk import of recruiters from:
  1. Direct CSV upload (any CSV with the right columns)
  2. Google Sheets exported as CSV (File → Download → CSV)

Google Sheets public URL import:
  If your sheet is published to web, we can fetch it directly.
  Share → Publish to web → CSV → copy link → POST /recruiters/import-gsheet

Expected CSV columns (case-insensitive):
  Required: first_name (or first), last_name (or last), company
  Optional: title, linkedin_url, company_domain

The parser is lenient — it tries several column name variations.
"""

import csv
import io
from typing import List
import httpx

from app.models.recruiter import RecruiterCreate
from app.services.hunter_service import infer_domain


# Maps common column name variations to our canonical names
# Keys = what we look for (lowercase), Values = our field name
COLUMN_ALIASES = {
    # first_name variations
    "first_name": "first_name",
    "first":      "first_name",
    "firstname":  "first_name",
    "fname":      "first_name",
    "given_name": "first_name",
    
    # last_name variations
    "last_name":  "last_name",
    "last":       "last_name",
    "lastname":   "last_name",
    "lname":      "last_name",
    "surname":    "last_name",
    "family_name": "last_name",
    
    # company variations
    "company":        "company",
    "company_name":   "company",
    "organization":   "company",
    "org":            "company",
    "employer":       "company",
    
    # optional fields
    "title":          "title",
    "job_title":      "title",
    "position":       "title",
    "role":           "title",
    "linkedin_url":   "linkedin_url",
    "linkedin":       "linkedin_url",
    "profile":        "linkedin_url",
    "company_domain": "company_domain",
    "domain":         "company_domain",
    "email_domain":   "company_domain",
}


def parse_csv_content(content: str) -> List[RecruiterCreate]:
    """
    Parses CSV string into a list of RecruiterCreate objects.
    
    Steps:
    1. Read CSV headers
    2. Map headers to canonical field names via COLUMN_ALIASES
    3. Parse each row, skipping blank rows
    4. Infer company_domain if not provided
    
    Returns list of valid RecruiterCreate objects.
    Raises ValueError if required columns are missing.
    """
    reader = csv.DictReader(io.StringIO(content.strip()))
    
    if not reader.fieldnames:
        raise ValueError("CSV file appears to be empty or has no headers.")
    
    # Build mapping: original_header → canonical_field_name
    # e.g., "First Name" → "first_name"
    header_map = {}
    for original_header in reader.fieldnames:
        normalized = original_header.strip().lower().replace(" ", "_").replace("-", "_")
        if normalized in COLUMN_ALIASES:
            header_map[original_header] = COLUMN_ALIASES[normalized]
    
    # Check required fields are present
    mapped_fields = set(header_map.values())
    required = {"first_name", "last_name", "company"}
    missing = required - mapped_fields
    if missing:
        raise ValueError(
            f"CSV missing required columns: {missing}. "
            f"Found columns: {list(reader.fieldnames)}. "
            f"Required: first_name (or 'first'), last_name (or 'last'), company."
        )
    
    recruiters = []
    
    for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is headers
        # Skip completely blank rows
        if not any(v.strip() for v in row.values()):
            continue
        
        # Extract mapped fields from this row
        data = {}
        for original_header, canonical_name in header_map.items():
            value = row.get(original_header, "").strip()
            if value:
                data[canonical_name] = value
        
        # Validate required fields have values
        if not data.get("first_name") or not data.get("last_name") or not data.get("company"):
            # Skip rows with missing required data (partial rows)
            continue
        
        # Infer domain if not provided
        if not data.get("company_domain"):
            data["company_domain"] = infer_domain(data["company"])
        
        try:
            recruiter = RecruiterCreate(**data)
            recruiters.append(recruiter)
        except Exception as e:
            # Log bad rows but don't fail the whole import
            print(f"Row {row_num} skipped due to error: {e} — Data: {data}")
    
    if not recruiters:
        raise ValueError("No valid recruiter rows found in the CSV.")
    
    return recruiters


async def fetch_gsheet_csv(published_url: str) -> str:
    """
    Fetches a Google Sheet that has been published to web as CSV.
    
    How to publish a Google Sheet:
    1. File → Share → Publish to web
    2. Select "Comma-separated values (.csv)"
    3. Click Publish → copy the URL
    4. Paste that URL into POST /recruiters/import-gsheet
    
    The URL looks like:
    https://docs.google.com/spreadsheets/d/SHEET_ID/pub?output=csv
    """
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        response = await client.get(published_url)
        
        if response.status_code != 200:
            raise ValueError(
                f"Could not fetch Google Sheet (status {response.status_code}). "
                "Make sure the sheet is published to web as CSV."
            )
        
        content_type = response.headers.get("content-type", "")
        if "html" in content_type.lower() and "csv" not in content_type.lower():
            raise ValueError(
                "URL returned HTML, not CSV. "
                "Make sure you're using the 'Publish to web' CSV link, "
                "not a regular Google Sheets share link."
            )
        
        return response.text
