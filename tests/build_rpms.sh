#!/bin/bash -xe

# Build source and binary RPMs.
# SRPMs will be /tmp/rpmbuild/SRPMS/*.rpm.
# Binary RPMs will be /tmp/rpmbuild/RPMS/*/*.rpm.

OS_VERSION=${1:-$OS_VERSION}
BUILD_ENV=${2:-$BUILD_ENV}
DEPLOY_STAGE=${3:-$DEPLOY_STAGE}


# Clean the yum cache
yum clean all
yum -y -d0 update  # Update the OS packages

# First, install all the needed packages.
rpm -U https://dl.fedoraproject.org/pub/epel/epel-release-latest-${OS_VERSION}.noarch.rpm

# Broken mirror?
echo "exclude=mirror.beyondhosting.net" >> /etc/yum/pluginconf.d/fastestmirror.conf

yum -y -d0 install yum-plugin-priorities rpm-build gcc gcc-c++ boost-devel cmake git tar gzip make autotools

if [[ $BUILD_ENV == osg ]]; then
    rpm -U https://repo.opensciencegrid.org/osg/3.4/osg-3.4-el${OS_VERSION}-release-latest.rpm
else
    pushd /etc/yum.repos.d
    yum install -y -d0 wget
    wget -q http://htcondor.org/yum/repo.d/htcondor-stable-rhel${OS_VERSION}.repo
    wget -q http://htcondor.org/yum/RPM-GPG-KEY-HTCondor
    rpm --import RPM-GPG-KEY-HTCondor
    popd
fi

# Prepare the RPM environment
mkdir -p /tmp/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# ${BUILD_ENV%_build} strips the '_build' from 'uw_build' to make the dist tag shorter.
cat >> /etc/rpm/macros.dist << EOF
%dist .${BUILD_ENV%_build}.el${OS_VERSION}
%${BUILD_ENV} 1
EOF

cp htcondor-ce/rpm/htcondor-ce.spec /tmp/rpmbuild/SPECS
package_version=`grep Version htcondor-ce/rpm/htcondor-ce.spec | awk '{print $2}'`
pushd htcondor-ce
git archive --format=tar --prefix=htcondor-ce-${package_version}/ HEAD | \
    gzip > /tmp/rpmbuild/SOURCES/htcondor-ce-${package_version}.tar.gz
popd

# Build the SRPM; don't put a dist tag in it
# rpmbuild on el6 does not have --undefine
rpmbuild --define '_topdir /tmp/rpmbuild' --define 'dist %{nil}' -bs /tmp/rpmbuild/SPECS/htcondor-ce.spec
# Build the binary RPM
rpmbuild --define '_topdir /tmp/rpmbuild' -bb /tmp/rpmbuild/SPECS/htcondor-ce.spec

if $DEPLOY_STAGE; then
    # dir needs to be inside htcondor-ce so it's visible outside the container
    mkdir -p htcondor-ce/travis_deploy
    cp -f /tmp/rpmbuild/RPMS/*/*.rpm htcondor-ce/travis_deploy/
    # HACK: only deploy the common file(s) (SRPM) on one env set
    # to avoid attempting to overwrite the GitHub build products
    # (which would raise an error).
    # `overwrite: true` in .travis.yml ought to fix that but doesn't
    # appear to.
    if [[ $OS_VERSION == 6 ]]; then
        cp -f /tmp/rpmbuild/SRPMS/*.rpm htcondor-ce/travis_deploy/
    fi
fi

