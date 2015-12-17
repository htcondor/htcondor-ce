#!/bin/sh

OS_VERSION=$1

ls -l /home

# First, install all the needed packages.
rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-${OS_VERSION}.noarch.rpm
yum -y install yum-plugin-priorities
rpm -Uvh https://repo.grid.iu.edu/osg/3.3/osg-3.3-el${OS_VERSION}-release-latest.rpm
yum -y install rpm-build gcc gcc-c++ boost-devel globus-rsl-devel condor-classads-devel cmake git

# Prepare the RPM environment
mkdir -p /tmp/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
cat >> /etc/rpm/macros.dist << 'EOF'
%dist .osg.el6
%osg 1
EOF

cp htcondor-ce/config/htcondor-ce.spec /tmp/rpmbuild/SPECS
package_version=`grep Version htcondor-ce/config/htcondor-ce.spec | awk '{print $2}'`
pushd htcondor-ce
git archive --format=tar --prefix=htcondor-ce-${package_version}/ HEAD  | gzip >/tmp/rpmbuild/SOURCES/htcondor-ce-${package_version}.tar.gz
popd

rpmbuild --buildroot=/tmp/rpmbuild -ba /tmp/rpmbuild/SPECS/htcondor-ce.spec
