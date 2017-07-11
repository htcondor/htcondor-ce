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
import time
from collections import OrderedDict

runningjobs = OrderedDict()

if 'AUDIT_PAYLOAD_MAX_HOURS' in htcondor.param:
    maxjobhours = int(htcondor.param['AUDIT_PAYLOAD_MAX_HOURS'])
else:
    maxjobhours = 3 * 24
htcondor.log(htcondor.LogLevel.Audit,
    "Audit payload maximum job hours: %d" % maxjobhours)
maxjobsecs = maxjobhours * 60 * 60

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

    del runningjobs[idx]

# a job may be being started
def startjob(info):
    global maxjobsecs
    global runningjobs

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
    now = time.time()
    thisjob = {}
    thisjob['globaljobid'] = globaljobid
    thisjob['starttime'] = now
    runningjobs[idx] = thisjob

    # also look for expired jobs at the beginning of the list and stop them
    for idx in runningjobs:
	thisjob = runningjobs[idx]
	deltasecs = int(now - thisjob['starttime'])
	if deltasecs <= maxjobsecs:
	    break
	loginfo = {}
	loginfo['Name'] = idx[0]
	loginfo['SlotID'] = idx[1]
	loginfo['GlobalJobId'] = thisjob['globaljobid']
	htcondor.log(htcondor.LogLevel.Audit,
	    "Cleaning up %d-second expired job: %s" % (deltasecs, loginfo))
	del runningjobs[idx]


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
