import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Union
import os

from wdev.notifiers import Notifier


class EmailNotifier(Notifier):
    """邮件通知器"""

    def __init__(self, recipients: Union[str, list],
                 smtp_host: str = None,
                 smtp_port: int = None,
                 smtp_user: str = None,
                 smtp_password: str = None):
        super().__init__("email")
        self.recipients = recipients if isinstance(recipients, list) else [recipients]
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")

    def notify(self, subject: str, message: str, **kwargs) -> bool:
        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_user
            msg["To"] = ", ".join(self.recipients)
            msg["Subject"] = subject

            msg.attach(MIMEText(message, "plain"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False