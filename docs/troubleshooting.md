HTCondor-CE Troubleshooting Guide
=================================

In this document, you will find a collection of files and commands to help troubleshoot HTCondor-CE along with a list of
common issues with suggested troubleshooting steps.

Known Issues
------------

### SUBMIT_EXPRS are not applied to jobs on the local HTCondor ###

If you are adding attributes to jobs submitted to your HTCondor pool with `SUBMIT_EXPRS`, these will *not* be applied to
jobs that are entering your pool from the HTCondor-CE. 
To get around this, you will want to add the attributes to your [job routes](job-router-recipes). 
If the CE is the only entry point for jobs into your pool, you can get rid of `SUBMIT_EXPRS` on your backend. Otherwise,
you will have to maintain your list of attributes both in your list of routes and in your `SUBMIT_EXPRS`.

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
    The reinstall command may place original versions of configuration files alongside the versions that you have modified. If this is the case, the reinstall command will notify you that the original versions will have an `.rpmnew` suffix. Further inspection of these files may be required as to whether or not you need to merge them into your current configuration.

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
    Before spending any time on troubleshooting, you should ensure that the state of configuration is as expected by running [condor\_ce\_reconfig](#condor_ce_reconfig).

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

1.  **If the MasterLog is filled with `ERROR:SECMAN...TCP connection to collector...failed`:** This is likely due to a misconfiguration for a host with multiple network interfaces. Verify that you have followed the instructions in [this](install-htcondor-ce#networking) section of the install guide.
2.  **If the MasterLog is filled with `DC_AUTHENTICATE` errors:** The HTCondor-CE daemons use the host certificate to authenticate with each other. Verify that your host certificate’s DN matches one of the regular expressions found in `/etc/condor-ce/condor_mapfile`.
3.  **If the SchedLog is filled with `Can’t find address for negotiator`:** You can ignore this error! The negotiator daemon is used in HTCondor batch systems to match jobs with resources but since HTCondor-CE does not manage any resources directly, it does not run one.


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
    [authentication method](install-htcondor-ce#configuring-authentication), and that the mapped users exist
    on your CE and cluster.
1.  **Check for lcmaps errors** in `/var/log/messages`
1.  **If you do not see helpful error messages in `/var/log/messages`,** adjust the debug level by adding `export LCMAPS_DEBUG_LEVEL=5` to `/etc/sysconfig/condor-ce`, restarting the condor-ce service, and checking `/var/log/messages` for errors again.

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
3.  Use [condor\_ce\_config\_val](#condor_ce_config_val) to verify that the `JOB_ROUTER_SCHEDD2_NAME`, `JOB_ROUTER_SCHEDD2_POOL`, and `JOB_ROUTER_SCHEDD2_SPOOL` configuration variables are set to the hostname of your CE, the hostname and port of your local HTCondor’s collector, and the location of your local HTCondor’s spool directory, respectively.
4.  Use `condor_config_val QUEUE_SUPER_USER_MAY_IMPERSONATE` and verify that it is set to `.*`.

##### For non-HTCondor batch systems

HTCondor-CE submits jobs to a non-HTCondor batch system via the Gridmanager, so any issues with the CE/local batch
system interaction will appear in the [GridmanagerLog](#gridmanagerlog). 
Look for `gm state change…` lines to figure out where the issures are occuring.

**Next actions**

1. **If you see failures in the GridmanagerLog during job submission:** Save the submit files by adding the appropriate entry to [blah.config](#blahp-configuration-file) and submit it [manually](#idle-jobs-on-ce-make-sure-the-underlying-batch-system-can-run-jobs) to the batch system. If that succeeds, make sure that the BLAHP knows where your binaries are located by setting the `<batch system>_binpath` in `/etc/blah.config`.
2. **If you see failures in the GridmanagerLog during queries for job status:** Query the resultant job with your batch system tools from the CE. If you can, the BLAHP uses scripts to query for status in `/usr/libexec/blahp/<batch system>_status.sh` (e.g., `/usr/libexec/blahp/lsf_status.sh`) that take the argument `batch system/YYYMMDD/job ID` (e.g., `lsf/20141008/65053`). Run the appropriate status script for your batch system and upon success, you should see the following output:

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

- As root, try to change ownership of the file or directory in question. If the file does not exist, a parent directory may have improper permissions.
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

The CE will only accept jobs from users that authenticate via [LCMAPS VOMS](/security/lcmaps-voms-authentication).
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

1.  Verify that an [authentication method](install-htcondor-ce#configuring-authentication) is set up on the CE
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
  [routes](/compute-element/job-router-recipes#how-job-routes-are-constructed).
- **The route(s) that the job matches to are full:**
  See [limiting the number of jobs](/compute-element/job-router-recipes#limiting-the-number-of-jobs).
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
These universes also have corresponding integer values that can be found in the [HTCondor
manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/12_Appendix_A.html#104736).

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

HTCondor-CE Troubleshooting Tools
---------------------------------

HTCondor-CE has its own separate set of of the HTCondor tools with **ce** in the name (i.e., `condor_ce_submit` vs
`condor_submit`). 
Some of the the commands are only for the CE (e.g., `condor_ce_run` and `condor_ce_trace`) but many of them are just
HTCondor commands configured to interact with the CE (e.g., `condor_ce_q`, `condor_ce_status`). 
It is important to differentiate the two: `condor_ce_config_val` will provide configuration values for your HTCondor-CE
while
`condor_config_val` will provide configuration values for your HTCondor batch system. 
If you are not running an HTCondor batch system, the non-CE commands will return errors.

### condor_ce_trace

#### Usage

`condor_ce_trace` is a useful tool for testing end-to-end job submission. It contacts both the CE’s Schedd and Collector daemons to verify your permission to submit to the CE, displays the submit script that it submits to the CE, and tracks the resultant job.

!!! note
    You must have generated a proxy (e.g., `voms-proxy-init`) and your DN must be added to your [chosen authentication method](install-htcondor-ce#configuring-authentication).

``` console
user@host $ condor_ce_trace condorce.example.com
```

Replacing the `condorce.example.com` with the hostname of the CE. 
If you are familiar with the output of condor commands, the command also takes a `--debug` option that displays verbose
condor output.

#### Troubleshooting

1.  **If the command fails with “Failed ping…”:** Make sure that the HTCondor-CE daemons are running on the CE
2.  **If you see “gsi@unmapped” in the “Remote Mapping” line:** Either your credentials are not mapped on the CE or authentication is not set up at all. To set up authentication, refer to our [installation document](install-htcondor-ce#configuring-authentication).
3.  **If the job submits but does not complete:** Look at the status of the job and perform the relevant [troubleshooting steps](#htcondor-ce-troubleshooting-items).

### condor_ce_host_network_check

#### Usage

`condor_ce_host_network_check` is a tool for testing an HTCondor-CE's networking configuration:

```console
root@host # condor_ce_host_network_check
Starting analysis of host networking for HTCondor-CE
System hostname: fermicloud360.fnal.gov
FQDN matches hostname
Forward resolution of hostname fermicloud360.fnal.gov is 131.225.155.96.
Backward resolution of IPv4 131.225.155.96 is fermicloud360.fnal.gov.
Forward and backward resolution match!
HTCondor is considering all network interfaces and addresses.
HTCondor would pick address of 131.225.155.96 as primary address.
HTCondor primary address 131.225.155.96 matches system preferred address.
Host network configuration should work with HTCondor-CE
```

#### Troubleshooting

If the tool reports that `Host network configuration not expected to work with HTCondor-CE`, ensure that forward and
reverse DNS resolution return the public IP and hostname.

### condor_ce_run

#### Usage

Similar to `globus-job-run`, `condor_ce_run` is a tool that submits a simple job to your CE, so it is useful for quickly
submitting jobs through your CE. 
To submit a job to the CE and run the `env` command on the remote batch system:

!!! note
    You must have generated a proxy (e.g., `voms-proxy-init`) and your DN must be added to your [chosen authentication method](install-htcondor-ce#configuring-authentication).

``` console
user@host $ condor_ce_run -r condorce.example.com:9619 /bin/env
```

Replacing the `condorce.example.com` with the hostname of the CE. 
If you are troubleshooting an HTCondor-CE that you do not have a login for and the CE accepts local universe jobs, you
can run commands locally on the CE with `condor_ce_run` with the `-l` option. 
The following example outputs the JobRouterLog of the CE in question:

``` console
user@host $ condor_ce_run -lr condorce.example.com:9619 cat /var/log/condor-ce/JobRouterLog
```

Replacing the `condorce.example.com` text with the hostname of the CE. 
To disable this feature on your CE, consult
[this](install-htcondor-ce#limiting-or-disabling-locally-running-jobs-on-the-ce) section of the install documentation.

#### Troubleshooting

1.  **If you do not see any results:** `condor_ce_run` does not display results until the job completes on the CE, which may take several minutes or longer if the CE is busy. In the meantime, can use [condor\_ce\_q](#condor_ce_q) in a separate terminal to track the job on the CE. If you never see any results, use [condor\_ce\_trace](#condor_ce_trace) to pinpoint errors.
2.  **If you see an error message that begins with “Failed to…”:** Check connectivity to the CE with [condor\_ce\_trace](#condor_ce_trace) or [condor\_ce\_ping](#condor_ce_ping)

### condor_ce_submit

See the [submitting to HTCondor-CE](submit-htcondor-ce) document for details.

### condor_ce_ping

#### Usage

Use the following `condor_ce_ping` command to test your ability to submit jobs to an HTCondor-CE, replacing
`condorce.example.com` with the hostname of your CE:

``` console
user@host $ condor_ce_ping -verbose -name condorce.example.com -pool condorce.example.com:9619 WRITE
```

The following shows successful output where I am able to submit jobs (`Authorized: TRUE`) as the glow user (`Remote
Mapping: glow@users.opensciencegrid.org`):

``` console
Remote Version:              $CondorVersion: 8.0.7 Sep 24 2014 $
Local  Version:              $CondorVersion: 8.0.7 Sep 24 2014 $
Session ID:                  condorce:27407:1412286981:3
Instruction:                 WRITE
Command:                     60021
Encryption:                  none
Integrity:                   MD5
Authenticated using:         GSI
All authentication methods:  GSI
Remote Mapping:              glow@users.opensciencegrid.org
Authorized:                  TRUE
```

!!! note
    If you run the `condor_ce_ping` command on the CE that you are testing, omit the `-name` and `-pool` options. `condor_ce_ping` takes the same arguments as `condor_ping` and is documented in the [HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_ping.html).

#### Troubleshooting

1.  **If you see “ERROR: couldn’t locate (null)”**, that means the HTCondor-CE schedd (the daemon that schedules jobs) cannot be reached. To track down the issue, increase debugging levels on the CE:

        MASTER_DEBUG = D_ALWAYS:2 D_CAT
        SCHEDD_DEBUG = D_ALWAYS:2 D_CAT

    Then look in the [MasterLog](#masterlog) and [SchedLog](#schedlog) for any errors.

2.  **If you see “gsi@unmapped” in the “Remote Mapping” line**, this means that either your credentials are not mapped on the CE or that authentication is not set up at all. To set up authentication, refer to our [installation document](install-htcondor-ce#configuring-authentication).


### condor_ce_q

#### Usage

`condor_ce_q` can display job status or specific job attributes for jobs that are still in the CE’s queue. To list jobs that are queued on a CE:

``` console
user@host $ condor_ce_q -name condorce.example.com -pool condorce.example.com:9619
```

To inspect the full ClassAd for a specific job, specify the `-l` flag and the job ID:

``` console
user@host $ condor_ce_q -name condorce.example.com -pool condorce.example.com:9619 -l <JOB-ID>
```

!!! note
    If you run the `condor_ce_q` command on the CE that you are testing, omit the `-name` and `-pool` options. `condor_ce_q` takes the same arguments as `condor_q` and is documented in the [HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_q.html).

#### Troubleshooting

If the jobs that you are submiting to a CE are not completing, `condor_ce_q` can tell you the status of your jobs.

1.  **If the schedd is not running:** You will see a lengthy message about being unable to contact the schedd. To track down the issue, increase the debugging levels on the CE with:

        MASTER_DEBUG = D_ALWAYS:2 D_CAT
        SCHEDD_DEBUG = D_ALWAYS:2 D_CAT

    To apply these changes, reconfigure HTCondor-CE:

        :::console
        root@host # condor_ce_reconfig

    Then look in the [MasterLog](#masterlog) and [SchedLog](#schedlog) on the CE for any errors.

1.  **If there are issues with contacting the collector:** You will see the following message:

        :::console
        user@host $ condor_ce_q -pool ce1.accre.vanderbilt.edu -name ce1.accre.vanderbilt.edu

        -- Failed to fetch ads from: <129.59.197.223:9620?sock`33630_8b33_4> : ce1.accre.vanderbilt.edu

    This may be due to network issues or bad HTCondor daemon permissions. To fix the latter issue, ensure that the `ALLOW_READ` configuration value is not set:

        :::console
        user@host $ condor_ce_config_val -v ALLOW_READ
        Not defined: ALLOW_READ

    If it is defined, remove it from the file that is returned in the output.

2.  **If a job is held:** There should be an accompanying `HoldReason` that will tell you why it is being held. The `HoldReason` is in the job’s ClassAd, so you can use the long form of `condor_ce_q` to extract its value:

        :::console
        user@host $ condor_ce_q -name condorce.example.com -pool condorce.example.com:9619 -l <Job ID> | grep HoldReason

3.  **If a job is idle:** The most common cause is that it is not matching any routes in the CE’s job router. To find out whether this is the case, use the [condor\_ce\_job\_router\_info](#condor_ce_job_router_info).


### condor_ce_history

#### Usage

`condor_ce_history` can display job status or specific job attributes for jobs that have that have left the CE’s queue. To list jobs that have run on the CE:

``` console
user@host $ condor_ce_history -name condorce.example.com -pool condorce.example.com:9619
```

To inspect the full ClassAd for a specific job, specify the `-l` flag and the job ID:

``` console
user@host $ condor_ce_history -name condorce.example.com -pool condorce.example.com:9619 -l <Job ID>
```

!!! note
    If you run the `condor_ce_history` command on the CE that you are testing, omit the `-name` and `-pool` options. `condor_ce_history` takes the same arguments as `condor_history` and is documented in the [HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_history.html).


### condor_ce_job_router_info

#### Usage

Use the `condor_ce_job_router_info` command to help troubleshoot your routes and how jobs will match to them. 
To see all of your routes (the output is long because it combines your routes with the
[JOB\_ROUTER\_DEFAULTS](job-router-recipes#job_router_defaults) configuration variable):

``` console
root@host # condor_ce_job_router_info -config
```

To see how the job router is handling a job that is currently in the CE’s queue, analyze the output of `condor_ce_q`
(replace the `<JOB-ID>` with the job ID that you are interested in):

``` console
root@host # condor_ce_q -l <JOB-ID> | condor_ce_job_router_info -match-jobs -ignore-prior-routing -jobads -
```

To inspect a job that has already left the queue, use `condor_ce_history` instead of `condor_ce_q`:

``` console
root@host # condor_ce_history -l <JOB-ID> | condor_ce_job_router_info -match-jobs -ignore-prior-routing -jobads -
```

!!! note
    If the proxy for the job has expired, the job will not match any routes. To work around this constraint:

``` console
root@host # condor_ce_history -l <JOB-ID> | sed "s/^\(x509UserProxyExpiration\) = .*/\1 = `date +%s --date '+1 sec'`/" | condor_ce_job_router_info -match-jobs -ignore-prior-routing -jobads -
```

Alternatively, you can provide a file containing a job’s ClassAd as the input and edit attributes within that file:

``` console
root@host # condor_ce_job_router_info -match-jobs -ignore-prior-routing -jobads <JOBAD-FILE>
```

#### Troubleshooting

1.  **If the job does not match any route:** You can identify this case when you see `0 candidate jobs found` in the `condor_job_router_info` output. This message means that, when compared to your job’s ClassAd, the Umbrella constraint does not evaluate to `true`. When troubleshooting, look at all of the expressions prior to the `target.ProcId >= 0` expression, because it and everything following it is logic that the job router added so that routed jobs do not get routed again.
2.  **If your job matches more than one route:** the tool will tell you by showing all matching routes after the job ID:

        Checking Job src=162,0 against all routes
        Route Matches: Local_PBS
        Route Matches: Condor_Test

    To troubleshoot why this is occuring, look at the combined Requirements expressions for all routes and compare it to the job’s ClassAd provided. The combined Requirements expression is highlighted below:

        ::::file hl_lines="5"
        Umbrella constraint: ((target.x509userproxysubject =!= UNDEFINED) &&
        (target.x509UserProxyExpiration =!= UNDEFINED) &&
        (time() < target.x509UserProxyExpiration) &&
        (target.JobUniverse =?= 5 || target.JobUniverse =?= 1)) &&
        ( (target.osgTestPBS is true) || (true) ) &&
        (target.ProcId >= 0 && target.JobStatus == 1 &&
        (target.StageInStart is undefined || target.StageInFinish isnt undefined) &&
        target.Managed isnt "ScheddDone" &&
        target.Managed isnt "Extenal" &&
        target.Owner isnt Undefined &&
        target.RoutedBy isnt "htcondor-ce")


    Both routes evaluate to `true` for the job’s ClassAd because it contained `osgTestPBS = true`. Make sure your routes are mutually exclusive, otherwise you may have jobs routed incorrectly! See the [job route configuration page](job-router-recipes) for more details.

3.  **If it is unclear why jobs are matching a route:** wrap the route's requirements expression in [debug()](job-router-recipes#debugging-routes) and check the [JobRouterLog](#jobrouterlog) for more information.


### condor_ce_router_q

#### Usage

If you have multiple job routes and many jobs, `condor_ce_router_q` is a useful tool to see how jobs are being routed
and their statuses:

``` console
user@host $ condor_ce_router_q
```

`condor_ce_router_q` takes the same options as `condor_router_q` and `condor_q` and is documented in the [HTCondor
manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_router_q.html)


### condor_ce_status

#### Usage

To see the daemons running on a CE, run the following command:

``` console
user@host $ condor_ce_status -any
```

`condor_ce_status` takes the same arguments as `condor_status`, which are documented in the
[HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_status.html).

!!! note ""Missing" Worker Nodes"
    An HTCondor-CE will not show any worker nodes (e.g. `Machine` entries in the `condor_ce_status -any` output) if
    it does not have any running GlideinWMS pilot jobs.
    This is expected since HTCondor-CE only forwards incoming grid jobs to your batch system and does not match jobs to
    worker nodes.

#### Troubleshooting

If the output of `condor_ce_status -any` does not show at least the following daemons:

- Collector
- Scheduler
- DaemonMaster
- Job_Router

Increase the [debug level](/compute-element/troubleshoot-htcondor-ce/#htcondor-ce-troubleshooting-items) and consult the
[HTCondor-CE logs](/compute-element/troubleshoot-htcondor-ce/#htcondor-ce-troubleshooting-data) for errors.

### condor_ce_config_val

#### Usage

To see the value of configuration variables and where they are set, use `condor_ce_config_val`. 
Primarily, This tool is used with the other troubleshooting tools to make sure your configuration is set properly. 
To see the value of a single variable and where it is set:

``` console
user@host $ condor_ce_config_val -v <CONFIGURATION-VARIABLE>
```

To see a list of all configuration variables and their values:

``` console
user@host $ condor_ce_config_val -dump
```

To see a list of all the files that are used to create your configuration and the order that they are parsed, use the
following command:

``` console
user@host $ condor_ce_config_val -config
```

`condor_ce_config_val` takes the same arguments as `condor_config_val` and is documented in the [HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_config_val.html).


### condor_ce_reconfig

#### Usage

To ensure that your configuration changes have taken effect, run `condor_ce_reconfig`.

``` console
user@host $ condor_ce_reconfig
```

### condor_ce_{on,off,restart}

#### Usage

To turn on/off/restart HTCondor-CE daemons, use the following commands:

``` console
root@host # condor_ce_on
root@host # condor_ce_off
root@host # condor_ce_restart
```

The HTCondor-CE service uses the previous commands with default values. 
Using these commands directly gives you more fine-grained control over the behavior of HTCondor-CE's on/off/restart:

-   If you have installed a new version of HTCondor-CE and want to restart the CE under the new version, run the following command:

        :::console
        root@host # condor_ce_restart -fast

    This will cause HTCondor-CE to restart and quickly reconnect to all running jobs.

-   If you need to stop running new jobs, run the following:

        :::console
        root@host # condor_ce_off -peaceful

    This will cause HTCondor-CE to accept new jobs without starting them and will wait for currently running jobs to complete before shutting down.


HTCondor-CE Troubleshooting Data
--------------------------------

The following files are located on the CE host.

### MasterLog

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

#### What to look for: ####

Successful daemon start-up. 
The following line shows that the Collector daemon started successfully:

```
10/07/14 14:20:27 Started DaemonCore process "/usr/sbin/condor_collector -f -port 9619", pid and pgroup = 7318
```

### SchedLog

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

#### What to look for ####

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

    Since HTCondor-CE does not manage any resources, it does not run a negotiator daemon by default and this error message is expected. In the same vein, you may see messages that there are 0 worker nodes:

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

    This means `/var/lib/condor-ce/spool/job_queue.log` has been corrupted and you will need to hand-remove the offending record by searching for the text specified after the `Lines following corrupt log record...` line. The most common culprit of the corruption is that the disk containing the `job_queue.log` has filled up. To avoid this problem, you can change the location of `job_queue.log` by setting `JOB_QUEUE_LOG` in `/etc/condor-ce/config.d/` to a path, preferably one on a large SSD.

### JobRouterLog

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

#### Known Errors ####

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

#### What to look for ####

-   Job is considered for routing:

        09/17/14 15:00:56 JobRouter (src=86.0,route=Local_LSF): found candidate job

    In parentheses are the original HTCondor-CE job ID (e.g., `86.0`) and the route (e.g., `Local_LSF`).

-   Job is successfully routed:

        09/17/14 15:00:57 JobRouter (src=86.0,route=Local_LSF): claimed job

-   Finding the corresponding job ID on your HTCondor batch system:

        09/17/14 15:00:57 JobRouter (src=86.0,dest=205.0,route=Local_Condor): claimed job

    In parentheses are the original HTCondor-CE job ID (e.g., `86.0`) and the resultant job ID on the HTCondor batch system (e.g., `205.0`)

-   If your job is not routed, there will not be any evidence of it within the log itself. To investigate why your jobs are not being considered for routing, use the [condor\_ce\_job\_router\_info](#condor_ce_job_router_info)
-   **HTCondor batch systems only**: The following error occurs when the job router daemon cannot submit the routed job:

        :::text
        10/19/14 13:09:15 Can't resolve collector condorce.example.com; skipping
        10/19/14 13:09:15 ERROR (pool condorce.example.com) Can't find address of schedd
        10/19/14 13:09:15 JobRouter failure (src=5.0,route=Local_Condor): failed to submit job

### GridmanagerLog

The HTCondor-CE grid manager log tracks the submission and status of jobs on non-HTCondor batch systems. 
It contains valuable information when trying to troubleshoot jobs that have been routed but failed to complete. 
Details on how to read the Gridmanager log can be found on the [HTCondor
Wiki](https://htcondor-wiki.cs.wisc.edu/index.cgi/wiki?p=GridmanagerLog).

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

#### What to look for ####

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

    The first line tells us that the Gridmanager is initiating a status update and the following lines are the results. The most interesting line is the second highlighted section that notes the job ID on the batch system and its status. If there are errors querying the job on the batch system, they will appear here.

-   Finding the corresponding job ID on your non-HTCondor batch system:

        :::text
        09/17/14 15:07:24 [25543] (87.0) gm state change: GM_SUBMITTED -> GM_POLL_ACTIVE
        09/17/14 15:07:24 [25543] GAHP[25563] <- 'BLAH_JOB_STATUS 3 lsf/20140917/482046'

    On the first line, after the timestamp and PID of the Gridmanager process, you will find the CE’s job ID in parentheses, `(87.0)`. At the end of the second line, you will find the batch system, date, and batch system job id separated by slashes, `lsf/20140917/482046`.

-   Job completion on the batch system:

        09/17/14 15:07:25 [25543] (87.0) gm state change: GM_TRANSFER_OUTPUT -> GM_DONE_SAVE

### SharedPortLog

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

### Messages log

The messages file can include output from lcmaps, which handles mapping of X.509 proxies to Unix usernames. 
If there are issues with the [authentication setup](install-htcondor-ce#configuring-authentication), the errors may
appear here.

- Location: `/var/log/messages`
- Key contents: User authentication

#### What to look for ####

A user is mapped:

```
Oct 6 10:35:32 osgserv06 htondor-ce-llgt[12147]: Callout to "LCMAPS" returned local user (service condor): "osgglow01"
```

### BLAHP Configuration File

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
    Whitespace is important so do not put any spaces around the = sign. In addition, the directory must be created and HTCondor-CE should have sufficient permissions to create directories within `<DIR_NAME>`.

Getting Help
------------

If you are still experiencing issues after using this document, please let us know!

1.  Gather basic HTCondor-CE and related information (versions, relevant configuration, problem description, etc.)
2.  Gather system information:

        root@host # osg-system-profiler

3.  Start a support request using [a web interface](https://support.opensciencegrid.org/helpdesk/tickets/new) or by email to <help@opensciencegrid.org>
    -   Describe issue and expected or desired behavior
    -   Include basic HTCondor-CE and related information
    -   Attach the osg-system-profiler output

Reference
---------

Here are some other HTCondor-CE documents that might be helpful:

-   [HTCondor-CE overview and architecture](htcondor-ce-overview)
-   [Installing HTCondor-CE](install-htcondor-ce)
-   [Configuring HTCondor-CE job routes](job-router-recipes)
-   [Submitting jobs to HTCondor-CE](submit-htcondor-ce)
