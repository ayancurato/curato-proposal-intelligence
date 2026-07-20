"""
Curato Proposal Intelligence — Lead Schemas

Pydantic schemas for the Lead Capture API.
"""

import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator, HttpUrl

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
            raise ValueError("Invalid email format")
            
        domain = v.split("@")[1]
        if domain in PERSONAL_EMAIL_DOMAINS:
            raise ValueError("Please use your company email address.")
            
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
            raise ValueError(f"Invalid AI tool: {v}")
        return v


class LeadResponse(BaseModel):
    """Schema for successful lead submission response."""
    success: bool = True
    launch_url: str
