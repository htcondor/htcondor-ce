#!/bin/bash

CONDOR_HISTORY=`condor_ce_config_val HISTORY_HELPER`
OUTPUT_LOCATION=/var/lib/condor/accounting/

# "timestamp=1544614059" "userDN=/C=UK/O=eScience/OU=Liverpool/L=CSD/CN=stephen jones" "userFQAN=/dteam/Role=NULL/Capability=NULL" "ceID=hepgrid6.ph.liv.ac.uk:9619/hepgrid6.ph.liv.ac.uk-condor" "jobID=1.0_hepgrid6.ph.liv.ac.uk" "lrmsID=1_hepgrid6.ph.liv.ac.uk" "localUser=dteam001"

today=$(date -u --date='00:00:00 today' +%s)
yesterday=$(date -u --date='00:00:00 yesterday' +%s)
output=blah-$(date -u --date='yesterday' +%Y%m%d )-$(hostname -s)

OUTPUT_FILE=$OUTPUT_LOCATION/$output

# Build the filter for the history command
CONSTR="EnteredCurrentStatus >= $yesterday && EnteredCurrentStatus < $today && RemoteWallclockTime !=0"

$CONDOR_HISTORY -const "$CONSTR" \
 -format "\"timestamp=%d\" " 'formatTime(EnteredCurrentStatus, "%Y-%m-%d %H:%M:%S")'  \
 -format "\"userDN=%s\" " x509userproxysubject \
 -format "\"userFQAN=%s\" " x509UserProxyFirstFQAN \
 -format "\"ceID=hepgrid6.ph.liv.ac.uk:9619/hepgrid6.ph.liv.ac.uk-condor\" " EMPTY \
 -format "\"jobID=%v_hepgrid6.ph.liv.ac.uk\" " RoutedFromJobId \
 -format "\"lrmsID=%v_hepgrid6.ph.liv.ac.uk\" " ClusterId \
 -format "\"localUser=%s\"\n"  Owner   \
   > $OUTPUT_FILE

