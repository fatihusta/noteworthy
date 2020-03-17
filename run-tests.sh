#!/bin/bash

# This script is intended to be run via `make test`

echo "Running notectl tests..."

if [ -z "$WORKSPACE" ]
then
    WORKSPACE=/opt/noteworthy
    docker run -v `pwd`:/opt/noteworthy -e WORKSPACE=$WORKSPACE --rm --entrypoint $WORKSPACE/notectl/test-entrypoint.sh notectl:latest
else
    docker run --volumes-from jenkins -e WORKSPACE=$WORKSPACE --rm --entrypoint $WORKSPACE/notectl/test-entrypoint.sh notectl:latest
fi