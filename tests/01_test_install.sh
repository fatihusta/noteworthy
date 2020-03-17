#!/bin/bash

echo "Running notectl installation test..."

if [ -z "$WORKSPACE" ]
then
    WORKSPACE=/opt/noteworthy
    docker run -v `pwd`:/opt/noteworthy -e WORKSPACE=$WORKSPACE --rm --entrypoint $WORKSPACE/notectl/test-entrypoint.sh python:3.8
else
    docker run --volumes-from jenkins -e WORKSPACE=$WORKSPACE --rm --entrypoint $WORKSPACE/notectl/test-entrypoint.sh python:3.8
fi
