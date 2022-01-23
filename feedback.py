import smtplib
import os

class FeedbackMessage():

    def __init__(self):
        self.MY_EMAIL = "svitbands@gmail.com"
        self.EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
        self.GMAIL_HOST = "smtp.gmail.com"


    def receive_msg(self, message):
        with smtplib.SMTP(self.GMAIL_HOST, port=587) as connection:
            connection.starttls()
            connection.login(user=self.MY_EMAIL, password=self.EMAIL_PASSWORD)
            connection.sendmail(from_addr=self.MY_EMAIL, to_addrs="i.svit@yahoo.com", msg=message)