FROM debian

WORKDIR /root

RUN apt-get update && apt-get install -y openconnect squid python3 python3-pip
RUN pip3 install pytz
RUN apt-get remove -y python3-pip && apt-get autoremove -y

COPY init.py /root/init.py
COPY MailClient.py /root/MailClient.py

CMD python3 init.py
