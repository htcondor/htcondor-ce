#!/bin/bash

# "timestamp=2019-05-01 23:56:01" "userDN=/C=UK/O=eScience/OU=Liverpool/L=CSD/CN=stephen jones" "userFQAN=/dteam/Role=NULL/Capability=NULL" "ceID=hepgrid6.ph.liv.ac.uk:9619/hepgrid6.ph.liv.ac.uk-condor" "jobID=1.0_hepgrid6.ph.liv.ac.uk" "lrmsID=1_hepgrid6.ph.liv.ac.uk" "localUser=dteam001"

safe_config_val () {
    condor_ce_config_val $1 || echo "Failed to retrieve CE configuration value '$1'" && exit 1
}

today=$(date -u --date='00:00:00 today' +%s)
yesterday=$(date -u --date='00:00:00 yesterday' +%s)

OUTPUT_DIR="$(safe_config_val APEL_OUTPUT_DIR)"
OUTPUT_FILE="$OUTPUT_DIR/blah-$(date -u --date='yesterday' +%Y%m%d )-$(hostname -s)"

if [ ! -d $OUTPUT_DIR ] || [ ! -w $OUTPUT_DIR ]; then
    echo "Cannot write to $OUTPUT_DIR"
    exit 1
fi

# Build the filter for the history command
CONSTR="CompletionDate >= $yesterday && CompletionDate < $today "

CE_HOST=$(safe_config_val APEL_CE_HOST)
BATCH_HOST=$(safe_config_val APEL_BATCH_HOST)
CE_ID=$(safe_config_val APEL_CE_ID)

TZ=GMT condor_ce_history -const "$CONSTR" \
 -format "\"timestamp=%s\" " 'formatTime(CompletionDate, "%Y-%m-%d %H:%M:%S")' \
 -format "\"userDN=%s\" " x509userproxysubject \
 -format "\"userFQAN=%s\" " x509UserProxyFirstFQAN \
 -format "\"ceID=${CE_ID}\" " EMPTY \
 -format "\"jobID=%v_${CE_HOST}\" " 'split(GlobalJobId,"\#")[1]' \
 -format "\"lrmsID=%v_${BATCH_HOST}\" " 'split(RoutedToJobId,"\.")[0]' \
 -format "\"localUser=%s\"\n"  Owner  > $OUTPUT_FILE

TZ=GMT condor_ce_q   -const "$CONSTR" \
 -format "\"timestamp=%s\" " 'formatTime(CompletionDate, "%Y-%m-%d %H:%M:%S")' \
 -format "\"userDN=%s\" " x509userproxysubject \
 -format "\"userFQAN=%s\" " x509UserProxyFirstFQAN \
 -format "\"ceID=${CE_ID}\" " EMPTY \
 -format "\"jobID=%v_${CE_HOST}\" " 'split(GlobalJobId,"\#")[1]' \
 -format "\"lrmsID=%v_${BATCH_HOST}\" " 'split(RoutedToJobId,"\.")[0]' \
 -format "\"localUser=%s\"\n"  Owner  >> $OUTPUT_FILE

