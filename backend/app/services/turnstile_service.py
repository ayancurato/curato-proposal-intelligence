"""
Curato Proposal Intelligence — Turnstile Service

Handles Cloudflare Turnstile CAPTCHA verification.
"""

import httpx

from app.config import Settings


class TurnstileService:
    """Verifies Cloudflare Turnstile tokens."""

    VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

    def __init__(self, settings: Settings):
        self.settings = settings

    async def verify_token(self, token: str, remote_ip: str | None = None) -> bool:
        """
        Verify the Turnstile token with Cloudflare.
        
        Args:
            token: The captcha_token submitted by the client
            remote_ip: Optional client IP address
            
        Returns:
            bool: True if verification succeeds, False otherwise
        """
        if not self.settings.turnstile_secret_key:
            # If no secret key is configured, bypass verification (useful for local dev)
            print("⚠ Turnstile secret key not configured, bypassing verification.")
            return True

        payload = {
            "secret": self.settings.turnstile_secret_key,
            "response": token
        }
        
        if remote_ip:
            payload["remoteip"] = remote_ip

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.VERIFY_URL, data=payload)
                response.raise_for_status()
                data = response.json()
                
                if data.get("success"):
                    return True
                
                print(f"✖ Turnstile verification failed: {data.get('error-codes', [])}")
                return False
                
            except Exception as e:
                print(f"✖ Turnstile service error: {e}")
                return False
