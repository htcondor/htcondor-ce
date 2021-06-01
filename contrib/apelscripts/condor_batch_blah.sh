#!/bin/bash

fail () {
    echo "$@" >&2
    exit 1
}

safe_config_val () {
    var=$1
    attr=$2
    val=$(condor_config_val $attr) ||
    fail "Failed to retrieve Condor configuration value '$attr'"
    eval "$var"='$val'
}

safe_ce_config_val () {
    var=$1
    attr=$2
    val=$(condor_ce_config_val $attr) ||
    fail "Failed to retrieve CE configuration value '$attr'"
    eval "$var"='$val'
}

safe_ce_config_val OUTPUT_DIR APEL_OUTPUT_DIR
[[ -d $OUTPUT_DIR && -w $OUTPUT_DIR ]] || fail "Cannot write to $OUTPUT_DIR"
OUTPUT_DATETIME=`date '+%Y%m%d-%H%M'`

safe_config_val HISTORY_DIR PER_JOB_HISTORY_DIR
QUARANTINE_DIR=$HISTORY_DIR/quarantine
mkdir -p "$QUARANTINE_DIR"
[[ -d $QUARANTINE_DIR && -w $QUARANTINE_DIR ]] || fail "Cannot write to $QUARANTINE_DIR"

CONDOR_Q_EXTRA_ARGS=(-format "\n" EMPTY)
safe_ce_config_val SCALING_ATTR APEL_SCALING_ATTR
[[ -z $SCALING_ATTR ]] || CONDOR_Q_EXTRA_ARGS=(-format "%v|" "${SCALING_ATTR} isnt undefined ? ${SCALING_ATTR} : 1" "${CONDOR_Q_EXTRA_ARGS[@]}")

safe_ce_config_val BATCH_HOST APEL_BATCH_HOST
safe_ce_config_val CE_HOST APEL_CE_HOST
safe_ce_config_val CE_ID APEL_CE_ID

# Iterate over all the files in PER_JOB_HISTORY_DIR
for file in "$HISTORY_DIR"/*
do
    # If $file is a directory, skip it
    if [[ ! -f $file ]]; then
        continue
    fi

    # Check if $file is a valid history file by looking for a ClusterId value
    # If not found, assume the file is invalid and move to quarantine folder
    if [[ -z `condor_q -job $file -format "%s" GlobalJobId` ]]; then
        mv "$file" "$QUARANTINE_DIR"
        continue
    fi

    batch_record=`TZ=GMT condor_q -job "$file" \
        -format "%s|" GlobalJobId \
        -format "%s|" Owner \
        -format "%d|" RemoteWallClockTime \
        -format "%d|" RemoteUserCpu \
        -format "%d|" RemoteSysCpu \
        -format "%d|" JobStartDate \
        -format "%d|" EnteredCurrentStatus \
        -format "%d|" ResidentSetSize_RAW \
        -format "%d|" ImageSize_RAW \
        -format "%d|" RequestCpus \
        "${CONDOR_Q_EXTRA_ARGS[@]}"`
    OUTPUT_FILE="$OUTPUT_DIR/batch-${OUTPUT_DATETIME}-$(hostname -s)"
    echo "$batch_record" >> "$OUTPUT_FILE"

    blah_record=`TZ=GMT condor_q -job "$file" \
        -format "\"timestamp=%s\" " 'formatTime(EnteredCurrentStatus, "%Y-%m-%d %H:%M:%S")' \
        -format "\"userDN=%s\" " x509userproxysubject \
        -format "\"userFQAN=%s\" " x509UserProxyFirstFQAN \
        -format "\"ceID=${CE_ID}\" " EMPTY \
        -format "\"jobID=%v_${CE_HOST}\" " RoutedFromJobId \
        -format "\"lrmsID=%s\" " GlobalJobId \
        -format "\"localUser=%s\"\n" Owner`
    OUTPUT_FILE="$OUTPUT_DIR/blah-${OUTPUT_DATETIME}-$(hostname -s)"
    echo "$blah_record" >> "$OUTPUT_FILE"

    rm "$file"
done
