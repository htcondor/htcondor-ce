Common Issues
=============

Known Issues
------------

### SUBMIT_ATTRS are not applied to jobs on the local HTCondor ###

If you are adding attributes to jobs submitted to your HTCondor pool with `SUBMIT_ATTRS`, these will *not* be applied to
jobs that are entering your pool from the HTCondor-CE. 
To get around this, you will want to add the attributes to your [job routes](../configuration/job-router-overview.md).
If the CE is the only entry point for jobs into your pool, you can get rid of `SUBMIT_ATTRS` on your backend. Otherwise,
you will have to maintain your list of attributes both in your list of routes and in your `SUBMIT_ATTRS`.

General Troubleshooting Items
-----------------------------

### Making sure packages are up-to-date

It is important to make sure that the HTCondor-CE and related RPMs are up-to-date.

``` console
root@host # yum update "htcondor-ce*" blahp condor
```

If you just want to see the packages to update, but do not want to perform the update now, answer `N` at the prompt.

### Verify package contents

If the contents of your HTCondor-CE packages have been changed, the CE may cease to function properly. To verify the
contents of your packages (ignoring changes to configuration files):

``` console
user@host $ rpm -q --verify htcondor-ce htcondor-ce-client blahp | grep -v '/var/' | awk '$2 != "c" {print $0}'
```

If the verification command returns output, this means that your packages have been changed. To fix this, you can
reinstall the packages:

``` console
user@host $ yum reinstall htcondor-ce htcondor-ce-client blahp
```

!!! note
    The reinstall command may place original versions of configuration files alongside the versions that you have modified.
    If this is the case, the reinstall command will notify you that the original versions will have an `.rpmnew` suffix.
    Further inspection of these files may be required as to whether or not you need to merge them into your current configuration.

### Verify clocks are synchronized

Like all GSI-based authentication, HTCondor-CE is sensitive to time skews. Make sure the clock on your CE is
synchronized using a utility such as `ntpd`. 
Additionally, HTCondor itself is sensitive to time skews on the NFS server.
If you see empty stdout / err being returned to the submitter, verify there is no NFS server time skew.

### Verify host cerificates and CRLs are valid

An expired host certificate or CRLs will cause various issues with GSI authentication. 
Verify that your host certificate is valid by running:

```console 
root@host # openssl x509 -in /etc/grid-security/hostcert.pem -noout -dates
```

Likewise, run the `fetch-crl` script to update your CRLs:

```console
root@host # fetch-crl
```

If updating CRLs fix your issues, make sure that the `fetch-crl-cron` and
`fetch-crl-boot` services are enabled and running.


HTCondor-CE Troubleshooting Items
---------------------------------

This section contains common issues you may encounter using HTCondor-CE and next actions to take when you do. 
Before troubleshooting, we recommend increasing the log level:

1.  Write the following into `/etc/condor-ce/config.d/99-local.conf` to increase the log level for all daemons:

        ALL_DEBUG = D_ALWAYS:2 D_CAT

2.  Ensure that the configuration is in place:

        root@host # condor_ce_reconfig

3.  Reproduce the issue

