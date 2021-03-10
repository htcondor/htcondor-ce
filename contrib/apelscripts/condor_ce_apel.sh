#!/bin/bash
# sjones@hep.ph.liv.ac.uk, 2019
# Run the processes of an HTCondor-CE + HTCondor accounting run

safe_config_val () {
    var=$1
    attr=$2
    val=$(condor_ce_config_val $attr) ||
    fail "Failed to retrieve CE configuration value '$attr'"
    eval "$var"='$val'
}

safe_config_val USE_PUBLISHER APEL_USE_PUBLISHER

/usr/share/condor-ce/condor_blah.sh       # Make the blah file (CE/Security data)
/usr/share/condor-ce/condor_batch.sh      # Make the batch file (batch system job run times)
/usr/bin/apelparser                       # Read the blah and batch files in
if [ "$USE_PUBLISHER" == "False"]; then
    /usr/bin/apelclient                   # Join blah and batch records to make job records
    /usr/bin/ssmsend                      # Send job records into APEL system
fi
