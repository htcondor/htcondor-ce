#!/bin/sh

OS_VERSION=$1

ls -l /home

# First, install all the needed packages.
rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-${OS_VERSION}.noarch.rpm
yum -y install yum-plugin-priorities
rpm -Uvh https://repo.grid.iu.edu/osg/3.3/osg-3.3-el${OS_VERSION}-release-latest.rpm
yum -y install rpm-build gcc gcc-c++ boost-devel globus-rsl-devel condor-classads-devel cmake git

# Prepare the RPM environment
sudo -u centos mkdir -p /home/centos/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
cat > /home/centos/.rpmmacros << 'EOF'
%dist .osg.el6
%osg 1
EOF

cp htcondor-ce/config/htcondor-ce.spec /home/centos/rpmbuild/SPECS
package_version=`grep Version config/htcondor-ce.spec | awk '{print $2}'`
pushd htcondor-ce
git archive --format=tar --prefix=htcondor-ce-${package_version}/ HEAD  | gzip >/home/centos/rpmbuild/SOURCES/htcondor-ce-${package_version}.tar.gz
popd

sudo -u centos rpmbuild -ba /home/centos/rpmbuild/SPECS/htcondor-ce.spec
