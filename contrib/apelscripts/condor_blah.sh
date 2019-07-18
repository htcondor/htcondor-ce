#!/bin/bash

# "timestamp=2019-05-01 23:56:01" "userDN=/C=UK/O=eScience/OU=Liverpool/L=CSD/CN=stephen jones" "userFQAN=/dteam/Role=NULL/Capability=NULL" "ceID=hepgrid6.ph.liv.ac.uk:9619/hepgrid6.ph.liv.ac.uk-condor" "jobID=1.0_hepgrid6.ph.liv.ac.uk" "lrmsID=1_hepgrid6.ph.liv.ac.uk" "localUser=dteam001"

fail () {
    echo "$@" >&2
    exit 1
}

safe_config_val () {
    var=$1
    attr=$2
    val=$(condor_ce_config_val $attr) ||
    fail "Failed to retrieve CE configuration value '$attr'"
    eval "$var"='$val'
}

today=$(date -u --date='00:00:00 today' +%s)
yesterday=$(date -u --date='00:00:00 yesterday' +%s)

safe_config_val OUTPUT_DIR APEL_OUTPUT_DIR
OUTPUT_FILE="$OUTPUT_DIR/blah-$(date -u --date='yesterday' +%Y%m%d )-$(hostname -s)"

if [ ! -d $OUTPUT_DIR ] || [ ! -w $OUTPUT_DIR ]; then
    echo "Cannot write to $OUTPUT_DIR"
    exit 1
fi

# Build the filter for the history command
CONSTR="EnteredCurrentStatus >= $yesterday && EnteredCurrentStatus < $today && RemoteWallclockTime !=0"

safe_config_val CE_HOST APEL_CE_HOST
safe_config_val BATCH_HOST APEL_BATCH_HOST
safe_config_val CE_ID APEL_CE_ID

TZ=GMT condor_history -const "$CONSTR" \
 -format "\"timestamp=%s\" " 'formatTime(EnteredCurrentStatus, "%Y-%m-%d %H:%M:%S")' \
 -format "\"userDN=%s\" " x509userproxysubject \
 -format "\"userFQAN=%s\" " x509UserProxyFirstFQAN \
 -format "\"ceID=${CE_ID}\" " EMPTY \
 -format "\"jobID=%v_${CE_HOST}\" " RoutedFromJobId \
 -format "\"lrmsID=%v_${BATCH_HOST}\" " clusterId \
 -format "\"localUser=%s\"\n"  Owner  > $OUTPUT_FILE

