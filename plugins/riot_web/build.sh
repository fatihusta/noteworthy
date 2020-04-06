#!/bin/bash
set -e
echo 'Building riot_web plugin...'
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
docker build ext -t riot_web_tmp_img
echo "build it"
docker create -ti --name riot_web_tmp riot_web_tmp_img bash
docker cp riot_web_tmp:/src/web_app.tar.gz ext/web_app.tar.gz
docker rm -f riot_web_tmp
echo 'done.'
