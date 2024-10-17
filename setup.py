import os
# from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
# from config.integration.google import GoogleConfig
# from config.conf_type import ConfType
# from utils.initialization import configuration


def setup_google_auth():
    # config: GoogleConfig = configuration.get_conf(ConfType.GOOGLE)
    scopes = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
    ]

    # Check if we already have valid credentials
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", scopes)
        if creds and creds.valid:
            return creds

    # If not, start the OAuth flow
    # flow = Flow.from_client_config(
    #     config.oauth_client_config,
    #     config.scopes,
    #     redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    # )

    # auth_url, _ = flow.authorization_url(prompt='consent')
    # print(f"Please visit this URL to authorize the application: {auth_url}")

    # Get the authorization code from the user
    # code = input("Enter the authorization code: ")

    # Exchange the authorization code for credentials
    # flow.fetch_token(code=code)
    # creds = flow.credentials

    # Save the credentials for future use
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    return creds


def initialize_services():
    creds = setup_google_auth()
    gmail_service = build("gmail", "v1", credentials=creds)
    calendar_service = build("calendar", "v3", credentials=creds)
    return gmail_service, calendar_service
