"""
Curato Proposal Intelligence — Lead Schemas

Pydantic schemas for the Lead Capture API.
"""

import re
from typing import Optional, Any

from pydantic import BaseModel, Field, field_validator, HttpUrl
import socket
import urllib.request
import urllib.error
from urllib.parse import urlparse

from app.config import get_settings


PERSONAL_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", 
    "live.com", "icloud.com", "proton.me", "protonmail.com", 
    "aol.com", "gmx.com", "yandex.com", "zoho.com"
}


class LeadCreate(BaseModel):
    """Schema for incoming lead capture submissions."""
    
    full_name: str = Field(..., min_length=2)
    company_name: str = Field(..., min_length=2)
    company_website: HttpUrl
    designation: str = Field(..., min_length=2, max_length=100)
    work_email: str
    phone_number: str
    captcha_token: str = Field(..., min_length=10)
    tool: str

    @field_validator("designation", mode="before")
    @classmethod
    def validate_designation(cls, v: Any) -> Any:
        if not isinstance(v, str) or len(v.strip()) < 2 or len(v.strip()) > 100:
            raise ValueError("INVALID_DESIGNATION|Please enter your designation.")
        return v.strip()
    
    @field_validator("work_email")
    @classmethod
    def validate_business_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v:
            raise ValueError("VALIDATION_ERROR|Invalid email format")
            
        domain = v.split("@")[1]
        if domain in PERSONAL_EMAIL_DOMAINS:
            raise ValueError("PERSONAL_EMAIL_NOT_ALLOWED|Please enter a valid business email address to continue.")
            
        return v
        
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        # Basic international phone number validation: Optional + followed by digits, spaces, hyphens, parentheses
        if not re.match(r"^\+?[\d\s\-\(\)]{7,20}$", v):
            raise ValueError("Invalid phone number format")
        return v
        
    @field_validator("tool")
    @classmethod
    def validate_tool(cls, v: str) -> str:
        settings = get_settings()
        if v not in settings.valid_tools_list:
            raise ValueError(f"VALIDATION_ERROR|Invalid AI tool: {v}")
        return v

    @field_validator("company_website", mode="before")
    @classmethod
    def normalize_website(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v.startswith(("http://", "https://")):
                v = "https://" + v
        return v

    @field_validator("company_website", mode="after")
    @classmethod
    def validate_website(cls, v: HttpUrl) -> HttpUrl:
        url_str = str(v)
        domain = v.host
        print(f"[Website Validation] Normalized URL: {url_str}, Domain: {domain}")
        if not domain:
            raise ValueError("INVALID_WEBSITE|Please enter a valid company website.")
            
        try:
            ip = socket.gethostbyname(domain)
            print(f"[Website Validation] DNS lookup successful: {domain} -> {ip}")
        except socket.gaierror as e:
            print(f"[Website Validation] DNS lookup failed for {domain}: {e}")
            raise ValueError("INVALID_WEBSITE|Please enter a valid company website.")
            
        try:
            req = urllib.request.Request(url_str, method="HEAD", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"[Website Validation] HEAD validation successful: {response.status} for {url_str}")
                return v
        except urllib.error.HTTPError as e:
            if e.code in [200, 301, 302, 303, 307, 308, 401, 403, 405]:
                print(f"[Website Validation] HEAD validation successful with code {e.code} for {url_str}")
                return v
            elif e.code not in [403, 405, 501, 503]: 
                # If it's 404 or something else definitive, reject immediately.
                print(f"[Website Validation] HEAD validation returned hard error {e.code} for {url_str}")
                raise ValueError("INVALID_WEBSITE|Please enter a valid company website.")
            # Otherwise (like 403 or 405), fallback to GET
        except Exception as e:
            print(f"[Website Validation] HEAD validation raised {e} for {url_str}, falling back to GET")
            
        # Fallback to GET
        try:
            req = urllib.request.Request(url_str, method="GET", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"[Website Validation] GET validation successful: {response.status} for {url_str}")
                return v
        except urllib.error.HTTPError as e:
            print(f"[Website Validation] GET validation returned error code {e.code} for {url_str}")
            if e.code not in [200, 301, 302, 303, 307, 308, 401, 403, 405]:
                raise ValueError("INVALID_WEBSITE|Please enter a valid company website.")
        except Exception as e:
            print(f"[Website Validation] GET validation failed with exception: {e}")
            raise ValueError("INVALID_WEBSITE|Please enter a valid company website.")
            
        return v


class LeadResponse(BaseModel):
    """Schema for successful lead submission response."""
    success: bool = True
    launch_url: str
