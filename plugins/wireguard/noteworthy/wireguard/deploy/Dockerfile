FROM alpine:latest

RUN apk add git linux-headers build-base py3-py py3-pip py3-yaml openssh openssh-server-pam sudo; \
git clone https://git.zx2c4.com/wireguard-tools; cd wireguard-tools/src; make && make install;\
mkdir -p /opt/noteworthy/noteworthy-wireguard;

ADD wg-shell.py /opt/noteworthy/noteworthy-wireguard