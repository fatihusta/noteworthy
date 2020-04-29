#!/bin/bash

# This script is intended to be run via `make test`

echo "Running notectl tests..."

if [ -z "$WORKSPACE" ]
then
    # DO THIS ON DEV / LOCAL
    WORKSPACE=/opt/noteworthy
    docker run -v "/usr/local/bin/docker:/usr/local/bin/docker" -v "/var/run/docker.sock:/var/run/docker.sock" -v `pwd`/notectl:/opt/noteworthy -e WORKSPACE=$WORKSPACE --rm --entrypoint pytest noteworthy:dev
else
    # DO THIS ON CI
    docker run --volumes-from jenkins -e WORKSPACE=$WORKSPACE --rm --entrypoint pytest noteworthy:dev
fi