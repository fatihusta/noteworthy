#!/bin/bash

docker run --rm --entrypoint /opt/noteworthy/notectl/test-entrypoint.sh -v `pwd`:/opt/noteworthy/notectl python:3.8