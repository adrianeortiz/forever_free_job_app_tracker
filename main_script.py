import os
import json
from datetime import datetime
from dateutil import parser
from dotenv import load_dotenv
from credentials_manager import CredentialsManager
from google_sheet_manager import GoogleSheetManager
from gmail_manager import GmailManager

load_dotenv()


def calculate_days_since(date_str):
    application_date = parser.parse(date_str)
    now_utc = datetime.now(application_date.tzinfo)
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


def remove_duplicate_ids(processed_emails_file):
    with open(processed_emails_file, 'r') as file:
        processed_emails = json.load(file)
    
    unique_emails = list(set(processed_emails))
    
    with open(processed_emails_file, 'w') as file:
        json.dump(unique_emails, file)


def parse_date_with_timezone(date_str):
    try:
        return parser.parse(date_str)
    except ValueError:
        # If there's a value error, you may need to extend this part to
        # handle different date formats
        return parser.parse(date_str, ignoretz = True).replace(
            tzinfo = datetime.utcnow().tzinfo
            )


def update_days_since_application(sheet_manager, sheet_range):
    current_data = sheet_manager.read_sheet(sheet_range)
    updated_data = []
    
    for row in current_data:
        if row and len(
                row
                ) > 1:  # Check if the row is not empty and has at least two
            # columns
            try:
                date_str = row[1]  # Assuming the date is in the second column
                date_obj = parse_date_with_timezone(date_str)
                days_since = calculate_days_since(
                    date_obj.strftime("%a, %d %b %Y %H:%M:%S %z")
                    )
                updated_data.append([days_since])
            except Exception as e:
                print(f"Error parsing date {date_str}: {e}")
                updated_data.append(["Error"])
    
    # Write the updated "Days since" back to the sheet in column C
    sheet_manager.write_to_column(
        sheet_range.split('!')[0] + "!C2:C", updated_data
        )


def main():
    creds_manager = CredentialsManager()
    creds = creds_manager.get_credentials(os.getenv('GOOGLE_CREDENTIALS_PATH'))
    
    processed_emails_file = os.getenv('PROCESSED_EMAILS_PATH')
    remove_duplicate_ids(processed_emails_file)
    processed_emails = set(load_processed_emails(processed_emails_file))
    
    sheet_manager = GoogleSheetManager(creds, os.getenv('GOOGLE_SHEET_ID'))
    gmail_manager = GmailManager(creds)
    
    current_data = sheet_manager.read_sheet("Sheet1!A2:F")
    new_emails = gmail_manager.get_new_data()
    
    new_data = []
    for email in new_emails:
        if email['id'] not in processed_emails:
            date_obj = parse_date_with_timezone(email['date'])
            days_since = calculate_days_since(
                date_obj.strftime("%a, %d %b %Y %H:%M:%S %z")
                )
            email_data = [
                email['subject'], email['date'], days_since, '', '', ''
                ]
            new_data.append(email_data)
            processed_emails.add(email['id'])
    
    if new_data:
        last_row = len(current_data) + 2
        append_range = f"Sheet1!A{last_row}:F"
        sheet_manager.append_to_sheet(append_range, new_data)
        save_processed_emails(processed_emails_file, list(processed_emails))
    
    update_days_since_application(sheet_manager, "Sheet1!A2:F")


if __name__ == "__main__":
    main()
