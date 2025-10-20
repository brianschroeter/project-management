"""Email receiver service for processing forwarded emails into tasks"""
from typing import Dict, Any, Optional
import email
from email.header import decode_header
from email import policy
from email.parser import BytesParser
import re
from datetime import datetime
from sqlalchemy.orm import Session

from backend.ai_engine import AIEngine
from backend.ticktick_client import TickTickClient
from backend.services.task_analyzer import TaskAnalyzer
from backend.services.gmail_oauth import GmailOAuth
from backend.services.outlook_oauth import OutlookOAuth
from backend.models import TaskInsight


class EmailReceiver:
    """Process emails and convert them to tasks"""

    def __init__(self, db: Session, ticktick_client: TickTickClient):
        self.db = db
        self.ticktick_client = ticktick_client
        self.ai_engine = AIEngine()
        self.task_analyzer = TaskAnalyzer(db, ticktick_client)

    def process_email(
        self,
        email_data: Dict[str, Any],
        user_id: int,
        email_source: str = "gmail"  # 'gmail' or 'outlook'
    ) -> Dict[str, Any]:
        """
        Process an incoming email and create a task

        Args:
            email_data: Dictionary containing email details
            user_id: ID of the user who owns this task
            email_source: Source of the email ('gmail' or 'outlook')

        Returns:
            Dictionary with created task and analysis
        """
        # Extract email fields
        subject = email_data.get('subject', 'Untitled')
        body = email_data.get('body', '')
        from_email = email_data.get('from', '')
        message_id = email_data.get('message_id', '')
        has_attachments = email_data.get('has_attachments', False)
        attachment_count = email_data.get('attachment_count', 0)

        # Use AI to parse email into task
        parsed = self.ai_engine.parse_email_to_task(
            email_subject=subject,
            email_body=body,
            email_from=from_email
        )

        # Create task in TickTick
        task_title = parsed.get('task_title', subject)
        task_description = parsed.get('task_description', body[:500])
        priority = self._convert_priority(parsed.get('suggested_priority', 'medium'))

        ticktick_task = self.ticktick_client.create_task(
            title=task_title,
            content=task_description,
            priority=priority
        )

        task_id = ticktick_task['id']

        # Generate email link
        email_link = self._generate_email_link(message_id, email_source)

        # Analyze task with AI
        analysis = self.task_analyzer.analyze_new_task(
            user_id=user_id,
            task_id=task_id,
            task_title=task_title,
            task_description=task_description,
            auto_create_subtasks=False  # Don't create subtasks from emails by default
        )

        # Update TaskInsight with email metadata
        insight = self.db.query(TaskInsight).filter(
            TaskInsight.ticktick_task_id == task_id
        ).first()

        if insight:
            insight.email_source = email_source
            insight.email_message_id = message_id
            insight.email_link = email_link
            insight.email_has_attachments = has_attachments
            insight.email_attachment_count = attachment_count
            insight.email_subject = subject
            insight.email_from = from_email
            insight.email_received_at = datetime.utcnow()

            # Add clarifying questions if needed
            if parsed.get('needs_clarification') and parsed.get('clarifying_questions'):
                insight.clarifying_questions = parsed['clarifying_questions']

            self.db.commit()

        return {
            "task": ticktick_task,
            "analysis": analysis,
            "email_metadata": {
                "source": email_source,
                "from": from_email,
                "subject": subject,
                "link": email_link,
                "has_attachments": has_attachments
            },
            "ai_parsing": parsed
        }

    @staticmethod
    def _convert_priority(priority_str: str) -> int:
        """Convert string priority to TickTick numeric priority"""
        priority_map = {
            'high': 5,
            'medium': 3,
            'low': 1
        }
        return priority_map.get(priority_str.lower(), 3)

    @staticmethod
    def _generate_email_link(message_id: str, email_source: str) -> str:
        """Generate link to view original email"""
        if email_source == 'gmail':
            return GmailOAuth.generate_email_link(message_id)
        elif email_source == 'outlook':
            return OutlookOAuth.generate_email_link(message_id)
        else:
            return ""

    @staticmethod
    def parse_email_raw(raw_email: bytes) -> Dict[str, Any]:
        """
        Parse raw email bytes into structured data

        Args:
            raw_email: Raw email bytes (RFC 822 format)

        Returns:
            Dictionary with parsed email fields
        """
        msg = BytesParser(policy=policy.default).parsebytes(raw_email)

        # Decode subject
        subject = msg.get('Subject', '')
        if subject:
            decoded_parts = decode_header(subject)
            subject = ''.join([
                part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
                for part, encoding in decoded_parts
            ])

        # Get sender
        from_email = msg.get('From', '')

        # Get message ID
        message_id = msg.get('Message-ID', '')

        # Get body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
                elif content_type == 'text/html' and not body:
                    # Fallback to HTML if no plain text
                    html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    body = EmailReceiver._html_to_text(html_body)
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

        # Count attachments
        attachment_count = 0
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    attachment_count += 1

        return {
            'subject': subject,
            'from': from_email,
            'body': body,
            'message_id': message_id,
            'has_attachments': attachment_count > 0,
            'attachment_count': attachment_count
        }

    @staticmethod
    def _html_to_text(html: str) -> str:
        """Convert HTML to plain text (basic implementation)"""
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML tags
        html = re.sub(r'<[^>]+>', '', html)

        # Decode HTML entities
        html = html.replace('&nbsp;', ' ')
        html = html.replace('&lt;', '<')
        html = html.replace('&gt;', '>')
        html = html.replace('&amp;', '&')
        html = html.replace('&quot;', '"')

        # Clean up whitespace
        html = re.sub(r'\s+', ' ', html)

        return html.strip()
