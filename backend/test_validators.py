import unittest
from pydantic import ValidationError
from app.schemas.lead import LeadCreate

class TestWebsiteValidation(unittest.TestCase):

    def get_valid_lead_data(self):
        return {
            "full_name": "Test User",
            "company_name": "Test Corp",
            "work_email": "test@curato.ai",
            "phone_number": "+1234567890",
            "captcha_token": "1234567890",
            "tool": "proposal-intelligence",
            "designation": "Founder"
        }

    def test_existing_domain_accepted(self):
        data = self.get_valid_lead_data()
        data["company_website"] = "curato.ai"
        
        lead = LeadCreate(**data)
        self.assertIsNotNone(lead.company_website)

    def test_fake_domain_rejected(self):
        data = self.get_valid_lead_data()
        data["company_website"] = "this-domain-should-not-exist-123456789.com"
        
        with self.assertRaises(ValidationError) as context:
            LeadCreate(**data)
            
        self.assertIn("INVALID_WEBSITE", str(context.exception))

    def test_invalid_format_rejected(self):
        data = self.get_valid_lead_data()
        data["company_website"] = "abc"
        
        with self.assertRaises(ValidationError) as context:
            LeadCreate(**data)
            
        # Pydantic URL parsing might fail before custom validator, 
        # but it should still be a ValidationError.
        self.assertTrue("company_website" in str(context.exception))

if __name__ == '__main__':
    unittest.main()
