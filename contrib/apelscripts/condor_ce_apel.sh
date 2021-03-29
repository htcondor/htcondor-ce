#!/bin/sh
# sjones@hep.ph.liv.ac.uk, 2019
# Run the processes of an HTCondor-CE + HTCondor accounting run

fail () {
    echo "$@" >&2
    exit 1
}

safe_config_val () {
    var=$1
    attr=$2
    val=$(/usr/bin/condor_ce_config_val $attr) ||
    fail "Failed to retrieve CE configuration value '$attr'"
    eval "$var"='$val'
}

safe_config_val SEND_RECORDS APEL_SEND_RECORDS

/usr/share/condor-ce/condor_batch_blah.sh # Make the batch file (batch system job run times) and blah file (CE/Security data)
/usr/bin/apelparser                       # Read the blah and batch files in
if [ "$SEND_RECORDS" == "True" ]; then
    /usr/bin/apelclient                   # Join blah and batch records to make job records
    /usr/bin/ssmsend                      # Send job records into APEL system
fi

