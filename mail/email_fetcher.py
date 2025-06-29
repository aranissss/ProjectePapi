import imaplib
import email
from email.header import decode_header
import streamlit as st
#import os
#from dotenv import load_dotenv

class EmailFetcher:
    """
    Secure email fetcher for reading emails from a Gmail inbox using IMAP.
    """
    def __init__(self):
        #load_dotenv()
        self.imap_server = "imap.gmail.com"        
        self.username = st.secrets["EMAIL_ADDRESS"]
        self.password = st.secrets["EMAIL_PASSWORD"]
        #self.username = os.getenv("EMAIL_ADDRESS")
        #self.password = os.getenv("EMAIL_PASSWORD")
        self.mail = None
        self.emails= []

    def connect(self):
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.username, self.password)
            print("[✓] Logged in successfully.")
        except imaplib.IMAP4.error as e:
            print("[✗] Login failed:", str(e))
            self.mail = None

    def fetch_latest_email(self, limit=10):
        if not self.mail:
            print("Not connected to the mail server.")
            return

        self.mail.select("inbox")
        status, messages = self.mail.search(None, "ALL")

        if status != "OK":
            print("[!] Failed to retrieve emails.")
            return

        email_ids = messages[0].split()
        if not email_ids:
            print("[!] Inbox is empty.")
            return

        # Get the last N email IDs (most recent ones)
        latest_ids = email_ids[-limit:]

        for eid in reversed(latest_ids):  # reversed to show newest first
            status, msg_data = self.mail.fetch(eid, "(RFC822)")
            if status != "OK":
                continue
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")
                    sender = msg.get("From")
                    body = self._extract_body(msg)

                    self.emails.append({
                        "subject": subject,
                        "sender": sender,
                        "content": body
                    })

        return self.emails


    def _extract_body(self, msg):
        """
        Extract plain text body from the email message.
        """
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    return part.get_payload(decode=True).decode(errors="ignore")
        else:
            return msg.get_payload(decode=True).decode(errors="ignore")
        return "[No plain text content found]"

    def disconnect(self):
        if self.mail:
            self.mail.logout()
            print("[✓] Logged out.")

