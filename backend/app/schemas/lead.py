"""
Curato Proposal Intelligence — Lead Schemas

Pydantic schemas for the Lead Capture API.
"""

import re
from typing import Optional

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
    work_email: str
    phone_number: str
    captcha_token: str = Field(..., min_length=10)
    tool: str
    
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
        if not domain:
            raise ValueError("INVALID_WEBSITE|Please enter a valid company website.")
            
        try:
            socket.gethostbyname(domain)
        except socket.gaierror:
            raise ValueError("INVALID_WEBSITE|Please enter a valid company website.")
            
        try:
            req = urllib.request.Request(url_str, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as response:
                pass
        except urllib.error.HTTPError as e:
            if e.code not in [200, 301, 302, 303, 307, 308, 401, 403, 405]:
                # Other HTTP errors might indicate the site is broken, but the domain exists. 
                # We'll allow it to pass since DNS resolved, but if you want strict checking, 
                # you can raise the ValueError here.
                pass
        except Exception:
            raise ValueError("INVALID_WEBSITE|Please enter a valid company website.")
            
        return v


class LeadResponse(BaseModel):
    """Schema for successful lead submission response."""
    success: bool = True
    launch_url: str
