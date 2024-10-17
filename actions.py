from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64
import datetime

class GmailActions:
    def __init__(self, gmail_service):
        self.service = gmail_service

    def list_messages(self, max_results=100, query=None):
        try:
            response = self.service.users().messages().list(userId='me', maxResults=max_results, q=query).execute()
            messages = response.get('messages', [])
            
            detailed_messages = []
            for message in messages:
                msg_details = self.get_message(message['id'])
                detailed_messages.append(msg_details)
            
            return detailed_messages
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    def get_message(self, message_id):
        try:
            message = self.service.users().messages().get(userId='me', id=message_id, format='full').execute()
            
            headers = message['payload']['headers']
            subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
            sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown Sender')
            
            if 'parts' in message['payload']:
                parts = message['payload']['parts']
                body = self.get_body_from_parts(parts)
            else:
                body = self.decode_body(message['payload']['body'])
            
            return {
                'id': message['id'],
                'threadId': message['threadId'],
                'subject': subject,
                'sender': sender,
                'body': body
            }
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def get_body_from_parts(self, parts):
        for part in parts:
            if part['mimeType'] == 'text/plain':
                return self.decode_body(part['body'])
            elif 'parts' in part:
                return self.get_body_from_parts(part['parts'])
        return ''

    def decode_body(self, body):
        if 'data' in body:
            return base64.urlsafe_b64decode(body['data']).decode('utf-8')
        return ''

    def send_message(self, to, subject, body, user_id='me'):
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            message = self.service.users().messages().send(userId=user_id, body={'raw': raw_message}).execute()
            return message
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def delete_message(self, message_id, user_id='me'):
        try:
            self.service.users().messages().delete(userId=user_id, id=message_id).execute()
            return True
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False

class CalendarActions:
    def __init__(self, calendar_service):
        self.service = calendar_service

    def list_events(self, calendar_id='primary', max_results=100, time_min=None):
        try:
            if not time_min:
                time_min = datetime.datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(calendarId=calendar_id, timeMin=time_min,
                                                       maxResults=max_results, singleEvents=True,
                                                       orderBy='startTime').execute()
            return events_result.get('items', [])
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def create_event(self, summary, start_time, end_time, description=None, location=None, calendar_id='primary'):
        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
        }

        try:
            event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
            return event
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def update_event(self, event_id, summary=None, start_time=None, end_time=None, description=None, location=None, calendar_id='primary'):
        try:
            event = self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            
            if summary:
                event['summary'] = summary
            if start_time:
                event['start']['dateTime'] = start_time
            if end_time:
                event['end']['dateTime'] = end_time
            if description:
                event['description'] = description
            if location:
                event['location'] = location

            updated_event = self.service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
            return updated_event
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def delete_event(self, event_id, calendar_id='primary'):
        try:
            self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            return True
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False
