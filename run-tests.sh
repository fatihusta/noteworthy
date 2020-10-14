#!/bin/bash


# This script is intended to be run via `make test`

echo "Running notectl tests..."
if [ "$1" = "integration" ]
then
    echo "Running integration tests..."
    if [ -z "$WORKSPACE" ]
    then
        if [ -z "$HUB_IP" ]
        then
            echo "Must provide arg HUB_IP `make integration-test HUB_IP=192.168.1.x`"
            exit 1
        fi
        # DO THIS ON DEV / LOCAL
        WORKSPACE=/opt/noteworthy
        CMD="--hub $HUB_IP -m integration"
        docker run -e HUB_IP=$HUB_IP -v "/usr/local/bin/docker:/usr/local/bin/docker" -v "/var/run/docker.sock:/var/run/docker.sock" -v `pwd`:/opt/noteworthy -e WORKSPACE=$WORKSPACE --rm --entrypoint pytest noteworthy:dev $CMD
    else
        # DO THIS ON CI
        docker run --volumes-from jenkins -e WORKSPACE=$WORKSPACE --rm --entrypoint $WORKSPACE/notectl/docker-test.sh python:3.8
    fi

else
    if [ -z "$WORKSPACE" ]
    then
        # DO THIS ON DEV / LOCAL
        WORKSPACE=/opt/noteworthy
        docker run -v "/usr/local/bin/docker:/usr/local/bin/docker" -v "/var/run/docker.sock:/var/run/docker.sock" -v `pwd`:/opt/noteworthy -e WORKSPACE=$WORKSPACE --rm --entrypoint pytest noteworthy:dev '-m not integration'
    else
        # DO THIS ON CI
        docker run --volumes-from jenkins -e WORKSPACE=$WORKSPACE --rm --entrypoint $WORKSPACE/notectl/docker-test.sh python:3.8
    fi
fi