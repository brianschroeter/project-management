"""Outlook/Microsoft Graph OAuth and email link generation"""
from typing import Optional, Dict, Any
import msal
import requests


class OutlookOAuth:
    """Handle Outlook OAuth flow and email operations via Microsoft Graph API"""

    # Microsoft Graph API scopes
    SCOPES = [
        'https://graph.microsoft.com/Mail.Read',
        'https://graph.microsoft.com/User.Read'
    ]

    # Microsoft Graph API endpoint
    GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, tenant_id: str = "common"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.tenant_id = tenant_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"

        self.msal_app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority
        )

    def get_authorization_url(self, state: str) -> str:
        """
        Get the OAuth authorization URL
        User should be redirected to this URL to authorize
        """
        auth_url = self.msal_app.get_authorization_request_url(
            scopes=self.SCOPES,
            state=state,
            redirect_uri=self.redirect_uri
        )
        return auth_url

    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        Returns token data including access_token and refresh_token
        """
        result = self.msal_app.acquire_token_by_authorization_code(
            code=code,
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )

        if "error" in result:
            raise Exception(f"OAuth error: {result.get('error_description', result['error'])}")

        return {
            "access_token": result['access_token'],
            "refresh_token": result.get('refresh_token'),
            "token_expiry": result.get('expires_in'),  # Seconds until expiry
            "email": self._get_user_email(result['access_token'])
        }

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired access token"""
        result = self.msal_app.acquire_token_by_refresh_token(
            refresh_token=refresh_token,
            scopes=self.SCOPES
        )

        if "error" in result:
            raise Exception(f"Token refresh error: {result.get('error_description', result['error'])}")

        return {
            "access_token": result['access_token'],
            "token_expiry": result.get('expires_in')
        }

    def _get_user_email(self, access_token: str) -> Optional[str]:
        """Get the user's email address from Microsoft Graph"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(
                f'{self.GRAPH_API_ENDPOINT}/me',
                headers=headers
            )
            response.raise_for_status()
            user_data = response.json()
            return user_data.get('mail') or user_data.get('userPrincipalName')
        except Exception as e:
            print(f"Error getting user email: {e}")
            return None

    @staticmethod
    def generate_email_link(message_id: str, folder_id: str = "inbox") -> str:
        """
        Generate a direct link to view an email in Outlook web interface

        Args:
            message_id: Outlook/Exchange message ID
            folder_id: Folder name (default: inbox)

        Returns:
            Direct link to the email in Outlook
        """
        # Outlook web URL format
        # https://outlook.office.com/mail/inbox/id/{message_id}
        return f"https://outlook.office.com/mail/{folder_id}/id/{message_id}"

    def get_message_details(self, access_token: str, message_id: str) -> Dict[str, Any]:
        """
        Get details about a specific email message

        Args:
            access_token: Valid Microsoft Graph access token
            message_id: Outlook message ID

        Returns:
            Dictionary with message details (subject, from, date, snippet, etc.)
        """
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            response = requests.get(
                f'{self.GRAPH_API_ENDPOINT}/me/messages/{message_id}',
                headers=headers,
                params={'$select': 'subject,from,receivedDateTime,bodyPreview,hasAttachments,parentFolderId'}
            )
            response.raise_for_status()
            message = response.json()

            return {
                "id": message['id'],
                "subject": message.get('subject', ''),
                "from": message.get('from', {}).get('emailAddress', {}).get('address', ''),
                "date": message.get('receivedDateTime', ''),
                "snippet": message.get('bodyPreview', ''),
                "has_attachments": message.get('hasAttachments', False),
                "link": self.generate_email_link(message['id'])
            }
        except Exception as e:
            print(f"Error getting message details: {e}")
            return {
                "error": str(e),
                "link": self.generate_email_link(message_id)
            }

    def list_recent_messages(self, access_token: str, limit: int = 10) -> list:
        """
        List recent messages from inbox
        Useful for testing and debugging
        """
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            response = requests.get(
                f'{self.GRAPH_API_ENDPOINT}/me/messages',
                headers=headers,
                params={
                    '$top': limit,
                    '$select': 'id,subject,from,receivedDateTime',
                    '$orderby': 'receivedDateTime DESC'
                }
            )
            response.raise_for_status()
            return response.json().get('value', [])
        except Exception as e:
            print(f"Error listing messages: {e}")
            return []
