#!/bin/sh

CONDOR_HISTORY=`condor_config_val HISTORY_HELPER`
OUTPUT_LOCATION=/var/lib/condor/accounting/

# Create a temporary accounting file name
today=$(date -u --date='00:00:00 today' +%s)
yesterday=$(date -u --date='00:00:00 yesterday' +%s)
output=batch-$(date -u --date='yesterday' +%Y%m%d )-$(hostname -s)

OUTPUT_FILE=$OUTPUT_LOCATION/$output

# Build the filter for the history command
CONSTR="EnteredCurrentStatus >= $yesterday && EnteredCurrentStatus < $today && RemoteWallclockTime !=0"

$CONDOR_HISTORY -constraint "$CONSTR" \
    -format "%s_hepgrid6.ph.liv.ac.uk|" ClusterId \
    -format "%s|" Owner \
    -format "%d|" RemoteWallClockTime \
    -format "%d|" RemoteUserCpu \
    -format "%d|" RemoteSysCpu \
    -format "%d|" JobStartDate \
    -format "%d|" EnteredCurrentStatus \
    -format "%d|" ResidentSetSize_RAW \
    -format "%d|" ImageSize_RAW \
    -format "%d|" RequestCpus \
    -format "%v|" MachineAttrRalScaling0 \
    -format "\n" EMPTY  | sed -e "s/undefined|$/1.0|/" > $OUTPUT_FILE
