#!/bin/bash

# This script starts docker and systemd (if el7)

OS_VERSION=$1
BUILD_ENV=$2

set -e

# Run tests in Container
# We use `--privileged` for cgroup compatability, which seems to be enabled by default in HTCondor 8.6.x
set +x
env_file=`pwd`/tests/env.sh
cat >"$env_file" <<__END__
encrypted_e14a22ad945b_key=$encrypted_e14a22ad945b_key
encrypted_e14a22ad945b_iv=$encrypted_e14a22ad945b_iv
TRAVIS_REPO_SLUG=$TRAVIS_REPO_SLUG
TRAVIS_BUILD_NUMBER=$TRAVIS_BUILD_NUMBER
TRAVIS_JOB_NUMBER=$TRAVIS_JOB_NUMBER
TRAVIS_PULL_REQUEST=$TRAVIS_PULL_REQUEST
TRAVIS_TAG=$TRAVIS_TAG
__END__
trap "rm -f \"$env_file\"" EXIT
set -x

DOCKER_CONTAINER_ID=$BUILD_ENV-$OS_VERSION

# Disable slow dnf makecache service
# https://bugzilla.redhat.com/show_bug.cgi?id=1814337
[[ $OS_VERSION -gt 7 ]] && \
    docker exec $DOCKER_CONTAINER_ID systemctl stop dnf-makecache

