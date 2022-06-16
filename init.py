from common import *
from MailClient import MailClient

import sys
import subprocess


OC_USER, OC_PWD = parse_file('credentials/openconnect.txt', 2)


if __name__ == '__main__':
    clash = subprocess.Popen(['/root/clash', '-d', '/etc/clash'], stdout=sys.stdout, stderr=sys.stderr)

    while True:
        mail_client = MailClient()

        for i in range(3):
            logging.warning('Starting new connection')

            mail_client.reset_init_time()
            oc = subprocess.Popen(['openconnect', 'vpn2fa.hku.hk'],
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
