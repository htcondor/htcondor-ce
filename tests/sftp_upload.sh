#!/bin/bash

_old_x=+x
[[ $- = *x* ]] && _old_x=-x

set -eu

prog=${0##*/}
progdir=${0%%/*}

if [[ -r $progdir/env.sh ]]; then
    set +x
    source $progdir/env.sh
    set $_old_x
fi

if [[ $TRAVIS_PULL_REQUEST != false ]]; then
    echo "Not running deploy on a PR"
    exit 0
fi

project=${TRAVIS_REPO_SLUG#*/}
repo_owner=${TRAVIS_REPO_SLUG%/*}

keyfile=$progdir/id_rsa_cibot2
upload_server=ci-xfer.chtc.wisc.edu
# from "ssh-keyscan -t rsa ci-xfer.chtc.wisc.edu"
hostsig="ci-xfer.chtc.wisc.edu ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDyrceRMLPsOmdtDHxXpfI82snDF0Q9/Z1Mick5zsQK1RyOtNgkyvXM50AJSPPSl0I9JmIxSBxhqcNDcbDz0Kc8tKcA1iGQxp4Ll9z9ZCl60AUq72WwkS1A4z11JjRoYvw1CL8bvoJhk55dcgAz+bXWx/eTwcBsmW80/okNDkdYmtv+QgfUmRP6TjMtIkzvCsXi5x+B4j66yQcLDDYb36EcGyHZqoyLuxkxX0OwS7LuzDfnKxpsV9jlnu3PuJnZOizalqKUpTYc2b83XnfsIYTqoiclmFr89+WuQJG6e/596y/9aVtNacCphdS7u3D+tSoME6OG7xQtZiQfkWvKPicv"



function setup_ssh_to_chtc {
    if [[ ! -e $keyfile.enc.$repo_owner ]]; then
        echo "Repo owner $repo_owner does not have a key in the repo." >&2
        echo "Cannot deploy via ssh." >&2
        return 1
    fi
    (
        umask 077
        mkdir -p ~/.ssh
        openssl aes-256-cbc \
            -K $encrypted_e14a22ad945b_key \
            -iv $encrypted_e14a22ad945b_iv \
            -in $keyfile.enc.$repo_owner -out $keyfile \
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

function sftp_to_chtc {
    local ret=0
    local remote_dir=/var/tmp/travis/$repo_owner/$project
    if [[ -n ${TRAVIS_TAG-} ]]; then
        # .../htcondor-ce-v2.3.4
        remote_dir=${remote_dir}-$(tr / _ <<<"$TRAVIS_TAG")
    else
        # .../htcondor-ce-88
        remote_dir=${remote_dir}-${TRAVIS_BUILD_NUMBER}
    fi
    set +x
    script=$(mktemp -t build_rpms.$$.XXXXXX)
    cat >>"$script" <<__END__
-MKDIR /var/tmp/travis
-MKDIR /var/tmp/travis/$repo_owner
-MKDIR $remote_dir
CD $remote_dir
__END__

    for file; do
        printf 'PUT "%s"\n' "$file" >>"$script"
    done
    set $_old_x

    cat "$script"

    sftp -b "$script" "$upload_server"; ret=$?

    return $ret
}


setup_ssh_to_chtc
sftp_to_chtc "$progdir"/../travis_deploy/*


# vim:et:sw=4:sts=4:ts=8
