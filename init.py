import sys
import subprocess

from datetime import datetime

from MailClient import MailClient

with open('credentials/openconnect.txt') as oc_acc:
    OC_USER, OC_PWD = oc_acc.readlines()[:2]


if __name__ == '__main__':
    squid = subprocess.Popen(['squid'])

    mail_client = MailClient()

    while True:
        for i in range(3):
            mail_client.reset_init_time()
            oc = subprocess.Popen(['openconnect', 'vpn2fa.hku.hk'],
                                  bufsize=1, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr,
                                  encoding='utf-8')

            oc.stdin.write(OC_USER)
            oc.stdin.write(OC_PWD)
            token = mail_client.parse_token()
            if token:
                oc.stdin.write(token+'\n')
                break
            print(datetime.now().isoformat(), f'Faild getting token, retrying{i}/{3}')
        else:
            print(datetime.now().isoformat(), 'Reached maximum reattempts.', file=sys.stderr)
            exit(1)

        oc.wait()
        print(datetime.now().isoformat(), 'Reconnecting')
