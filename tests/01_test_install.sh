#!/bin/bash

echo "Running notectl installation test..."

sleep 10000

docker run --rm --entrypoint /opt/noteworthy/notectl/test-entrypoint.sh -v `pwd`/notectl:/opt/noteworthy/notectl python:3.8