#!/bin/sh -x

OS_VERSION=$1

ls -l /home

# First, install all the needed packages.
rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-${OS_VERSION}.noarch.rpm
yum -y install yum-plugin-priorities
rpm -Uvh https://repo.grid.iu.edu/osg/3.3/osg-3.3-el${OS_VERSION}-release-latest.rpm
yum -y install rpm-build gcc gcc-c++ boost-devel globus-rsl-devel condor-classads-devel cmake git tar gzip make autotools

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

# Install the /var/lock directory
mkdir -p /var/lock

# After building the RPM, try to install it
yum localinstall -y /tmp/rpmbuild/RPMS/x86_64/htcondor-ce-client* /tmp/rpmbuild/RPMS/x86_64/htcondor-ce-${package_version}* /tmp/rpmbuild/RPMS/x86_64/htcondor-ce-view*

############
# Cannot start the condor-ce service correctly on docker
############

# Try starting the service:
#service condor-ce start

# Sleep for a few seconds, then run some basic commands
#sleep 30
#condor_ce_status
#condor_ce_q
