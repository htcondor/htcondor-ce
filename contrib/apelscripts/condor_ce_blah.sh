#!/bin/bash

CONDOR_HISTORY=`condor_ce_config_val HISTORY_HELPER`

# "timestamp=2019-05-01 23:56:01" "userDN=/C=UK/O=eScience/OU=Liverpool/L=CSD/CN=stephen jones" "userFQAN=/dteam/Role=NULL/Capability=NULL" "ceID=hepgrid6.ph.liv.ac.uk:9619/hepgrid6.ph.liv.ac.uk-condor" "jobID=1.0_hepgrid6.ph.liv.ac.uk" "lrmsID=1_hepgrid6.ph.liv.ac.uk" "localUser=dteam001"

today=$(date -u --date='00:00:00 today' +%s)
yesterday=$(date -u --date='00:00:00 yesterday' +%s)
output=blah-$(date -u --date='yesterday' +%Y%m%d )-$(hostname -s)

# Build the filter for the history command
CONSTR="EnteredCurrentStatus >= $yesterday && EnteredCurrentStatus < $today && RemoteWallclockTime !=0"

function die() { echo "$0 aborted when reading config"; exit 1; }
trap die ERR;
if [ $# -gt 0 ]; then
  source $1
fi
trap '' ERR

[[ -z "$CE_HOST" ]] && CE_HOST=`hostname`
[[ -z "$BATCH_HOST" ]] && BATCH_HOST=`hostname`
[[ -z "$CE_ID" ]] && CE_ID=${CE_HOST}:9619/${BATCH_HOST}-condor
[[ -z "$OUTPUT_LOCATION" ]] && OUTPUT_LOCATION=/var/lib/condor-ce/apel/

OUTPUT_FILE=$OUTPUT_LOCATION/$output

TZ=GMT $CONDOR_HISTORY -const "$CONSTR" \
 -format "\"timestamp=%s\" " 'formatTime(EnteredCurrentStatus, "%Y-%m-%d %H:%M:%S")' \
 -format "\"userDN=%s\" " x509userproxysubject \
 -format "\"userFQAN=%s\" " x509UserProxyFirstFQAN \
 -format "\"ceID=${CE_ID}\" " EMPTY \
 -format "\"jobID=%v_${CE_HOST}\" " RoutedFromJobId \
 -format "\"lrmsID=%v_${BATCH_HOST}\" " ClusterId \
 -format "\"localUser=%s\"\n"  Owner  > $OUTPUT_FILE