!!! note
    Before spending any time on troubleshooting, you should ensure that the state of configuration is as expected by
    running [condor\_ce\_reconfig](#condor_ce_reconfig).

### Daemons fail to start

If there are errors in your configuration of HTCondor-CE, this may cause some of its required daemons to fail to
startup. 
Check the following subsections in order:

**Symptoms**

Daemon startup failure may manifest in many ways, the following are few symptoms of the problem.

-   The service fails to start:

        :::console
        root@host # service condor-ce start
        Starting Condor-CE daemons: [ FAIL ]

-   `condor_ce_q` fails with a lengthy error message:

        :::console
        user@host $ condor_ce_q
        Error:

        Extra Info: You probably saw this error because the condor_schedd is not running
        on the machine you are trying to query. If the condor_schedd is not running, the
        Condor system will not be able to find an address and port to connect to and
        satisfy this request. Please make sure the Condor daemons are running and try
        again.

        Extra Info: If the condor_schedd is running on the machine you are trying to
        query and you still see the error, the most likely cause is that you have setup
        a personal Condor, you have not defined SCHEDD_NAME in your condor_config file,
        and something is wrong with your SCHEDD_ADDRESS_FILE setting. You must define
        either or both of those settings in your config file, or you must use the -name
        option to condor_q. Please see the Condor manual for details on SCHEDD_NAME and
        SCHEDD_ADDRESS_FILE.

**Next actions**

1.  **If the MasterLog is filled with `ERROR:SECMAN...TCP connection to collector...failed`:**
    This is likely due to a misconfiguration for a host with multiple network interfaces.
    Verify that you have followed the instructions in
    [this](../configuration/optional-configuration.md#configuring-for-multiple-network-interfaces) section of the
    optional configuration page.
2.  **If the MasterLog is filled with `DC_AUTHENTICATE` errors:**
    The HTCondor-CE daemons use the host certificate to authenticate with each other.
    Verify that your host certificate’s DN matches one of the regular expressions found in `/etc/condor-ce/condor_mapfile`.
3.  **If the SchedLog is filled with `Can’t find address for negotiator`:**
    You can ignore this error!
    The negotiator daemon is used in HTCondor batch systems to match jobs with resources but since HTCondor-CE does not
    manage any resources directly, it does not run one.


### Jobs fail to submit to the CE

If a user is having issues submitting jobs to the CE and you've ruled out general connectivity or firewalls as the
culprit, then you may have encountered an authentication or authorization issue. 
You may see error messages like the following in your [SchedLog](#schedlog):

```text
08/30/16 16:52:56 DC_AUTHENTICATE: required authentication of 72.33.0.189 failed: AUTHENTICATE:1003:Failed to authenticate with any method|AUTHENTICATE:1004:Failed to authenticate using GSI|GSI:5002:Failed to authenticate because the remote (client) side was not able to acquire its credentials.|AUTHENTICATE:1004:Failed to authenticate using FS|FS:1004:Unable to lstat(/tmp/FS_XXXZpUlYa)
08/30/16 16:53:12 PERMISSION DENIED to gsi@unmapped from host 72.33.0.189 for command 60021 (DC_NOP_WRITE), access level WRITE: reason: WRITE authorization policy contains no matching ALLOW entry for this request; identifiers used for this host: 72.33.0.189,dyn-72-33-0-189.uwnet.wisc.edu, hostname size = 1, original ip address = 72.33.0.189
08/30/16 16:53:12 DC_AUTHENTICATE: Command not authorized, done!
```

**Next actions**

1.  **Check voms-mapfile or grid-mapfile** and ensure that the user's DN or VOMS attributes are known to your
    [authentication method](../installation/htcondor-ce.md#configuring-authentication), and that the mapped users exist
    on your CE and cluster.
1.  **Check for lcmaps errors** in `/var/log/messages`
1.  **If you do not see helpful error messages in `/var/log/messages`,** adjust the debug level by adding `export
    LCMAPS_DEBUG_LEVEL=5` to `/etc/sysconfig/condor-ce`, restarting the condor-ce service, and checking
    `/var/log/messages` for errors again.

### Jobs stay idle on the CE

Check the following subsections in order, but note that jobs may take several minutes or longer to run if the CE is
busy.

#### Idle jobs on CE: Make sure the underlying batch system can run jobs

HTCondor-CE delegates jobs to your batch system, which is then responsible for matching jobs to worker nodes.
If you cannot manually submit jobs (e.g., `condor_submit`, `qsub`) on the CE host to your batch system, then HTCondor-CE
won't be able to either.

**Procedure**

1.  Manually create and submit a simple job (e.g., one that runs `sleep`)
2.  Check for errors in the submission itself
3.  Watch the job in the batch system queue (e.g., `condor_q`, `qstat`)
4.  If the job does not run, check for errors on the batch system

**Next actions**

Consult troubleshooting documentation or support avenues for your batch system.
Once you can run simple manual jobs on your batch system, try submitting to the HTCondor-CE again.

#### Idle jobs on CE: Is the job router handling the incoming job?

Jobs on the CE will be put on hold if they do not match any job routes after 30 minutes, but you can check a few things
if you suspect that the jobs are not being matched. 
Check if the JobRouter sees a job before that by looking at the [job router log](#jobrouterlog) and looking for the text
`src=<JOB-ID>…claimed job`.

**Next actions**

Use [condor\_ce\_job\_router\_info](#condor_ce_job_router_info) to see why your idle job does not match any routes

#### Idle jobs on CE: Verify correct operation between the CE and your local batch system

##### For HTCondor batch systems

HTCondor-CE submits jobs directly to an HTCondor batch system via the JobRouter, so any issues with the CE/local batch
system interaction will appear in the [JobRouterLog](#jobrouterlog).

**Next actions**

1.  Check the [JobRouterLog](#jobrouterlog) for failures.
2.  Verify that the local HTCondor is functional.
3.  Use [condor\_ce\_config\_val](#condor_ce_config_val) to verify that the `JOB_ROUTER_SCHEDD2_NAME`,
    `JOB_ROUTER_SCHEDD2_POOL`, and `JOB_ROUTER_SCHEDD2_SPOOL` configuration variables are set to the hostname of your
    CE, the hostname and port of your local HTCondor’s collector, and the location of your local HTCondor’s spool
    directory, respectively.
4.  Use `condor_config_val QUEUE_SUPER_USER_MAY_IMPERSONATE` and verify that it is set to `.*`.

##### For non-HTCondor batch systems

HTCondor-CE submits jobs to a non-HTCondor batch system via the Gridmanager, so any issues with the CE/local batch
system interaction will appear in the [GridmanagerLog](#gridmanagerlog). 
Look for `gm state change…` lines to figure out where the issures are occuring.

**Next actions**

1. **If you see failures in the GridmanagerLog during job submission:**
   Save the submit files by adding the appropriate entry to [blah.config](#blahp-configuration-file) and submit it
   [manually](#idle-jobs-on-ce-make-sure-the-underlying-batch-system-can-run-jobs) to the batch system.
   If that succeeds, make sure that the BLAHP knows where your binaries are located by setting the `<batch
   system>_binpath` in `/etc/blah.config`.
2. **If you see failures in the GridmanagerLog during queries for job status:**
   Query the resultant job with your batch system tools from the CE.
   If you can, the BLAHP uses scripts to query for status in `/usr/libexec/blahp/<batch system>_status.sh` (e.g.,
   `/usr/libexec/blahp/lsf_status.sh`) that take the argument `batch system/YYYMMDD/job ID` (e.g.,
   `lsf/20141008/65053`).
   Run the appropriate status script for your batch system and upon success, you should see the following output:

        :::console
        root@host # /usr/libexec/blahp/lsf_status.sh lsf/20141008/65053
        [ BatchjobId = "894862"; JobStatus = 4; ExitCode = 0; WorkerNode = "atl-prod08" ]

    If the script fails, [request help](#getting-help) from the OSG.


#### Idle jobs on CE: Verify ability to change permissions on key files

HTCondor-CE needs the ability to write and chown files in its `spool` directory and if it cannot, jobs will not run at
all. 
Spool permission errors can appear in the [SchedLog](#schedlog) and the [JobRouterLog](#jobrouterlog).

**Symptoms**

```
09/17/14 14:45:42 Error: Unable to chown '/var/lib/condor-ce/spool/1/0/cluster1.proc0.subproc0/env' from 12345 to 54321
```

**Next actions**

- As root, try to change ownership of the file or directory in question. If the file does not exist, a parent directory
  may have improper permissions.
- Verify that there aren't any underlying file system issues in the specified location

### Jobs stay idle on a remote host submitting to the CE

If you are submitting your job from a separate submit host to the CE, it stays idle in the queue forever, and you do not
see a resultant job in the CE's queue, this means that your job cannot contact the CE for submission or it is not
authorized to run there. 
Note that jobs may take several minutes or longer if the CE is busy.

#### Remote idle jobs: Can you contact the CE?

To check basic connectivity to a CE, use [condor\_ce\_ping](#condor_ce_ping):

**Symptoms**

``` console
user@host $ condor_ping -verbose -name condorce.example.com -pool condorce.example.com:9619 WRITE
ERROR: couldn't locate condorce.example.com!
```

**Next actions**

1.  Make sure that the HTCondor-CE daemons are running with [condor\_ce\_status](#condor_ce_status).
2.  Verify that your CE is reachable from your submit host, replacing `condorce.example.com` with the hostname of your CE:

        :::console
        user@host $ ping condorce.example.com

#### Remote idle jobs: Are you authorized to run jobs on the CE?

The CE will only run jobs from users that authenticate through the
[HTCondor-CE configuration](../installation/htcondor-ce.md#configuring-authentication).
You can use [condor\_ce\_ping](#condor_ce_ping) to check if you are authorized and what user your proxy is being mapped
to.

**Symptoms**

``` console
user@host $ condor_ping -verbose -name condorce.example.com -pool condorce.example.com:9619 WRITE
Remote Version:              $CondorVersion: 8.0.7 Sep 24 2014 $
Local  Version:              $CondorVersion: 8.0.7 Sep 24 2014 $
Session ID:                  condorce:3343:1412790611:0
Instruction:                 WRITE
Command:                     60021
Encryption:                  none
Integrity:                   MD5
Authenticated using:         GSI
All authentication methods:  GSI
Remote Mapping:              gsi@unmapped
Authorized:                  FALSE
```

Notice the failures in the above message: `Remote Mapping: gsi@unmapped` and `Authorized: FALSE`

**Next actions**

1.  Verify that an [authentication method](../installation/htcondor-ce.md#configuring-authentication) is set up on the CE
2.  Verify that your user DN is mapped to an existing system user

### Jobs go on hold

Jobs will be put on held with a `HoldReason` attribute that can be inspected with [condor\_ce\_q](#condor_ce_q):

``` console
user@host $ condor_ce_q -l <JOB-ID> -attr HoldReason
HoldReason = "CE job in status 5 put on hold by SYSTEM_PERIODIC_HOLD due to no matching routes, route job limit, or route failure threshold."
```

#### Held jobs: no matching routes, route job limit, or route failure threshold

Jobs on the CE will be put on hold if they are not claimed by the job router within 30 minutes.
The most common cases for this behavior are as follows:

- **The job does not match any job routes:**
  use [condor\_ce\_job\_router\_info](#condor_ce_job_router_info) to see why your idle job does not match any
  [routes](../configuration/job-router-overview.md#how-jobs-match-to-routes).
- **The route(s) that the job matches to are full:**
  See [limiting the number of jobs](../configuration/writing-job-routes.md#limiting-the-number-of-jobs).
- **The job router is throttling submission to your batch system due to submission failures:**
  See the HTCondor manual for [FailureRateThreshold](http://research.cs.wisc.edu/htcondor/manual/v8.6/5_4HTCondor_Job.html#55958).
  Check for errors in the [JobRouterLog](#jobrouterlog) or [GridmanagerLog](#gridmanagerlog) for HTCondor and
  non-HTCondor batch systems, respectively.

#### Held jobs: Missing/expired user proxy

HTCondor-CE requires a valid user proxy for each job that is submitted. 
You can check the status of your proxy with the following

``` console
user@host $ voms-proxy-info -all
```

**Next actions**

Ensure that the owner of the job generates their proxy with `voms-proxy-init`.

#### Held jobs: Invalid job universe

The HTCondor-CE only accepts jobs that have `universe` in their submit files set to `vanilla`, `standard`, `local`, or
`scheduler`. 
These universes also have corresponding integer values that can be found in the
[HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/12_Appendix_A.html#104736).

**Next actions**

1.  Ensure jobs submitted locally, from the CE host, are submitted with `universe = vanilla`
2.  Ensure jobs submitted from a remote submit point are submitted with:

        universe = grid
        grid_resource = condor condorce.example.com condorce.example.com:9619

    replacing `condorce.example.com` with the hostname of the CE.

### Identifying the corresponding job ID on the local batch system

When troubleshooting interactions between your CE and your local batch system, you will need to associate the CE job ID
and the resultant job ID on the batch system. 
The methods for finding the resultant job ID differs between batch systems.

#### HTCondor batch systems

1.  To inspect the CE’s job ad, use [condor\_ce\_q](#condor_ce_q) or [condor\_ce\_history](#condor_ce_history):

    - Use `condor_ce_q` if the job is still in the CE’s queue:

            :::console
            user@host $ condor_ce_q <JOB-ID> -af RoutedToJobId

    - Use `condor_ce_history` if the job has left the CE’s queue:

            :::console
            user@host $ condor_ce_history <JOB-ID> -af RoutedToJobId

2.  Parse the [JobRouterLog](#jobrouterlog) for the CE’s job ID.

#### Non-HTCondor batch systems

When HTCondor-CE records the corresponding batch system job ID, it is written in the form `<BATCH-SYSTEM>/<DATE>/<JOB
ID>`:

```
lsf/20141206/482046
```

1.  To inspect the CE’s job ad, use [condor\_ce\_q](#condor_ce_q):

        :::console
        user@host $ condor_ce_q <JOB-ID> -af GridJobId

2.  Parse the [GridmanagerLog](#gridmanagerlog) for the CE’s job ID.

### Jobs removed from the local HTCondor pool become resubmitted (HTCondor batch systems only)

By design, HTCondor-CE will resubmit jobs that have been removed from the underlying HTCondor pool. 
Therefore, to remove misbehaving jobs, they will need to be removed on the CE level following these steps:

1.  Identify the misbehaving job ID in your batch system queue
2.  Find the job's corresponding CE job ID:

        :::console
        user@host $ condor_q <JOB-ID> -af RoutedFromJobId

3.  Use `condor_ce_rm` to remove the CE job from the queue

### Missing HTCondor tools

Most of the HTCondor-CE tools are just wrappers around existing HTCondor tools that load the CE-specific config. 
If you are trying to use HTCondor-CE tools and you see the following error:

``` console
user@host $ condor_ce_job_router_info
/usr/bin/condor_ce_job_router_info: line 6: exec: condor_job_router_info: not found
```

This means that the `condor_job_router_info` (note this is not the CE version), is not in your `PATH`.

**Next Actions**

1.  Either the condor RPM is missing or there are some other issues with it (try `rpm --verify condor`).
2.  You have installed HTCondor in a non-standard location that is not in your `PATH`.
3.  The `condor_job_router_info` tool itself wasn't available until Condor-8.2.3-1.1 (available in osg-upcoming).
