# Auto OpenConnect Proxy

> A container that automaticly maintains an [OpenConnect](https://www.infradead.org/openconnect/)
> connection that requires mail authorization,
> then hosts HTTP(S) and SOCKS proxy by [Clash](https://github.com/Dreamacro/clash).

OpenConnect is a SSL VPN client which supports the Cisco AnyConnect protocol.

Please follow the university regulations and use at your own risk.


### Build
```bash
docker build -f Dockerfile -t openconnect_proxy .
```

### Usage example
1. Prepare the credentials
    * Store your credentials for OpenConnect to a plain text file.
        ```
        # /path/to/credentials/openconnect.txt

        your_awesome_uid
        your_awesome_password
        ```
    * Store your credentials for your mail plus the imap server of your mail to another plani text file
        ```
        # /path/to/credentials/mail.txt

        imap.of.your.awesome.mail.server.com
        your_awesome_account@your_awesome_mail_server.com
        your_awesome_password
        ```

2. Create a macvlan network
    ```bash
    docker network create -d macvlan \
        --subnet=192.168.1.0/24 \
        --gateway=192.168.1.1 \
        -o parent=eth0 openconnect
    ```

3. Run the container
    ```bash
    docker run -d \
        --name auto_openconnect_proxy \
        --log-opt max-size=1m \
        --restart unless-stopped \
        --privileged \
        -e TZ=Asia/Hong_Kong \
        --network openconnect \
        --ip 192.168.1.2 \
        -v /path/to/credentials/:/root/credentials \
        -v /path/to/clash/config/:/etc/clash \
        openconnect_proxy
    ```
4. Access your HTTP(S) / SOCKS proxy at `192.168.1.2:2333`

### Notes
* Make sure you enabled IMAP service for your email account.
* Make sure the ip addr assigned in `3.` is free and out of the DHCP range.
* As warned by [Python Docs](https://docs.python.org/3/library/subprocess.html#subprocess.Popen.stdin),
Use of `Popen.stdin.write` may cause deadlocks. Take your own risk.
