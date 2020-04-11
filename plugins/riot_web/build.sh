#!/bin/bash
set -e
echo 'Downloading riot_web app...'
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
curl https://decentralabs.io/download/riot_web_app.tar.gz > noteworthy/riot_web/deploy/web_app.tar.gz
echo 'Finished Downloading riot_web: noteworthy/riot_web/deploy/web_app.tar.gz'
