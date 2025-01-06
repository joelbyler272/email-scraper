import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from loguru import logger

class Notifier:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', False)

    def send_notification(self, subject: str, body: str) -> bool:
        """Send email notification"""
        if not self.enabled:
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['smtp_username']
            msg['To'] = self.config['email']
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['smtp_username'], self.config['smtp_password'])
                server.send_message(msg)

            logger.info(f"Sent notification: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False

    def send_summary(self, processed_emails: List[Dict[str, Any]], errors: List[str] = None) -> bool:
        """Send summary of processed emails"""
        if not processed_emails and not errors:
            return False

        subject = f"Email Scraper Summary - {len(processed_emails)} Processed"
        body = f"Processed {len(processed_emails)} emails\n\n"

        if errors:
            body += f"Errors ({len(errors)}):\n"
            body += '\n'.join(f"- {error}" for error in errors)

        return self.send_notification(subject, body)