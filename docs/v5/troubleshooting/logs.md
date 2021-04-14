Helpful Logs
============

MasterLog
---------

The HTCondor-CE master log tracks status of all of the other HTCondor daemons and thus contains valuable information if
they fail to start.

- Location: `/var/log/condor-ce/MasterLog`
- Key contents: Start-up, shut-down, and communication with other HTCondor daemons
- Increasing the debug level:
    1. Set the following value in `/etc/condor-ce/config.d/99-local.conf` on the CE host:

            MASTER_DEBUG = D_ALWAYS:2 D_CAT

    2. To apply these changes, reconfigure HTCondor-CE:

            :::console
            root@host # condor_ce_reconfig

### What to look for ###

Successful daemon start-up. 
The following line shows that the Collector daemon started successfully:

```
10/07/14 14:20:27 Started DaemonCore process "/usr/sbin/condor_collector -f -port 9619", pid and pgroup = 7318
```

SchedLog
--------

The HTCondor-CE schedd log contains information on all jobs that are submitted to the CE. 
It contains valuable information when trying to troubleshoot authentication issues.

- Location: `/var/log/condor-ce/SchedLog`
- Key contents:
    -   Every job submitted to the CE
    -   User authorization events
- Increasing the debug level:
    1. Set the following value in `/etc/condor-ce/config.d/99-local.conf` on the CE host:

            SCHEDD_DEBUG = D_ALWAYS:2 D_CAT

    2. To apply these changes, reconfigure HTCondor-CE:

            :::console
            root@host # condor_ce_reconfig

### What to look for ###

-   Job is submitted to the CE queue:

        10/07/14 16:52:17 Submitting new job 234.0

    In this example, the ID of the submitted job is `234.0`.

-   Job owner is authorized and mapped:

        10/07/14 16:52:17 Command=QMGMT_WRITE_CMD, peer=<131.225.154.68:42262>
        10/07/14 16:52:17 AuthMethod=GSI, AuthId=/DC=com/DC=DigiCert-Grid/O=Open Science Grid/OU=People/CN=Brian Lin 1047,
                          /GLOW/Role=NULL/Capability=NULL, <CondorId=glow@users.opensciencegrid.org>

    In this example, the job is authorized with the job’s proxy subject using GSI and is mapped to the `glow` user.

