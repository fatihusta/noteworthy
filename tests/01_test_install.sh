#!/bin/bash

ls

docker run --rm --entrypoint /opt/noteworthy/notectl/test-entrypoint.sh -v `pwd`/notectl:/opt/noteworthy/notectl python:3.8