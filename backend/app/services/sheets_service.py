"""
Curato Proposal Intelligence — Google Sheets Service

Appends leads to a configured Google Sheet.
"""

import json
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

import gspread
from google.oauth2.service_account import Credentials

from app.config import Settings
from app.schemas.lead import LeadCreate


class GoogleSheetsService:
    """Appends data to Google Sheets."""

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    def __init__(self, settings: Settings):
        self.settings = settings
        self._executor = ThreadPoolExecutor(max_workers=3)

    def _get_client(self) -> gspread.Client | None:
        """Authenticate and return the gspread client."""
        if not self.settings.google_sheets_credentials_json or not self.settings.google_sheets_spreadsheet_id:
            print("[WARN] Google Sheets credentials or spreadsheet ID not configured. Bypassing sheets append.")
            return None

        try:
            creds_dict = json.loads(self.settings.google_sheets_credentials_json)
            credentials = Credentials.from_service_account_info(
                creds_dict, scopes=self.SCOPES
            )
            return gspread.authorize(credentials)
        except Exception as e:
            print(f"[ERROR] Failed to authenticate with Google Sheets: {e}")
            return None

    def _append_sync(self, lead: LeadCreate, timestamp: str) -> None:
        """Synchronous append operation (to be run in thread pool)."""
        client = self._get_client()
        if not client:
            return

        try:
            spreadsheet = client.open_by_key(self.settings.google_sheets_spreadsheet_id)
            
            if self.settings.google_sheets_worksheet_name:
                worksheet = spreadsheet.worksheet(self.settings.google_sheets_worksheet_name)
            else:
                worksheet = spreadsheet.sheet1

            # Columns: Timestamp | Full Name | Company Name | Company Website | Work Email | Phone Number | AI Tool
            row = [
                timestamp,
                lead.full_name,
                lead.company_name,
                str(lead.company_website),
                lead.work_email,
                lead.phone_number,
                lead.tool
            ]
            
            worksheet.append_row(row, value_input_option="USER_ENTERED")
            print(f"  [OK] Appended lead {lead.work_email} to Google Sheets")
            
        except Exception as e:
            print(f"[ERROR] Failed to append to Google Sheets: {e}")

    async def append_lead(self, lead: LeadCreate) -> None:
        """
        Append the lead data to the configured Google Sheet asynchronously.
        Does not overwrite existing rows.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        loop = asyncio.get_running_loop()
        # Run the blocking gspread network call in a thread pool
        await loop.run_in_executor(self._executor, self._append_sync, lead, timestamp)
