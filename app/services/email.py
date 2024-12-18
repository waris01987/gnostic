from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib

from app.config import settings


class EmailService:
    @staticmethod
    async def send(recipient_emails: list[str], subject: str, body: str):
        html_message = MIMEMultipart("alternative")
        html_message["Subject"] = subject
        html_message["From"] = settings.SENDER_EMAIL
        html_message["To"] = ", ".join(recipient_emails)

        html_message.attach(MIMEText(body, "html"))

        server = aiosmtplib.SMTP(hostname="smtp.gmail.com", port=465, use_tls=True)
        await server.connect(
            username=settings.SENDER_EMAIL, password=settings.SENDER_PASSWORD
        )
        await server.sendmail(
            settings.SENDER_EMAIL, recipient_emails, html_message.as_string()
        )
        await server.quit()