-   [User job submission fails](#jobs-fail-to-submit-to-the-ce) due to improper authentication or authorization:

        :::text
        08/30/16 16:52:56 DC_AUTHENTICATE: required authentication of 72.33.0.189
                          failed: AUTHENTICATE:1003:Failed to authenticate with any
                          method|AUTHENTICATE:1004:Failed to authenticate using GSI|GSI:5002:Failed to
                          authenticate because the remote (client) side was not able to acquire its
                          credentials.|AUTHENTICATE:1004:Failed to authenticate using FS|FS:1004:Unable to
                          lstat(/tmp/FS_XXXZpUlYa)
        08/30/16 16:53:12 PERMISSION DENIED to <gsi@unmapped>
                          from host 72.33.0.189 for command 60021 (DC_NOP_WRITE), access level WRITE:
                          reason: WRITE authorization policy contains no matching ALLOW entry for this
                          request; identifiers used for this host:
                          72.33.0.189,dyn-72-33-0-189.uwnet.wisc.edu, hostname size = 1, original ip
                          address = 72.33.0.189
        08/30/16 16:53:12 DC_AUTHENTICATE: Command not authorized, done

-   Missing negotiator:

        10/18/14 17:32:21 Can't find address for negotiator
        10/18/14 17:32:21 Failed to send RESCHEDULE to unknown daemon:

    Since HTCondor-CE does not manage any resources, it does not run a negotiator daemon by default and this error
    message is expected.
    In the same vein, you may see messages that there are 0 worker nodes:

        06/23/15 11:15:03 Number of Active Workers 0

-   Corrupted `job_queue.log`:

        02/07/17 10:55:49 WARNING: Encountered corrupt log record _654 (byte offset 5046225)
        02/07/17 10:55:49 103 1354325.0 PeriodicRemove ( StageInFinish > 0 ) 105
        02/07/17 10:55:49 Lines following corrupt log record _654 (up to 3):
        02/07/17 10:55:49 103 1346101.0 RemoteWallClockTime 116668.000000
        02/07/17 10:55:49 104 1346101.0 WallClockCheckpoint
        02/07/17 10:55:49 104 1346101.0 ShadowBday
        02/07/17 10:55:49 ERROR "Error: corrupt log record _654 (byte offset 5046225) occurred inside closed transaction,
                          recovery failed" at line 1080 in file /builddir/build/BUILD/condor-8.4.8/src/condor_utils/classad_log.cpp

    This means `/var/lib/condor-ce/spool/job_queue.log` has been corrupted and you will need to hand-remove the
    offending record by searching for the text specified after the `Lines following corrupt log record...` line.
    The most common culprit of the corruption is that the disk containing the `job_queue.log` has filled up.
    To avoid this problem, you can change the location of `job_queue.log` by setting `JOB_QUEUE_LOG` in
    `/etc/condor-ce/config.d/` to a path, preferably one on a large SSD.

JobRouterLog
------------

The HTCondor-CE job router log produced by the job router itself and thus contains valuable information when trying to
troubleshoot issues with job routing.

- Location: `/var/log/condor-ce/JobRouterLog`
- Key contents:
    -   Every attempt to route a job
    -   Routing success messages
    -   Job attribute changes, based on chosen route
    -   Job submission errors to an HTCondor batch system
    -   Corresponding job IDs on an HTCondor batch system
- Increasing the debug level:
    1. Set the following value in `/etc/condor-ce/config.d/99-local.conf` on the CE host:

            JOB_ROUTER_DEBUG = D_ALWAYS:2 D_CAT

    2. Apply these changes, reconfigure HTCondor-CE:

            :::console
            root@host # condor_ce_reconfig

### Known Errors ###

-   **(HTCondor batch systems only)** If you see the following error message:

        Can't find address of schedd

    This means that HTCondor-CE cannot communicate with your HTCondor batch system.
    Verify that the `condor` service is running on the HTCondor-CE host and is configured for your central manager.

-   **(HTCondor batch systems only)** If you see the following error message:

        JobRouter failure (src=2810466.0,dest=47968.0,route=MWT2_UCORE): giving up, because submitted job is still not in job queue mirror (submitted 605 seconds ago).  Perhaps it has been removed?

    Ensure that `condor_config_val SPOOL` and `condor_ce_config_val JOB_ROUTER_SCHEDD2_SPOOL` return the same value.
    If they don't, change the value of `JOB_ROUTER_SCHEDD2_SPOOL` in your HTCondor-CE configuration to match `SPOOL`
    from your HTCondor configuration.

-   If you have `D_ALWAYS:2` turned on for the job router, you will see errors like the following:

        06/12/15 14:00:28 HOOK_UPDATE_JOB_INFO not configured.

    You can safely ignore these.

### What to look for ###

-   Job is considered for routing:

        09/17/14 15:00:56 JobRouter (src=86.0,route=Local_LSF): found candidate job

    In parentheses are the original HTCondor-CE job ID (e.g., `86.0`) and the route (e.g., `Local_LSF`).

-   Job is successfully routed:

        09/17/14 15:00:57 JobRouter (src=86.0,route=Local_LSF): claimed job

-   Finding the corresponding job ID on your HTCondor batch system:

        09/17/14 15:00:57 JobRouter (src=86.0,dest=205.0,route=Local_Condor): claimed job

    In parentheses are the original HTCondor-CE job ID (e.g., `86.0`) and the resultant job ID on the HTCondor batch system (e.g., `205.0`)

-   If your job is not routed, there will not be any evidence of it within the log itself.
    To investigate why your jobs are not being considered for routing, use the
    [condor\_ce\_job\_router\_info](#condor_ce_job_router_info)
-   **HTCondor batch systems only**: The following error occurs when the job router daemon cannot submit the routed job:

        :::text
        10/19/14 13:09:15 Can't resolve collector condorce.example.com; skipping
        10/19/14 13:09:15 ERROR (pool condorce.example.com) Can't find address of schedd
        10/19/14 13:09:15 JobRouter failure (src=5.0,route=Local_Condor): failed to submit job

GridmanagerLog
--------------

The HTCondor-CE grid manager log tracks the submission and status of jobs on non-HTCondor batch systems. 
It contains valuable information when trying to troubleshoot jobs that have been routed but failed to complete. 
Details on how to read the Gridmanager log can be found on the
[HTCondor Wiki](https://htcondor-wiki.cs.wisc.edu/index.cgi/wiki?p=GridmanagerLog).

- Location: `/var/log/condor-ce/GridmanagerLog.<JOB-OWNER>`
- Key contents:
    -   Every attempt to submit a job to a batch system or other grid resource
    -   Status updates of submitted jobs
    -   Corresponding job IDs on non-HTCondor batch systems
- Increasing the debug level:
    1. Set the following value in `/etc/condor-ce/config.d/99-local.conf` on the CE host:

            MAX_GRIDMANAGER_LOG = 6h
            MAX_NUM_GRIDMANAGER_LOG = 8
            GRIDMANAGER_DEBUG = D_ALWAYS:2 D_CAT

    2. To apply these changes, reconfigure HTCondor-CE:

            :::console
            root@host # condor_ce_reconfig

### What to look for ###

-   Job is submitted to the batch system:

        09/17/14 09:51:34 [12997] (85.0) gm state change: GM_SUBMIT_SAVE -> GM_SUBMITTED

    Every state change the Gridmanager tracks should have the job ID in parentheses (i.e.=(85.0)).

-   Job status being updated:

        :::text
        09/17/14 15:07:24 [25543] (87.0) gm state change: GM_SUBMITTED -> GM_POLL_ACTIVE
        09/17/14 15:07:24 [25543] GAHP[25563] <- 'BLAH_JOB_STATUS 3 lsf/20140917/482046'
        09/17/14 15:07:24 [25543] GAHP[25563] -> 'S'
        09/17/14 15:07:25 [25543] GAHP[25563] <- 'RESULTS'
        09/17/14 15:07:25 [25543] GAHP[25563] -> 'R'
        09/17/14 15:07:25 [25543] GAHP[25563] -> 'S' '1'
        09/17/14 15:07:25 [25543] GAHP[25563] -> '3' '0' 'No Error' '4' '[ BatchjobId = "482046"; JobStatus = 4; ExitCode = 0; WorkerNode = "atl-prod08" ]'

    The first line tells us that the Gridmanager is initiating a status update and the following lines are the results.
    The most interesting line is the second highlighted section that notes the job ID on the batch system and its status.
    If there are errors querying the job on the batch system, they will appear here.

-   Finding the corresponding job ID on your non-HTCondor batch system:

        :::text
        09/17/14 15:07:24 [25543] (87.0) gm state change: GM_SUBMITTED -> GM_POLL_ACTIVE
        09/17/14 15:07:24 [25543] GAHP[25563] <- 'BLAH_JOB_STATUS 3 lsf/20140917/482046'

    On the first line, after the timestamp and PID of the Gridmanager process, you will find the CE’s job ID in
    parentheses, `(87.0)`.
    At the end of the second line, you will find the batch system, date, and batch system job id separated by slashes,
    `lsf/20140917/482046`.

-   Job completion on the batch system:

        09/17/14 15:07:25 [25543] (87.0) gm state change: GM_TRANSFER_OUTPUT -> GM_DONE_SAVE

SharedPortLog
-------------

The HTCondor-CE shared port log keeps track of all connections to all of the HTCondor-CE daemons other than the
collector. 
This log is a good place to check if experiencing connectivity issues with HTCondor-CE. More information can be found
[here](http://research.cs.wisc.edu/htcondor/manual/v8.6/3_9Networking_includes.html#SECTION00492000000000000000).

- Location: `/var/log/condor-ce/SharedPortLog`
- Key contents: Every attempt to connect to HTCondor-CE (except collector queries)
- Increasing the debug level:
    1. Set the following value in `/etc/condor-ce/config.d/99-local.conf` on the CE host:

            SHARED_PORT_DEBUG = D_ALWAYS:2 D_CAT

    2. To apply these changes, reconfigure HTCondor-CE:

            :::console
            root@host # condor_ce_reconfig

Messages Log
------------

The messages file can include output from lcmaps, which handles mapping of X.509 proxies to Unix usernames. 
If there are issues with the [authentication setup](../installation/htcondor-ce.md#configuring-authentication), the
errors may appear here.

- Location: `/var/log/messages`
- Key contents: User authentication

### What to look for ###

A user is mapped:

```
Oct 6 10:35:32 osgserv06 htondor-ce-llgt[12147]: Callout to "LCMAPS" returned local user (service condor): "osgglow01"
```

BLAHP Configuration File
------------------------

HTCondor-CE uses the BLAHP to submit jobs to your local non-HTCondor batch system using your batch system's client
tools.

- Location: `/etc/blah.config`
- Key contents:
    -   Locations of the batch system's client binaries and logs
    -   Location to save files that are submitted to the local batch system

You can also tell the BLAHP to save the files that are being submitted to the local batch system to `<DIR-NAME>` by
adding the following line:

```
blah_debug_save_submit_info=<DIR_NAME>
```

The BLAHP will then create a directory with the format `bl_*` for each submission to the local jobmanager with the
submit file and proxy used.

!!! note
    Whitespace is important so do not put any spaces around the = sign.
    In addition, the directory must be created and HTCondor-CE should have sufficient permissions to create directories
    within `<DIR_NAME>`.
