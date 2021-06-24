#!/bin/bash

# Allow the derived images to run any additional runtime customizations
for x in /etc/condor-ce/image-init.d/*.sh; do source "$x"; done

# Allow child images to add cleanup customizations
function source_cleanup {
    for x in /etc/condor-ce/image-cleanup.d/*.sh; do source "$x"; done
}
trap source_cleanup EXIT TERM QUIT

# Now we can actually start the supervisor
exec /usr/bin/supervisord -c /etc/supervisord.conf

