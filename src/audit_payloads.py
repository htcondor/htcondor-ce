# audit_payload.py
#
# Writes logs of jobs starting and stopping based on ClassAd updates.
#
# This works automatically in a condor-ce if worker nodes have the environment
#   variable CONDORCE_COLLECTOR_HOST set to point to their site's condor-ce
#   server, if the jobs are run with condor glideins such as with GlideinWMS.
#
# Otherwise a job should use
#     condor_advertise -pool $CONDORCE_COLLECTOR_HOST:9619 UPDATE_STARTD_AD
#   at the start of the job and
#     condor_advertise -pool $CONDORCE_COLLECTOR_HOST:9619 INVALIDATE_STARTD_ADS
#   at the end of the job, sending to both comannds' standard input at least
#   these variables with format var = value, string values double-quoted:
#     Name (string) - name identifying the worker node, typically in the
#	format user@fully.qualified.domain.name
#     SlotID (integer) - slot identifier number on the worker node
#     MyType (string) - required to be set to the value of "Machine"
#   The condor_advertise at the begining of the message must also contain
#     GlobalJobId (string) - a globally unique identifier of the job
#     RemoteOwner (string) - a string identifying the owner of the job
#   and if the beginning of the message contains any of these they will
#   also be logged:
#     ClientMachine (string)
#     ProjectName (string)
#     Group (string)
#     x509UserProxyVOName (string)
#     x509userproxysubject (string)
#     x509UserProxyFQAN (string)
#     x509UserProxyEmail (string)
#
# There is one condor-ce configuration variable AUDIT_PAYLOAD_MAX_HOURS,
#   which is optional and indicates the maximum number of hours any job
#   is expected to run, default 72 hours (3 days).  After that time the
#   jobs will stop being tracked, in case a stop message was missed.
#
# Written by Dave Dykstra, June 2017
#

import htcondor
# I would use the simpler "time" module but it gets a load error
#   undefined symbol: PyExc_ValueError
from datetime import datetime

runningjobs = {}
firstidx = None
lastidx = None

if 'AUDIT_PAYLOAD_MAX_HOURS' in htcondor.param:
    maxjobhours = int(htcondor.param['AUDIT_PAYLOAD_MAX_HOURS'])
else:
    maxjobhours = 3 * 24
htcondor.log(htcondor.LogLevel.Audit,
    "Audit payload maximum job hours: %d" % maxjobhours)
maxjobsecs = maxjobhours * 60 * 60

# stop tracking a running job
def removerunningjob(idx):
    global runningjobs
    global firstidx
    global lastidx

    if idx not in runningjobs:
	# shouldn't happen, but just in case
	return

    # remove this job from the doubly-linked list
    thisjob = runningjobs[idx]
    if thisjob['previdx'] == None:
	firstidx = thisjob['nextidx']
    else:
	runningjobs[thisjob['previdx']]['nextidx'] = thisjob['nextidx']
    if thisjob['nextidx'] == None:
	lastidx = thisjob['nextidx']
    else:
	runningjobs[thisjob['nextidx']]['previdx'] = thisjob['previdx']

    # and remove it from the running jobs
    del runningjobs[idx]


# start tracking a running job
def addrunningjob(idx, globaljobid, now):
    global runningjobs
    global firstidx
    global lastidx

    if idx in runningjobs:
	# shouldn't happen, but just in case
	removerunningjob(idx)

    thisjob = {}
    thisjob['globaljobid'] = globaljobid
    thisjob['starttime'] = now

    # Use a doubly-linked list so jobs can stay sorted by start time,
    #  making checking for expired jobs order(1) instead of order(n).
    #  This is better because n (the number of running jobs) can be
    #  very large.
    # Append this job the end of the list.
    thisjob['previdx'] =  lastidx
    thisjob['nextidx'] =  None
    if lastidx != None:
	runningjobs[lastidx]['nextidx'] = idx
    lastidx = idx
    if firstidx == None:
	firstidx = idx 

    # and add it to the running jobs
    runningjobs[idx] = thisjob

# a job may be being stopped
def stopjob(info):
    global runningjobs
    if 'Name' not in info or 'SlotID' not in info:
	return
    idx = (info['Name'], info['SlotID'])
    if idx not in runningjobs:
	return
    loginfo = {}
    loginfo['Name'] = info['Name']
    loginfo['SlotID'] = info['SlotID']
    loginfo['GlobalJobId'] = runningjobs[idx]['globaljobid']
    htcondor.log(htcondor.LogLevel.Audit, "Job stop: %s" % loginfo)

    removerunningjob(idx)

# a job may be being started
def startjob(info):
    global maxjobsecs

    if 'Name' not in info or 'SlotID' not in info or 'GlobalJobId' not in info:
	return

    idx = (info['Name'], info['SlotID'])
    globaljobid = info['GlobalJobId']
    if idx in runningjobs:
	if globaljobid == runningjobs[idx]['globaljobid']:
	    # just an update to a running job, ignore
	    return
	# first stop the existing job, the slot is being reused
	stopjob(info)

    htcondor.log(htcondor.LogLevel.Audit, "Job start: %s" % info)
    now = datetime.now()
    addrunningjob(idx, globaljobid, now)

    # also look for expired jobs at the beginning of the list and stop them
    idx = firstidx
    while idx != None:
	thisjob = runningjobs[idx]
	delta = now - thisjob['starttime']
	deltasecs = int(delta.total_seconds())
	if deltasecs <= maxjobsecs:
	    break
	nextidx = thisjob['nextidx']
	loginfo = {}
	loginfo['Name'] = idx[0]
	loginfo['SlotID'] = idx[1]
	loginfo['GlobalJobId'] = thisjob['globaljobid']
	htcondor.log(htcondor.LogLevel.Audit,
	    "Cleaning up %d-second expired job: %s" % (deltasecs, loginfo))
	removerunningjob(idx)
	idx = nextidx


# this is the primary entry point called by the API
def update(command, ad):
    if command != "UPDATE_STARTD_AD":
        return
    if ad.get('State') == 'Unclaimed':
	stopjob(ad)  # stop previous job on this slot if any
	return
    info = {}
    keys = ['Name', 'SlotID', 'GlobalJobId',
	    'RemoteOwner', 'ClientMachine', 'ProjectName', 'Group',
	    'x509UserProxyVOName', 'x509userproxysubject', 'x509UserProxyEmail']
    for key in keys:
        if key in ad:
            info[key] = ad[key]
    startjob(info)


# this can also be called from the API when a job or slot is deleted
def invalidate(command, ad):
    if command != "INVALIDATE_STARTD_ADS":
        return
    stopjob(ad)
