#!/bin/bash

set -ex

BUILD_ENV=$1

# After building the RPM, try to install it
# Fix the lock file error on EL7.  /var/lock is a symlink to /var/run/lock
mkdir -p /var/run/lock

# Create the condor user/group for subsequent chowns,
# using the official RHEL UID/GID
groupadd -g 64 -r condor
useradd -r -g condor -d /var/lib/condor -s /sbin/nologin \
        -u 64 -c "Owner of HTCondor Daemons" condor

RPM_LOCATION=/tmp/rpmbuild/RPMS/noarch
[[ $BUILD_ENV =~ ^osg\-[0-9]+\.[0-9]+\-upcoming$ ]] && extra_repos='--enablerepo=osg-upcoming'

package_version=`grep Version htcondor-ce/rpm/htcondor-ce.spec | awk '{print $2}'`
yum localinstall -y $RPM_LOCATION/htcondor-ce-${package_version}* \
    $RPM_LOCATION/htcondor-ce-client-* \
    $RPM_LOCATION/htcondor-ce-condor-* \
    $RPM_LOCATION/htcondor-ce-view-* \
    $extra_repos
