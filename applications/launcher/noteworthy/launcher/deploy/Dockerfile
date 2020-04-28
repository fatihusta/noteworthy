ARG RELEASE_TAG
FROM decentralabs/noteworthy:$RELEASE_TAG

ADD . /opt/noteworthy/dist
# TODO fix messenger install hack
ADD messenger /opt/noteworthy/notectl/applications/messenger
ADD riot_web /opt/noteworthy/notectl/plugins/riot_web
ADD install.sh /opt/noteworthy/
RUN chmod +x /opt/noteworthy/install.sh

RUN /opt/noteworthy/install.sh

ENV NOTEWORTHY_ENV $RELEASE_TAG

ENTRYPOINT ["/usr/local/bin/notectl", "start"]