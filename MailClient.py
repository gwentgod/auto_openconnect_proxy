import time
import pytz
from datetime import datetime, timedelta

from email import message_from_bytes
from imaplib import IMAP4_SSL

with open('config/mail_config.yaml') as mail_config:
    IMAP_SERVER, MAIL_USER, MAIL_PWD = mail_config.read().split('\n')[:3]


class MailClient:
    def __init__(self):
        self.initial_time = None

        self.imap_server = IMAP4_SSL(IMAP_SERVER)
        self.imap_server.login(MAIL_USER, MAIL_PWD)
        self.imap_server.select()

    def reset_init_time(self):
        self.initial_time = datetime.now(pytz.timezone("Asia/Hong_Kong"))

    def download_last_mail(self):
        status, mail_list = self.imap_server.search(None, '(Subject "HKU 2FA Email Token Code")')
        mail_list = mail_list[0].split()
        if mail_list:
            status, mail_data = self.imap_server.fetch(mail_list[0].split()[-1], '(RFC822)')
            mail = message_from_bytes(mail_data[0][1])
            return mail
        else:
            return None

    def parse_token(self):
        for _ in range(50):
            time.sleep(5)
            mail = self.download_last_mail()

            if not mail:
                continue

            sent_time = datetime.strptime(mail['Date'].split(', ')[-1], "%d %b %Y %H:%M:%S %z")
            deltat = self.initial_time - sent_time
            if sent_time > self.initial_time and deltat < timedelta(minutes=5):
                token = mail['Subject'].split()[-1]
                return token

        return False
