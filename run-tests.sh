#!/bin/bash

# Jenkins runs these tests from the top-level dir of the repo
cd notectl
echo "------------------"
pwd
echo "------------------"


for test in tests/*;
    do $test;
done

