import smtplib
from email.message import EmailMessage
#import os
#from dotenv import load_dotenv
import streamlit as st
class EmailSender:
    """
    Secure email sender for sending emails via a Gmail account using SMTP.
    """
    def __init__(self):
        #load_dotenv()
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587        
        self.username = st.secrets["EMAIL_ADDRESS"]
        self.password = st.secrets["EMAIL_PASSWORD"]
        #self.username = os.getenv("EMAIL_ADDRESS")
        #self.password = os.getenv("EMAIL_PASSWORD")
        self.server = None

    def connect(self):
        try:
            self.server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            self.server.starttls()
            self.server.login(self.username, self.password)
            print("[✓] SMTP connection established and logged in.")
        except smtplib.SMTPException as e:
            print("[✗] SMTP connection failed:", str(e))
            self.server = None

    def send_email(self, to_address, subject, body, reply_to=None):
        if not self.server:
            print("[!] SMTP server not connected.")
            return False

        msg = EmailMessage()
        msg["From"] = self.username
        msg["To"] = to_address
        msg["Subject"] = subject
        if reply_to:
            msg["Reply-To"] = reply_to
        msg.set_content(body)

        try:
            self.server.send_message(msg)
            print(f"[✓] Email sent to {to_address}")
            return True
        except smtplib.SMTPException as e:
            print("[✗] Failed to send email:", str(e))
            return False

    def disconnect(self):
        if self.server:
            self.server.quit()
            print("[✓] SMTP connection closed.")
