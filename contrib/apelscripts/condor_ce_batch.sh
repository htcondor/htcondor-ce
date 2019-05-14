#!/bin/sh

# Create a temporary accounting file name
today=$(date -u --date='00:00:00 today' +%s)
yesterday=$(date -u --date='00:00:00 yesterday' +%s)
output=batch-$(date -u --date='yesterday' +%Y%m%d )-$(hostname -s)

# Build the filter for the history command
CONSTR="EnteredCurrentStatus >= $yesterday && EnteredCurrentStatus < $today && RemoteWallclockTime !=0"

function die() { echo "$0 aborted when reading config"; exit 1; }
trap die ERR;
if [ $# -gt 0 ]; then
  source $1
fi
trap '' ERR

[[ -z "$SCALING_ATTR" ]] && SCALING_ATTR=MachineAttrRalScaling0
[[ -z "$BATCH_HOST" ]] && BATCH_HOST=`hostname`
[[ -z "$OUTPUT_LOCATION" ]] && OUTPUT_LOCATION=/var/lib/condor-ce/apel/

OUTPUT_FILE=$OUTPUT_LOCATION/$output

TZ=GMT condor_history -constraint "$CONSTR" \
    -format "%s_${BATCH_HOST}|" ClusterId \
    -format "%s|" Owner \
    -format "%d|" RemoteWallClockTime \
    -format "%d|" RemoteUserCpu \
    -format "%d|" RemoteSysCpu \
    -format "%d|" JobStartDate \
    -format "%d|" EnteredCurrentStatus \
    -format "%d|" ResidentSetSize_RAW \
    -format "%d|" ImageSize_RAW \
    -format "%d|" RequestCpus \
    -format "%v|" ${SCALING_ATTR} \
    -format "\n" EMPTY  | sed -e "s/undefined|$/1.0|/" # > $OUTPUT_FILE

