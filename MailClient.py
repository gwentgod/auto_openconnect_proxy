from common import *

import time
from datetime import datetime, timedelta, timezone

from email import message_from_bytes
from imaplib import IMAP4_SSL


IMAP_SERVER, MAIL_USER, MAIL_PWD = parse_file('./credentials/mail.txt', 3)


class MailClient:
    def __init__(self):
        self.reset_init_time()

        self.imap_server = IMAP4_SSL(IMAP_SERVER)
        self.imap_server.login(MAIL_USER, MAIL_PWD)
        self.imap_server.select()

    def reset_init_time(self):
        self.initial_time = datetime.now(timezone(timedelta(hours=8)))

    def download_last_mail(self):
        try:
            status, mail_list = self.imap_server.search(None, '(Subject "HKU 2FA Email Token Code")')
            mail_list = mail_list[0].split()
            if mail_list:
                status, mail_data = self.imap_server.fetch(mail_list[-1], '(RFC822)')
                mail = message_from_bytes(mail_data[0][1])
                return mail
            else:
                logging.info('No mail found in selected mail list')
        except Exception as e:
            logging.error(e)

        return None

    def parse_token(self):
        logging.info('Waiting for mail')
        for _ in range(19):
            time.sleep(15)
            mail = self.download_last_mail()

            if not mail:
                continue

            sent_time = datetime.strptime(mail['Date'].split(', ')[-1], "%d %b %Y %H:%M:%S %z")
            logging.info(f'Last mail was sent at {sent_time.isoformat()}')
            deltat = self.initial_time - sent_time
            if sent_time > self.initial_time and deltat < timedelta(minutes=5):
                token = mail['Subject'].split()[-1]
                logging.info(f'Received valid token {token} at {sent_time.isoformat()}')
                return token

        return False
