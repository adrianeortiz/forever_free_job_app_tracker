from googleapiclient.discovery import build


class GmailManager:
    def __init__(self, creds):
        self.service = build('gmail', 'v1', credentials = creds)
    
    def get_new_data(self):
        query = ('subject:'
                 '("application" OR "applying" '
                 'OR "job opportunity" OR "Thanks for applying") '
                 'after:2023/10/06 before:2025/01/01')
        results = (self.service.users().messages().list
                   (userId = 'me', q = query).execute())
        messages = results.get('messages', [])
        
        new_emails = []
        for message in messages:
            msg = (self.service.users().messages().get
                   (userId = 'me', id = message['id']).execute())
            headers = msg['payload']['headers']
            email_data = {
                'id': message['id'],
                'subject': next(
                    (header['value'] for header in headers if
                     header['name'] == 'Subject'), 'No Subject'
                    ),
                'date': next(
                    (header['value'] for header in headers if
                     header['name'] == 'Date'), 'No Date'
                    )
                }
            new_emails.append(email_data)
        
        return new_emails
