from dotenv import load_dotenv
load_dotenv()
from credentials_manager import CredentialsManager
from google_sheet_manager import GoogleSheetManager
from gmail_manager import GmailManager
import os
import json
from datetime import datetime
from dateutil import parser
from dateutil.tz import tzutc
import pytz


def calculate_days_since(date_str):
    application_date = parser.parse(date_str)
    # Convert application date to UTC
    application_date = application_date.astimezone(tzutc())
    now_utc = datetime.now(tzutc())
    return (now_utc - application_date).days

def save_processed_emails(processed_emails_file, processed_emails):
    with open(processed_emails_file, 'w') as file:
        json.dump(processed_emails, file)

def load_processed_emails(processed_emails_file):
    try:
        with open(processed_emails_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
#
# def calculate_days_since(date_str):
#     date_format = "%a, %d %b %Y %H:%M:%S %z"
#     application_date = datetime.strptime(date_str, date_format)
#     now_utc = datetime.now(pytz.utc)
#     return (now_utc - application_date).days

def main():
    creds_manager = CredentialsManager()
    creds = creds_manager.get_credentials()

    sheet_manager = GoogleSheetManager(creds, os.getenv('GOOGLE_SHEET_ID'))
    gmail_manager = GmailManager(creds)

    processed_emails_file = os.getenv('PROCESSED_EMAILS_PATH')
    processed_emails = load_processed_emails(processed_emails_file)

# Fetch the current data from the sheet to determine where to start appending
    current_data = sheet_manager.read_sheet("Sheet1!A2:F")
    last_row = len(current_data) + 2  # Assuming header is in the first row

    # Fetch new emails
    new_emails = gmail_manager.get_new_data()

    # Prepare new data for the sheet
    new_data = []
    for email in new_emails:
        if email['id'] not in processed_emails:
            days_since = calculate_days_since(email['date'])
            # Prepare the rest of the data as per your Google Sheet's columns
            # Make sure the indexes align with the columns in your sheet
            email_data = [
                email['subject'],  # Column A: Subject
                email['date'],     # Column B: Date
                days_since,      # Column C: Days since application submitted
                '',             # Column D: Status (check mark means rejected)
                '',                # Column E: Interview Dates
                ''                 # Column F: Notes/Comments
            ]
            new_data.append(email_data)
            processed_emails.append(email['id'])

    # Update the Google Sheet with new data
    if new_data:
        append_range = f"Sheet1!A{last_row}:F"
        sheet_manager.append_to_sheet(append_range, new_data)
        save_processed_emails(processed_emails_file, processed_emails)

if __name__ == "__main__":
    main()
