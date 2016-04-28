#!/bin/sh -xe

OS_VERSION=$1

ls -l /home

# Clean the yum cache
yum -y clean all
yum -y clean expire-cache

# First, install all the needed packages.
rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-${OS_VERSION}.noarch.rpm

# Broken mirror?
echo "exclude=mirror.beyondhosting.net" >> /etc/yum/pluginconf.d/fastestmirror.conf

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

yum localinstall -y /tmp/rpmbuild/RPMS/noarch/htcondor-ce-client* /tmp/rpmbuild/RPMS/noarch/htcondor-ce-${package_version}* /tmp/rpmbuild/RPMS/noarch/htcondor-ce-condor-${package_version}* /tmp/rpmbuild/RPMS/noarch/htcondor-ce-view*

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
yum -y install --enablerepo=osg-testing osg-test osg-configure
# osg-test will automatically determine the correct tests to run based on the RPMs installed.
# Don't cleanup so we can do reasonable debug printouts later.

# HTCondor really, really wants a domain name.  Fake one.
sed /etc/hosts -e "s/`hostname`/`hostname`.unl.edu `hostname`/" > /etc/hosts.new
/bin/cp -f /etc/hosts.new /etc/hosts

# Bind on the right interface and skip hostname checks.
cat << EOF > /etc/condor/config.d/99-local.conf
NETWORK_INTERFACE=eth0
GSI_SKIP_HOST_CHECK=true
SCHEDD_DEBUG=\$(SCHEDD_DEBUG) D_FULLDEBUG
SCHEDD_INTERVAL=1
SCHEDD_MIN_INTERVAL=1
EOF
cp /etc/condor/config.d/99-local.conf /etc/condor-ce/config.d/99-local.conf

# Reduce the trace timeouts
export _condor_CONDOR_CE_TRACE_ATTEMPTS=60

# Ok, do actual testing
osg-test -vad --hostcert --no-cleanup

# Some simple debug files for failures.
openssl x509 -in /etc/grid-security/hostcert.pem -noout -text
echo "------------ CE Logs --------------"
cat /var/log/condor-ce/MasterLog
cat /var/log/condor-ce/CollectorLog
cat /var/log/condor-ce/SchedLog
cat /var/log/condor-ce/JobRouterLog
_condor_COLLECTOR_PORT=9619 condor_status -schedd -l | sort
echo "------------ HTCondor Logs --------------"
cat /var/log/condor/MasterLog
cat /var/log/condor/CollectorLog
cat /var/log/condor/SchedLog
condor_config_val -dump
condor_status -schedd -l | sort
