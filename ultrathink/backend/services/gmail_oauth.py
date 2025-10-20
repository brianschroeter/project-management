"""Gmail OAuth and email link generation"""
from typing import Optional, Dict, Any
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os


class GmailOAuth:
    """Handle Gmail OAuth flow and email operations"""

    # OAuth scopes needed
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.metadata'
    ]

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_authorization_url(self, state: str) -> str:
        """
        Get the OAuth authorization URL
        User should be redirected to this URL to authorize
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )

        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state
        )

        return authorization_url

    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        Returns token data including access_token and refresh_token
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_expiry": credentials.expiry.isoformat() if credentials.expiry else None,
            "email": self._get_user_email(credentials)
        }

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired access token"""
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret
        )

        credentials.refresh()

        return {
            "access_token": credentials.token,
            "token_expiry": credentials.expiry.isoformat() if credentials.expiry else None
        }

    def _get_user_email(self, credentials: Credentials) -> Optional[str]:
        """Get the user's email address from their Gmail account"""
        try:
            service = build('gmail', 'v1', credentials=credentials)
            profile = service.users().getProfile(userId='me').execute()
            return profile.get('emailAddress')
        except Exception as e:
            print(f"Error getting user email: {e}")
            return None

    @staticmethod
    def generate_email_link(message_id: str) -> str:
        """
        Generate a direct link to view an email in Gmail web interface

        Args:
            message_id: Gmail message ID (format: thread_id/message_id or just message_id)

        Returns:
            Direct link to the email in Gmail
        """
        # Gmail web URL format
        # https://mail.google.com/mail/u/0/#inbox/message_id
        return f"https://mail.google.com/mail/u/0/#inbox/{message_id}"

    def get_message_details(self, access_token: str, message_id: str) -> Dict[str, Any]:
        """
        Get details about a specific email message

        Args:
            access_token: Valid Gmail access token
            message_id: Gmail message ID

        Returns:
            Dictionary with message details (subject, from, date, snippet, etc.)
        """
        credentials = Credentials(token=access_token)
        service = build('gmail', 'v1', credentials=credentials)

        try:
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()

            headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}

            return {
                "id": message['id'],
                "thread_id": message['threadId'],
                "subject": headers.get('Subject', ''),
                "from": headers.get('From', ''),
                "date": headers.get('Date', ''),
                "snippet": message.get('snippet', ''),
                "has_attachments": len(message.get('payload', {}).get('parts', [])) > 1,
                "link": self.generate_email_link(message['id'])
            }
        except Exception as e:
            print(f"Error getting message details: {e}")
            return {
                "error": str(e),
                "link": self.generate_email_link(message_id)
            }
