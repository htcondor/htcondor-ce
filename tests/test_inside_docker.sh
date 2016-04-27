#!/bin/sh -xe

OS_VERSION=$1

ls -l /home

# Clean the yum cache
yum -y clean all
yum -y clean expire-cache

# First, install all the needed packages.
rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-${OS_VERSION}.noarch.rpm
yum -y install yum-plugin-priorities
rpm -Uvh https://repo.grid.iu.edu/osg/3.3/osg-3.3-el${OS_VERSION}-release-latest.rpm
yum -y install rpm-build gcc gcc-c++ boost-devel cmake git tar gzip make autotools

# Prepare the RPM environment
mkdir -p /tmp/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
cat >> /etc/rpm/macros.dist << EOF
%dist .osg.el${OS_VERSION}
%osg 1
EOF

cp htcondor-ce/config/htcondor-ce.spec /tmp/rpmbuild/SPECS
package_version=`grep Version htcondor-ce/config/htcondor-ce.spec | awk '{print $2}'`
pushd htcondor-ce
git archive --format=tar --prefix=htcondor-ce-${package_version}/ HEAD  | gzip >/tmp/rpmbuild/SOURCES/htcondor-ce-${package_version}.tar.gz
popd

# Build the RPM
rpmbuild --define '_topdir /tmp/rpmbuild' -ba /tmp/rpmbuild/SPECS/htcondor-ce.spec

# After building the RPM, try to install it
# Fix the lock file error on EL7.  /var/lock is a symlink to /var/run/lock
mkdir -p /var/run/lock

yum localinstall -y /tmp/rpmbuild/RPMS/noarch/htcondor-ce-client* /tmp/rpmbuild/RPMS/noarch/htcondor-ce-${package_version}* /tmp/rpmbuild/RPMS/noarch/htcondor-ce-view*

# Run unit tests
pushd htcondor-ce/tests/
python run_tests.py
popd

# Source repo version
#git clone https://github.com/opensciencegrid/osg-test.git
#pushd osg-test
#make install
#popd
#git clone https://github.com/opensciencegrid/osg-ca-generator.git
#pushd osg-ca-generator
#make install
#popd
# RPM version of osg-test
yum -y install --enablerepo=osg-testing osg-test
# osg-test will automatically determine the correct tests to run based on the RPMs installed.
# Don't cleanup so we can do reasonable debug printouts later.
hostname localhost.localdomain
echo "127.0.0.1 localhost localhost.localdomain localhost4 localhost4.localdomain4 `hostname`" > /etc/hosts
osg-test -vad --hostcert --no-cleanup
openssl x509 -in /etc/grid-security/hostcert.pem -noout -text
cat /var/log/condor-ce/MasterLog
cat /var/log/condor-ce/CollectorLog
cat /var/log/condor-ce/SchedLog
_condor_COLLECTOR_PORT=9619 condor_status -schedd -l | sort

