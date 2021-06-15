#!/bin/bash

TEST_USER=testuser
TEST_HOME=$(getent passwd $TEST_USER | cut -d: -f6)
PROXY_PATH="/tmp/x509up_u$(id -u $TEST_USER)"

# Generate a test CA, host certificate, and VO files necessary for
# VOMS auth and place everything in their grid locations
osg-ca-generator --host --voms testvo --user=$TEST_USER --pass='testpass'

# Generate a user X.509 proxy with VOMS attrs
# voms-proxy-fake requires that the user cert/key to be owned by the
# user running the command. We need to run as root to be able to read
# the CA key
chown -R root: $TEST_HOME/.globus/*
echo -e 'testpass\n' | \
voms-proxy-fake -cert $TEST_HOME/.globus/usercert.pem \
                -key $TEST_HOME/.globus/userkey.pem \
                -out $PROXY_PATH \
                -bits 2048 \
                -hours 72 \
                -voms testvo \
                -hostcert /etc/grid-security/hostcert.pem \
                -hostkey /etc/grid-security/hostkey.pem \
                -uri $(hostname) \
                -fqan '/testvo/Role=NULL/Capability=NULL' \
                -path-length 20

cat << EOF >> /etc/condor-ce/mapfiles.d/10-ce.conf
GSI "$(voms-proxy-info --file $PROXY_PATH -issuer)" $TEST_USER
EOF

# The test user actually needs to be able to read the proxy
chown -R $TEST_USER: $PROXY_PATH
