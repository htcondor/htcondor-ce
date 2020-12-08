#!/bin/bash

function run_osg_tests {
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
    # create host/user certificates
    test_user=cetest
    useradd -m $test_user
    yum install -y openssl # centos7 containers don't have openssl by default
    osg-ca-generator --host --user $test_user --pass $test_user

    # add the host subject DN to the top of the condor_mapfile
    host_dn=$(python3 -c "import cagen; print(cagen.certificate_info('/etc/grid-security/hostcert.pem')[0])")
    host_dn=${host_dn//\//\\/} # escape all forward slashes
    entry="GSI \"${host_dn}\" $(hostname --long)@daemon.htcondor.org"
    ce_mapfile='/etc/condor-ce/condor_mapfile'
    tmp_mapfile=$(mktemp)
    echo $entry | cat - $ce_mapfile > $tmp_mapfile && mv $tmp_mapfile $ce_mapfile
    chmod 644 $ce_mapfile

    yum install -y sudo # run tests as non-root user

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
    # TODO: Change this to voms-proxy-init to test VOMS attr mapping
    pushd /tmp
    sudo -u $test_user /bin/sh -c "echo $test_user | grid-proxy-init -pwstdin"
    sudo -u $test_user condor_ce_trace -d $(hostname)
    test_exit=$?
    popd
    set -e
}

# --------- EXECUTION BEGINS HERE ---------
set -xe

OS_VERSION=$1
BUILD_ENV=$2

if [[ $BUILD_ENV == uw_build ]]; then
    # UW build tests run against HTCondor 8.8.0, which does not automatically configure a personal condor
    # The 'minicondor' package now provides that configuration
    extra_packages='minicondor'
fi
# ensure that our test users can generate proxies
yum install -y globus-proxy-utils $extra_packages

# HTCondor really, really wants a domain name.  Fake one.
sed /etc/hosts -e "s/`hostname`/`hostname`.unl.edu `hostname`/" > /etc/hosts.new
/bin/cp -f /etc/hosts.new /etc/hosts

# Install tooling for creating test certificates
git clone -q https://github.com/opensciencegrid/osg-ca-generator.git
pushd osg-ca-generator
git rev-parse HEAD
make install PYTHON=/usr/bin/python3
popd

# Bind on the right interface and skip hostname checks.
cat << EOF > /etc/condor/config.d/99-local.conf
BIND_ALL_INTERFACES = true
GSI_SKIP_HOST_CHECK=true
ALL_DEBUG=\$(ALL_DEBUG) D_FULLDEBUG D_CAT
SCHEDD_INTERVAL=1
SCHEDD_MIN_INTERVAL=1
EOF
cp /etc/condor/config.d/99-local.conf /etc/condor-ce/config.d/99-local.conf

# Reduce the trace timeouts
export _condor_CONDOR_CE_TRACE_ATTEMPTS=60

if [[ $BUILD_ENV == osg ]]; then
    run_osg_tests
else
    run_integration_tests
fi

exit $test_exit
