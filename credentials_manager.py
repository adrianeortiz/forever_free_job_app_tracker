import os
from google_auth_oauthlib.flow import InstalledAppFlow


class CredentialsManager:
    def __init__(self):
        self.creds = None
        self.creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets',
                       'https://www.googleapis.com/auth/gmail.readonly']
        self.creds = None
    
    def get_credentials(self, getenv):
        if not self.creds or not self.creds.valid:
            self.creds = InstalledAppFlow.from_client_secrets_file(
                self.creds_path, self.scopes
                ).run_local_server(port = 8080)
        return self.creds
