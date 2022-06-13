import sys
import time
from datetime import datetime, timedelta, timezone

from email import message_from_bytes
from imaplib import IMAP4_SSL

with open('credentials/mail.txt') as mail_config:
    IMAP_SERVER, MAIL_USER, MAIL_PWD = mail_config.read().split('\n')[:3]


class MailClient:
    def __init__(self):
        self.reset_init_time()

        self.imap_server = IMAP4_SSL(IMAP_SERVER)
        self.imap_server.login(MAIL_USER, MAIL_PWD)
        self.imap_server.select()

    def reset_init_time(self):
        self.initial_time = datetime.now(timezone(timedelta(hours=8)))

    def download_last_mail(self):
        status, mail_list = self.imap_server.search(None, '(Subject "HKU 2FA Email Token Code")')
        mail_list = mail_list[0].split()
        if mail_list:
            status, mail_data = self.imap_server.fetch(mail_list[-1], '(RFC822)')
            mail = message_from_bytes(mail_data[0][1])
            return mail
        else:
            print('No mail found in selected mail list', file=sys.stderr, flush=True)
            return None

    def parse_token(self):
        for _ in range(19):
            print('Waiting for mail', flush=True)
            time.sleep(15)
            mail = self.download_last_mail()

            if not mail:
                continue

            sent_time = datetime.strptime(mail['Date'].split(', ')[-1], "%d %b %Y %H:%M:%S %z")
            print('Last mail was sent at', sent_time.isoformat(), flush=True)
            deltat = self.initial_time - sent_time
            if sent_time > self.initial_time and deltat < timedelta(minutes=5):
                token = mail['Subject'].split()[-1]
                print('Got valid token', token, flush=True)
                return token

        return False
