#!/bin/bash

TEST_USER=testuser
TOKEN_PATH="/tmp/bt_u$(id -u $TEST_USER)"

cat << EOF >> /etc/condor-ce/mapfiles.d/10-ce.conf
SCITOKENS /https:\/\/demo.scitokens.org,.*/ $TEST_USER
EOF

su -c /usr/local/bin/renew-demo-token.py $TEST_USER
