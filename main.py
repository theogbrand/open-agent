from setup import initialize_services
from actions import GmailActions, CalendarActions
import json

def main():
    # Initialize services
    gmail_service, calendar_service = initialize_services()
    gmail_actions = GmailActions(gmail_service)
    calendar_actions = CalendarActions(calendar_service)

    while True:
        # Get user input
        action_input = input("Enter an action (or 'quit' to exit): ")
        
        if action_input.lower() == 'quit':
            break

        try:
            # Parse the input as JSON
            action_data = json.loads(action_input)
            action = action_data.get('action')

            if action.startswith('gmail_'):
                handle_gmail_action(gmail_actions, action, action_data)
            elif action.startswith('calendar_'):
                handle_calendar_action(calendar_actions, action, action_data)
            else:
                print(f"Unknown action: {action}")
        except json.JSONDecodeError:
            print("Invalid input. Please enter a valid JSON string.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

def handle_gmail_action(gmail_actions, action, action_data):
    if action == 'gmail_list_messages':
        messages = gmail_actions.list_messages(
            max_results=action_data.get('max_results', 100),
            query=action_data.get('query')
        )
        for message in messages:
            print(f"ID: {message['id']}")
            print(f"Thread ID: {message['threadId']}")
            print(f"Subject: {message['subject']}")
            print(f"From: {message['sender']}")
            print(f"Body: {message['body'][:100]}...")  # Print first 100 characters of the body
            print("-" * 50)
    elif action == 'gmail_get_message':
        message = gmail_actions.get_message(action_data['message_id'])
        print(json.dumps(message, indent=2))
    elif action == 'gmail_send_message':
        result = gmail_actions.send_message(
            action_data['to'],
            action_data['subject'],
            action_data['body']
        )
        print(json.dumps(result, indent=2))
    elif action == 'gmail_delete_message':
        result = gmail_actions.delete_message(action_data['message_id'])
        print(f"Message deleted: {result}")
    else:
        print(f"Unknown Gmail action: {action}")

def handle_calendar_action(calendar_actions, action, action_data):
    if action == 'calendar_list_events':
        events = calendar_actions.list_events(
            max_results=action_data.get('max_results', 100),
            time_min=action_data.get('time_min')
        )
        print(json.dumps(events, indent=2))
    elif action == 'calendar_create_event':
        event = calendar_actions.create_event(
            action_data['summary'],
            action_data['start_time'],
            action_data['end_time'],
            description=action_data.get('description'),
            location=action_data.get('location')
        )
        print(json.dumps(event, indent=2))
    elif action == 'calendar_update_event':
        updated_event = calendar_actions.update_event(
            action_data['event_id'],
            summary=action_data.get('summary'),
            start_time=action_data.get('start_time'),
            end_time=action_data.get('end_time'),
            description=action_data.get('description'),
            location=action_data.get('location')
        )
        print(json.dumps(updated_event, indent=2))
    elif action == 'calendar_delete_event':
        result = calendar_actions.delete_event(action_data['event_id'])
        print(f"Event deleted: {result}")
    else:
        print(f"Unknown Calendar action: {action}")

if __name__ == "__main__":
    main()
