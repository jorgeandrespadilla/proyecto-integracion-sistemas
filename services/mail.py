from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from config import MailConfig

class MailService:
    
    def send_email(self, dest_email: str, subject: str, html_content: str):
        message = Mail(
            from_email=MailConfig.SENDER_EMAIL,
            to_emails=dest_email,
            subject=subject,
            html_content=html_content
        )
        sg = SendGridAPIClient(MailConfig.SENDGRID_API_KEY)
        response = sg.send(message)
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)