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

project=${GITHUB_REPOSITORY#*/}
repo_owner=${GITHUB_REPOSITORY%/*}

upload_server=ci-xfer.chtc.wisc.edu
# from "ssh-keyscan -t rsa ci-xfer.chtc.wisc.edu"
hostsig="ci-xfer.chtc.wisc.edu ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDyrceRMLPsOmdtDHxXpfI82snDF0Q9/Z1Mick5zsQK1RyOtNgkyvXM50AJSPPSl0I9JmIxSBxhqcNDcbDz0Kc8tKcA1iGQxp4Ll9z9ZCl60AUq72WwkS1A4z11JjRoYvw1CL8bvoJhk55dcgAz+bXWx/eTwcBsmW80/okNDkdYmtv+QgfUmRP6TjMtIkzvCsXi5x+B4j66yQcLDDYb36EcGyHZqoyLuxkxX0OwS7LuzDfnKxpsV9jlnu3PuJnZOizalqKUpTYc2b83XnfsIYTqoiclmFr89+WuQJG6e/596y/9aVtNacCphdS7u3D+tSoME6OG7xQtZiQfkWvKPicv"



function setup_ssh_to_chtc {
    (
        umask 077
        mkdir -p ~/.ssh
        cat > ~/.ssh/config <<__END__
Host $upload_server
User cibot
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
    local remote_dir=/var/tmp/ci_deploy/$repo_owner/$project
    if [[ $GITHUB_REF =~ ^refs/tags/ ]]; then
        # .../htcondor-ce-v2.3.4
        remote_dir=${remote_dir}-$(tr / _ <<<"${GITHUB_REF##refs/tags/}")
    else
        # .../htcondor-ce-88
        remote_dir=${remote_dir}-${GITHUB_RUN_ID}
    fi
    set +x
    script=$(mktemp -t build_rpms.$$.XXXXXX)
    cat >>"$script" <<__END__
-MKDIR /var/tmp/ci_deploy
-MKDIR /var/tmp/ci_deploy/$repo_owner
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
sftp_to_chtc "$progdir"/../ci_deploy/*


# vim:et:sw=4:sts=4:ts=8
