#!/bin/bash

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

# Create a temporary accounting file name
today=$(date -u --date='00:00:00 today' +%s)
yesterday=$(date -u --date='00:00:00 yesterday' +%s)

OUTPUT_DIR="$(condor_ce_config_val APEL_OUTPUT_DIR)"
OUTPUT_FILE="$OUTPUT_DIR/batch-$(date -u --date='yesterday' +%Y%m%d )-$(hostname -s)"

[[ -d $OUTPUT_DIR && -w $OUTPUT_DIR ]] || fail "Cannot write to $OUTPUT_DIR"

# Build the filter for the history command
CONSTR="EnteredCurrentStatus >= $yesterday && EnteredCurrentStatus < $today && RemoteWallclockTime !=0"

HISTORY_EXTRA_ARGS=(-format "\n" EMPTY)
safe_config_val SCALING_ATTR APEL_SCALING_ATTR
[[ -z $SCALING_ATTR ]] || HISTORY_EXTRA_ARGS=(-format "%v|" "${SCALING_ATTR}" "${HISTORY_EXTRA_ARGS[@]}")

safe_config_val BATCH_HOST APEL_BATCH_HOST

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
    "${HISTORY_EXTRA_ARGS[@]}" > $OUTPUT_FILE
