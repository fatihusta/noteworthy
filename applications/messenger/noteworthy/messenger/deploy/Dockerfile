FROM notectl:latest

ADD . /opt/noteworthy/dist
ADD install.sh /opt/noteworthy/
RUN chmod +x /opt/noteworthy/install.sh

RUN /opt/noteworthy/install.sh

ENTRYPOINT ["notectl start"]