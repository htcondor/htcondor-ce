# audit_payload.py
#
# Writes logs of jobs starting and stopping based on ClassAd updates.
#
# This works automatically in a condor-ce if worker nodes have the environment
#   variable CONDORCE_COLLECTOR_HOST set to point to their site's condor-ce
#   server, if the jobs are run with condor glideins such as with GlideinWMS.
#
# Otherwise a job should use
#     condor_advertise -pool $CONDORCE_COLLECTOR_HOST UPDATE_STARTD_AD
#   at the start of the job and
#     condor_advertise -pool $CONDORCE_COLLECTOR_HOST INVALIDATE_STARTD_ADS
#   at the end of the job, sending to both comannds' standard input at least
#   these variables with format var = value, string values double-quoted:
#     Name (string) - name identifying the worker node, typically in the
#       format user@fully.qualified.domain.name
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

from htcondor import htcondor
import time
import re
from collections import OrderedDict

# Dictionary containing all tracked running jobs.
# Each entry is for a 'master', which is either a pilot job/glidein or
#  individual job.
# The index of the dictionary is a tuple of (mastername, slotid).
# The contents of each entry is a tuple of (starttime, jobs), where
#  jobs is a dictionary of individual job names running in that master
#  and each entry has a value of the GlobalJobId of that job.
runningmasters = OrderedDict()

if 'AUDIT_PAYLOAD_MAX_HOURS' in htcondor.param:
    maxjobhours = int(htcondor.param['AUDIT_PAYLOAD_MAX_HOURS'])
else:
    maxjobhours = 3 * 24
htcondor.log(htcondor.LogLevel.Audit,
    "Audit payload maximum job hours: %d" % maxjobhours)
maxjobsecs = maxjobhours * 60 * 60

# a job may be being stopped
def stopjob(info):
    global runningmasters
    if 'Name' not in info or 'SlotID' not in info:
        return
    name = info['Name']
    matchre = ""
    if 'GLIDEIN_MASTER_NAME' in info:
        idxname = info['GLIDEIN_MASTER_NAME']
        if idxname == name:
            # stop all jobs under this master
            matchre = '.*'
        else:
            # names of form "slotN@" stop that name and all "slotN_M@" names
            slotn = re.sub('^(slot[0-9]*)@.*', r'\1', name)
            if slotn != name:
                # match any name starting with slotN@ or slotN_
                matchre = '^' + slotn + '[@_]'
            # else take the default of matching only one name
    else:
        idxname = name
    idx = (idxname, info['SlotID'])
    if idx not in runningmasters:
        return

    runningjobs = runningmasters[idx][1]
    if matchre == "":
        # no match expression, just stop one
        if name not in runningjobs:
            return
        stopjobnames = [name]
    else:
        # select all jobs in this master
        stopjobnames = runningjobs.keys()
        if matchre != '.*':
            # restrict to the matching regular expression
            regex = re.compile(matchre)
            stopjobnames = filter(regex.search, stopjobnames)

    for stopjobname in stopjobnames:
        loginfo = {}
        loginfo['Name'] = stopjobname
        loginfo['SlotID'] = info['SlotID']
        loginfo['GlobalJobId'] = runningjobs[stopjobname]
        htcondor.log(htcondor.LogLevel.Audit, "Job stop: %s" % loginfo)
        del runningjobs[stopjobname]

    if len(runningjobs) == 0:
        del runningmasters[idx]

# a job may be being started
def startjob(info):
    global maxjobsecs
    global runningmasters

    if 'Name' not in info or 'SlotID' not in info or 'GlobalJobId' not in info:
        return

    name = info['Name']
    if 'GLIDEIN_MASTER_NAME' in info:
        # Glidein may be partitioned and sometimes tear down all contained
        #  slots at once, so need to track those slots together
        idxname = info['GLIDEIN_MASTER_NAME']
    else:
        idxname = name
    idx = (idxname, info['SlotID'])
    globaljobid = info['GlobalJobId']
    now = 0
    if idx in runningmasters:
        thismaster = runningmasters[idx]
        runningjobs = thismaster[1]
        if name in runningjobs:
            if globaljobid == runningjobs[name]:
                # just an update to a running job, ignore
                return
            # first stop the existing job, the slot is being reused
            stopjob(info)
	    # this may have removed the last job in thismaster, check again
    if idx not in runningmasters:
        # new master
        now = time.time()
        thismaster = (now, {})
        runningmasters[idx] = thismaster
    # add job to this master
    thismaster[1][name] = globaljobid

    printinfo = {}
    keys = ['Name', 'SlotID', 'GlobalJobId',
            'RemoteOwner', 'ClientMachine', 'ProjectName', 'Group',
            'x509UserProxyVOName', 'x509userproxysubject', 'x509UserProxyEmail']
    for key in keys:
        if key in info:
            printinfo[key] = info[key]
    htcondor.log(htcondor.LogLevel.Audit, "Job start: %s" % printinfo)

    if now == 0:
        return

    # also look for expired jobs at the beginning of the list and stop them
    for idx in runningmasters:
        thismaster = runningmasters[idx]
        deltasecs = int(now - thismaster[0])
        if deltasecs <= maxjobsecs:
            break
        loginfo = {}
        loginfo['SlotID'] = idx[1]
        runningjobs = thismaster[1]
        for jobname in runningjobs:
            loginfo['Name'] = jobname
            loginfo['GlobalJobId'] = runningjobs[jobname]
            htcondor.log(htcondor.LogLevel.Audit,
                "Cleaning up %d-second expired job: %s" % (deltasecs, loginfo))
        del runningmasters[idx]


# this is the primary entry point called by the API
def update(command, ad):
    if command != "UPDATE_STARTD_AD":
        return
    if ad.get('State') == 'Unclaimed':
        stopjob(ad)  # stop previous job on this slot if any
        return
    startjob(ad)


# this can also be called from the API when a job or slot is deleted
def invalidate(command, ad):
    if command != "INVALIDATE_STARTD_ADS":
        return
    stopjob(ad)
