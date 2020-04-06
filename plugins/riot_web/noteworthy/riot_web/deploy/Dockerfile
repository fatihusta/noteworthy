# Builder
FROM node:10 as builder

# Support custom branches of the react-sdk and js-sdk. This also helps us build
# images of riot-web develop.
ARG USE_CUSTOM_SDKS=true
ARG REACT_SDK_REPO="http://git.decentralabs.io/ether.ai/matrix-react-sdk-noteworthy.git"
ARG REACT_SDK_BRANCH="noteworthy_master"
ARG JS_SDK_REPO="http://git.decentralabs.io/ether.ai/matrix-js-sdk-noteworthy.git"
ARG JS_SDK_BRANCH="noteworthy_master"

RUN apt-get update && apt-get install -y git dos2unix
RUN git clone --depth=1 https://git.decentralabs.io/ether.ai/riot-web-noteworthy.git
WORKDIR /riot-web-noteworthy
RUN git pull --unshallow
WORKDIR /
RUN mv /riot-web-noteworthy /src

WORKDIR /src

RUN dos2unix /src/scripts/docker-link-repos.sh && bash /src/scripts/docker-link-repos.sh
RUN yarn --network-timeout=100000 install
RUN yarn build

# Copy the config now so that we don't create another layer in the app image
RUN cp /src/config.sample.json /src/webapp/config.json

# Ensure we populate the version file
RUN dos2unix /src/scripts/docker-write-version.sh && bash /src/scripts/docker-write-version.sh

RUN tar -czvf /src/web_app.tar.gz webapp/*
