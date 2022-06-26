FROM debian

WORKDIR /root

RUN apt-get update && apt-get install -y openconnect python3

COPY clash /root/clash
COPY init.py /root/init.py

CMD python3 /root/init.py
