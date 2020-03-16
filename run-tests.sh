#!/bin/bash

# Jenkins runs these tests from the top-level dir of the repo

echo "------------------"
pwd
echo "------------------"


for test in notectl/tests/*;
    do $test;
done

