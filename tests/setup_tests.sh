#!/bin/bash

# This script starts docker and systemd (if el7)

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

if [[ $OS_VERSION -eq 6 ]]; then
    sudo docker run --privileged --rm=true \
         --volume /sys/fs/cgroup:/sys/fs/cgroup \
         --volume `pwd`:/htcondor-ce:rw \
         centos:centos${OS_VERSION} \
         /bin/bash -c "exec bash -x /htcondor-ce/tests/test_inside_docker.sh ${OS_VERSION} ${BUILD_ENV}"
elif [[ $OS_VERSION -eq 7 ]]; then
    docker run --privileged --detach --tty --interactive --env "container=docker" \
           --volume /sys/fs/cgroup:/sys/fs/cgroup \
           --volume `pwd`:/htcondor-ce:rw  \
           centos:centos${OS_VERSION} \
           /usr/sbin/init

    DOCKER_CONTAINER_ID=$(docker ps | grep centos | awk '{print $1}')
    docker logs $DOCKER_CONTAINER_ID
    docker exec --tty --interactive $DOCKER_CONTAINER_ID \
           /bin/bash -c "exec bash -x /htcondor-ce/tests/test_inside_docker.sh ${OS_VERSION} ${BUILD_ENV};
           echo -ne \"------\nEND HTCONDOR-CE TESTS\n\";"

    docker ps -a
    docker stop $DOCKER_CONTAINER_ID
    docker rm -v $DOCKER_CONTAINER_ID
fi


