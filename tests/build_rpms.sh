#!/bin/bash

set -exu

# Build source and binary RPMs.
# SRPMs will be /tmp/rpmbuild/SRPMS/*.rpm.
# Binary RPMs will be /tmp/rpmbuild/RPMS/*/*.rpm.

PLATFORM=$1
OS_VERSION=${PLATFORM##*:}
BUILD_ENV=$2

if  [[ $OS_VERSION == 7 ]]; then
    YUM_PKG_NAME="yum-plugin-priorities"
else
    YUM_PKG_NAME="yum-utils"
fi

# Clean the yum cache
yum clean all

# Exponential backoff retry for missing DNF lock file
# FileNotFoundError: [Errno 2] No such file or directory: '/var/cache/dnf/metadata_lock.pid'
# 2020-03-17T13:43:57Z CRITICAL [Errno 2] No such file or directory: '/var/cache/dnf/metadata_lock.pid'
set +e
for retry in {1..3}; do
    yum -y -d0 update  # Update the OS packages
    [[ $? -eq 0 ]] && break
    sleep $((5**$retry))
done
set -e

yum install -y epel-release $YUM_PKG_NAME

# Broken mirror?
echo "exclude=mirror.beyondhosting.net" >> /etc/yum/pluginconf.d/fastestmirror.conf

if [[ $OS_VERSION != 7 ]]; then
    yum-config-manager --enable powertools
fi

# Install packages required for the build
yum -y install \
    rpm-build \
    cmake \
    git \
    tar \
    gzip \
    make \
    autoconf \
    automake \
    openssl \
    python3 \
    python-srpm-macros \
    python-rpm-macros \
    python3-rpm-macros \
    python3-devel \
    rrdtool \
    rrdtool-devel

if [[ $BUILD_ENV == osg* ]]; then
    OSG_SERIES=$(cut -d- -f2 <<< "$BUILD_ENV")
    yum install -y https://repo.opensciencegrid.org/osg/${OSG_SERIES}/osg-${OSG_SERIES}-el${OS_VERSION}-release-latest.rpm
else
    # This is currently tracking the 9.0 stable release.
    # For the stable release series the version number is required.
    # For the feature series, one can either use the version number (i.e. 9.1)
    # or 'current' which tracks the latest feature series
    yum install -y https://research.cs.wisc.edu/htcondor/repo/9.0/htcondor-release-current.el${OS_VERSION}.noarch.rpm
fi

# Prepare the RPM environment
mkdir -p /tmp/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

printf "%s\n" "%dist .el${OS_VERSION}" >> /etc/rpm/macros.dist
[[ ${BUILD_ENV} =~ ^osg ]] && printf "%s\n" "%osg 1" >> /etc/rpm/macros.dist

cp htcondor-ce/rpm/htcondor-ce.spec /tmp/rpmbuild/SPECS
package_version=`grep Version htcondor-ce/rpm/htcondor-ce.spec | awk '{print $2}'`
pushd htcondor-ce
git archive --format=tar --prefix=htcondor-ce-${package_version}/ HEAD | \
    gzip > /tmp/rpmbuild/SOURCES/htcondor-ce-${package_version}.tar.gz
popd

# Build the SRPM; don't put a dist tag in it
rpmbuild --define '_topdir /tmp/rpmbuild' --undefine 'dist' -bs /tmp/rpmbuild/SPECS/htcondor-ce.spec
# Build the binary RPM
rpmbuild --define '_topdir /tmp/rpmbuild' -bb /tmp/rpmbuild/SPECS/htcondor-ce.spec

# dir needs to be inside htcondor-ce so it's visible outside the container
mkdir -p htcondor-ce/ci_deploy
cp -f /tmp/rpmbuild/RPMS/*/*.rpm htcondor-ce/ci_deploy/
cp -f /tmp/rpmbuild/SRPMS/*.rpm htcondor-ce/ci_deploy/
