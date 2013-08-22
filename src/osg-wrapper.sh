#!/bin/sh

# Sets the path

export PATH=/bin:/sbin:/usr/sbin:/usr/bin:/usr/local/bin:/usr/local/sbin:$PATH

# Load OSG-specific env variables
if [ -f /var/lib/osg/osg-job-environment.conf ]; then
    . /var/lib/osg/osg-job-environment.conf
fi

if [ -f /var/lib/osg/osg-local-job-environment.conf ]; then
    . /var/lib/osg/osg-local-job-environment.conf
fi

exec "$@"
error=$?
echo "Failed to exec($error): $@" > $_CONDOR_WRAPPER_ERROR_FILE
exit 1
