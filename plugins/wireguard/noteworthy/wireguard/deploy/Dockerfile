FROM alpine:latest

RUN apk add git linux-headers build-base py3-py py3-pip py3-yaml openssh openssh-server-pam sudo; \
git clone https://git.zx2c4.com/wireguard-tools; cd wireguard-tools/src; make && make install;\
mkdir -p /opt/noteworthy/noteworthy-wireguard;

COPY wg-easy.sh wg-easy-set.py wg-easy-hub.py /usr/bin/
COPY noteworthy /usr/lib/python3.8/site-packages/noteworthy


ADD entrypoint.sh /opt/noteworthy/noteworthy-wireguard


ENTRYPOINT ["/opt/noteworthy/noteworthy-wireguard/entrypoint.sh"]