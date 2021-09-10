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

if [ $BUILD_ENV == osg* ] || [ $BUILD_ENV == uw_build ]; then
    run_osg_tests
fi

exit $test_exit
