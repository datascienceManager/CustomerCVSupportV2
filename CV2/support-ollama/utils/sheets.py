"""
utils/sheets.py
Google Sheets integration for syncing conversations.
"""
import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_HEADERS = ["ID", "Session ID", "Role", "Content", "Language", "Mode", "Timestamp", "Synced At"]

def get_sheet_client():
    """Authenticate and return gspread client."""
    creds_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "credentials.json")
    if not os.path.exists(creds_file):
        raise FileNotFoundError(
            f"Google credentials file '{creds_file}' not found. "
            "Please follow setup instructions in README.md"
        )
    creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def get_or_create_worksheet(spreadsheet, title: str):
    """Get worksheet by title or create it."""
    try:
        ws = spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=title, rows=5000, cols=10)
        ws.append_row(SHEET_HEADERS)
    return ws

def sync_messages_to_sheet(messages: list) -> dict:
    """
    Sync a list of message dicts to Google Sheets.
    Returns a result dict with success/error info.
    """
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        return {"success": False, "error": "GOOGLE_SHEET_ID not set in .env"}

    try:
        client = get_sheet_client()
        spreadsheet = client.open_by_key(sheet_id)
        ws = get_or_create_worksheet(spreadsheet, "Conversations")

        # Get existing IDs to avoid duplicates
        existing = ws.col_values(1)  # Column A = ID
        existing_ids = set(existing[1:])  # Skip header

        rows_to_add = []
        synced_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for msg in messages:
            if str(msg["id"]) not in existing_ids:
                rows_to_add.append([
                    msg["id"],
                    msg["session_id"],
                    msg["role"],
                    msg["content"],
                    msg["language"],
                    msg["mode"],
                    msg["timestamp"],
                    synced_at
                ])

        if rows_to_add:
            ws.append_rows(rows_to_add, value_input_option="USER_ENTERED")

        return {"success": True, "synced": len(rows_to_add)}

    except FileNotFoundError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Google Sheets error: {str(e)}"}

def append_single_message(msg: dict) -> bool:
    """Append a single message to Google Sheets in real time."""
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        return False
    try:
        client = get_sheet_client()
        spreadsheet = client.open_by_key(sheet_id)
        ws = get_or_create_worksheet(spreadsheet, "Conversations")
        ws.append_row([
            msg.get("id", ""),
            msg.get("session_id", ""),
            msg.get("role", ""),
            msg.get("content", ""),
            msg.get("language", "en"),
            msg.get("mode", "chat"),
            msg.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ], value_input_option="USER_ENTERED")
        return True
    except Exception:
        return False
