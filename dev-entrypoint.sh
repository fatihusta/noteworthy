#!/bin/bash
cd /opt/noteworthy/notectl
rm -rf build/ dist/
python setup.py develop

pip install -r requirements.txt

bash