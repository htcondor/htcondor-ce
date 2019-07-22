#!/bin/bash -xe

# Build source and binary RPMs.
# SRPMs will be /tmp/rpmbuild/SRPMS/*.rpm.
# Binary RPMs will be /tmp/rpmbuild/RPMS/*/*.rpm.

export OS_VERSION=${1:-$OS_VERSION}
export BUILD_ENV=${2:-$BUILD_ENV}
export DEPLOY_STAGE=${3:-$DEPLOY_STAGE}
export REPO_OWNER=${4:-$REPO_OWNER}


if $DEPLOY_STAGE && [[ -z $REPO_OWNER ]]; then
    echo >&2 "Deploying requires a REPO_OWNER"
    exit 1
fi


keyfile=$(dirname "$0")/id_rsa_cibot
upload_server=ci-xfer.chtc.wisc.edu
# from "ssh-keyscan -t rsa ci-xfer.chtc.wisc.edu"
hostsig="ci-xfer.chtc.wisc.edu ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDyrceRMLPsOmdtDHxXpfI82snDF0Q9/Z1Mick5zsQK1RyOtNgkyvXM50AJSPPSl0I9JmIxSBxhqcNDcbDz0Kc8tKcA1iGQxp4Ll9z9ZCl60AUq72WwkS1A4z11JjRoYvw1CL8bvoJhk55dcgAz+bXWx/eTwcBsmW80/okNDkdYmtv+QgfUmRP6TjMtIkzvCsXi5x+B4j66yQcLDDYb36EcGyHZqoyLuxkxX0OwS7LuzDfnKxpsV9jlnu3PuJnZOizalqKUpTYc2b83XnfsIYTqoiclmFr89+WuQJG6e/596y/9aVtNacCphdS7u3D+tSoME6OG7xQtZiQfkWvKPicv"



function setup_ssh {
    if [[ ! -e $keyfile.enc.$REPO_OWNER ]]; then
        echo "Repo owner $REPO_OWNER does not have a key in the repo." >&2
        echo "Cannot deploy via ssh." >&2
        return 1
    fi
    (
        umask 077
        mkdir -p ~/.ssh
        openssl aes-256-cbc \
            -K $encrypted_e14a22ad945b_key \
            -iv $encrypted_e14a22ad945b_iv \
            -in $keyfile.enc.$REPO_OWNER -out $keyfile \
            -d
        cat > ~/.ssh/config <<__END__
Host $upload_server
User cibot
IdentityFile $keyfile
PubkeyAuthentication yes
PasswordAuthentication no
GSSAPIAuthentication no
ChallengeResponseAuthentication no
KerberosAuthentication no
IdentitiesOnly yes
__END__
        printf "%s\n" "$hostsig" > ~/.ssh/known_hosts
    )
}

remote_dir=/var/tmp/travis/htcondor-ce/${REPO_OWNER}-${TRAVIS_JOB_NUMBER:-0.0}
function sftp_to_chtc {
    local ret=0
    script=$(mktemp -t build_rpms.$$.XXXXXX)
    cat >>"$script" <<__END__
-MKDIR /var/tmp/travis
-MKDIR /var/tmp/travis/htcondor-ce
-MKDIR $remote_dir
CD $remote_dir
__END__

    for file; do
        printf 'PUT "%s"\n' "$file" >>"$script"
    done

    sftp -b "$script" "$upload_server"; ret=$?

    return $ret
}


# Clean the yum cache
yum clean all
yum -y -d0 update  # Update the OS packages

# First, install all the needed packages.
rpm -U https://dl.fedoraproject.org/pub/epel/epel-release-latest-${OS_VERSION}.noarch.rpm

# Broken mirror?
echo "exclude=mirror.beyondhosting.net" >> /etc/yum/pluginconf.d/fastestmirror.conf

yum -y -d0 install yum-plugin-priorities rpm-build gcc gcc-c++ boost-devel cmake git tar gzip make autotools openssl

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

if [[ $BUILD_ENV == uw_build ]]; then
    printf "%s\n" "%dist .el${OS_VERSION}" >> /etc/rpm/macros.dist
else
    printf "%s\n" "%dist .${BUILD_ENV}.el${OS_VERSION}" >> /etc/rpm/macros.dist
fi
printf "%s\n" "%${BUILD_ENV} 1" >> /etc/rpm/macros.dist

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

    setup_ssh
    sftp_to_chtc htcondor-ce/travis_deploy/*
fi

