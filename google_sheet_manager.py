from googleapiclient.discovery import build
class GoogleSheetManager:
    def __init__(self, creds, sheet_id):
        self.service = build('sheets', 'v4', credentials=creds)
        self.sheet_id = sheet_id

    def read_sheet(self, range_name):
        # Read data from the specified range in the sheet
        result = (self.service.spreadsheets().values().get
                  (spreadsheetId=self.sheet_id, range=range_name).execute())
        return result.get('values', [])

    def append_to_sheet(self, range_name, values):
        # Append data to the sheet
        body = {'values': values}
        result = self.service.spreadsheets().values().append(
            spreadsheetId=self.sheet_id, range=range_name,
            valueInputOption='USER_ENTERED', body=body,
            insertDataOption='INSERT_ROWS'
        ).execute()
        return result
