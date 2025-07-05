#!/bin/bash

function run_osg_tests {
    # Install tooling for creating test certificates
    git clone -q https://github.com/opensciencegrid/osg-ca-generator.git
    pushd osg-ca-generator
    git rev-parse HEAD
    make install PYTHON=/usr/bin/python3
    popd

    # Source repo version
    git clone -q https://github.com/opensciencegrid/osg-test.git
    pushd osg-test
    git rev-parse HEAD
    make install
    popd

    # Ok, do actual testing
    set +e # don't exit immediately if osg-test fails
    echo "------------ OSG Test --------------"
    osg-test -vad --hostcert --no-cleanup
    test_exit=$?
    set -e
}

function run_integration_tests {
    # create host/user token
    test_user=cetest
    useradd -m $test_user

    ce_mapfile='/etc/condor-ce/mapfiles.d/01-osg-test.conf'
    issuer='https://demo.scitokens.org'
    map_string='/https:\/\/demo.scitokens.org,.*/'
    echo "SCITOKENS $map_string $test_user" > $ce_mapfile
    chmod 644 $ce_mapfile

    echo "------------ Integration Test --------------"
    # start necessary services
    systemctl start condor-ce
    systemctl start condor

    set +e
    # wait until the schedd is ready before submitting a job
    for service in condor condor-ce; do
        timeout 30 bash -c "until (grep -q 'JobQueue hash' /var/log/${service}/SchedLog); do sleep 0.5; done"
        timeout 30 bash -c "until (grep -q 'ScheddAd' /var/log/${service}/CollectorLog); do sleep 0.5; done"
    done

    # submit test job as a normal user
    pushd /tmp
    su $test_user -c "condor_ce_test_token --issuer $issuer --scope condor:/WRITE --sub $test_user --aud ANY > bearer_token_file"
    su $test_user -c "BEARER_TOKEN_FILE=bearer_token_file condor_ce_status -any"
    curl http://127.0.0.1
    su $test_user -c "BEARER_TOKEN_FILE=bearer_token_file condor_ce_trace -d $(hostname)"
    test_exit=$?
    popd
    set -e
}

# --------- EXECUTION BEGINS HERE ---------
set -xe

PLATFORM=$1
OS_VERSION=${PLATFORM##*:}
BUILD_ENV=$2

if [[ $BUILD_ENV == uw_build ]]; then
    # UW build tests run against HTCondor, which does not automatically configure a personal condor.
    # The 'minicondor' package now provides that configuration
    dnf install -y minicondor
fi

# HTCondor really, really wants a domain name.  Fake one.
sed /etc/hosts -e "s/`hostname`/`hostname`.unl.edu `hostname`/" > /etc/hosts.new
/bin/cp -f /etc/hosts.new /etc/hosts

# Bind on the right interface and skip hostname checks.
cat << 'EOF' > /etc/condor/config.d/99-local.conf
BIND_ALL_INTERFACES = true
ALL_DEBUG=$(ALL_DEBUG) D_FULLDEBUG D_CAT D_SECURITY:2
COLLECTOR_DEBUG=$(ALL_DEBUG)
SCHEDD_DEBUG=$(ALL_DEBUG)
SCHEDD_INTERVAL=1
SCHEDD_MIN_INTERVAL=1
EOF
cp /etc/condor/config.d/99-local.conf /etc/condor-ce/config.d/99-local.conf

# Fake systemctl (since not running under systemd)
cat << 'EOF' > /tmp/systemctl
#!/bin/sh
if [ "$2" = 'condor' ]; then
    if [ "$1" = 'start' ]; then
        /usr/sbin/condor_master
    elif [ "$1" = 'stop' ]; then
        /usr/sbin/condor_off -fast -master
    elif [ "$1" = 'is-active' ]; then
        /usr/bin/condor_status -totals
    else
        echo "ERROR: Unknown command ($1) for service ($2)"
        exit 1
    fi
elif [ "$2" = 'condor-ce' ]; then
    if [ "$1" = 'start' ]; then
        /usr/share/condor-ce/condor_ce_startup
    elif [ "$1" = 'stop' ]; then
        /usr/sbin/condor_ce_off -fast -master
    elif [ "$1" = 'is-active' ]; then
        /usr/bin/condor_ce_status -totals
    else
        echo "ERROR: Unknown command ($1) for service ($2)"
        exit 1
    fi
else
    echo "ERROR: Unknown service: $2"
    exit 1
fi
EOF
chmod 755 /tmp/systemctl
mv -f /tmp/systemctl /usr/bin/systemctl

# Reduce the trace timeouts
export _condor_CONDOR_CE_TRACE_ATTEMPTS=60

if [[ $BUILD_ENV == osg* ]]; then
    run_osg_tests
else
    run_integration_tests
fi

exit $test_exit
