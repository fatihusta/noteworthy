FROM alpine:latest

RUN apk add git linux-headers build-base py3-py py3-pip py3-yaml openssh openssh-server-pam sudo; \
git clone https://git.zx2c4.com/wireguard-tools; cd wireguard-tools/src; make && make install;\
mkdir -p /opt/noteworthy/noteworthy-wireguard;

ADD config.yaml /opt/noteworthy/noteworthy-wireguard/
ADD wg-easy.sh wg-easy-set.py wg-easy-hub.py /usr/bin/

# So, funny quirk here. These files are shipped with the noteworthy-wireguard
# python package and for some reason setup tools removes the executable bit on the *.py
# files when packaging these up via MANIFEST.in that pulls in everything from the deploy/ dir.
# These files need to be executable so fix them here.
RUN chmod +x /usr/bin/wg-easy-set.py /usr/bin/wg-easy-hub.py
COPY noteworthy /usr/lib/python3.8/site-packages/noteworthy


ADD entrypoint.sh /opt/noteworthy/noteworthy-wireguard


ENTRYPOINT ["/opt/noteworthy/noteworthy-wireguard/entrypoint.sh"]