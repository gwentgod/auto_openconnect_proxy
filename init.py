import sys
import subprocess
import time
from datetime import datetime, timedelta, timezone

from poplib import POP3_SSL
from email import message_from_bytes

import logging
LOG_FORMAT = '%(asctime)s: %(levelname)s %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


try:
    with open('/root/credentials/mail.txt') as mail_credentials:
        POP_SERVER, MAIL_USER, MAIL_PWD = mail_credentials.read().split('\n')[:3]
    with open('/root/credentials/openconnect.txt') as  oc_credentials:
        OC_USER, OC_PWD = oc_credentials.read().split('\n')[:2]
except FileNotFoundError:
    logging.critical('Failed to find credentials.')
    exit(1)
except ValueError:
    logging.critical('Failed to parse credentials')
    exit(1)


class MailClient:
    def __init__(self):
        self.reset_init_time()
        self.pop_server = POP3_SSL(POP_SERVER)
        self.pop_server.user(MAIL_USER)
        self.pop_server.pass_(MAIL_PWD)

    def reset_init_time(self):
        self.initial_time = datetime.now(timezone(timedelta(hours=8)))

    def download_last_mail(self):
        try:
            mail_count = len(self.pop_server.list()[1])
            while mail_count > 0:
                mail_bytes_list = self.pop_server.retr(mail_count)[1]
                mail_bytes = b'\n'.join(mail_bytes_list)
                mail = message_from_bytes(mail_bytes)
                if 'HKU 2FA Email Token Code' in mail['Subject']:
                    return mail
            logging.info('No mail found in selected mailbox')
        except Exception as e:
            logging.error(e)

        return None

    def parse_token(self):
        for _ in range(50):
            time.sleep(5)
            mail = self.download_last_mail()

            if mail is None:
                continue

            sent_time = datetime.strptime(mail['Date'].split(', ')[-1], "%d %b %Y %H:%M:%S %z")
            logging.info(f'Last mail was sent at {sent_time.isoformat()}')
            deltat = self.initial_time - sent_time
            if sent_time > self.initial_time and deltat < timedelta(minutes=5):
                token = mail['Subject'].split()[-1]
                logging.info(f'Received valid token {token} at {sent_time.isoformat()}')
                self.pop_server.quit()
                return token

        return None


if __name__ == '__main__':
    clash = subprocess.Popen(['/root/clash', '-d', '/etc/clash'], stdout=sys.stdout, stderr=sys.stderr)

    while True:
        mail_client = MailClient()

        for i in range(3):
            logging.warning('Starting new connection')

            mail_client.reset_init_time()
            oc = subprocess.Popen(['openconnect', '--reconnect-timeout', '15', 'vpn2fa.hku.hk'],
                                  bufsize=1, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr,
                                  encoding='utf-8')
            oc.stdin.write(OC_USER+'\n')
            oc.stdin.write(OC_PWD+'\n')

            token = mail_client.parse_token()
            if token:
                oc.stdin.write(token+'\n')
                break
            logging.warning(f'Failed getting token, retrying{i}/{3}')
        else:
            logging.error('Reached maximum reattempts.')
            exit(1)

        oc.wait()

        if clash.poll() is not None:
            logging.warning(f'Clash exited with code {clash.returncode}. Restarting')
            clash = subprocess.Popen(['/root/clash', '-d', '/etc/clash'], stdout=sys.stdout, stderr=sys.stderr)
