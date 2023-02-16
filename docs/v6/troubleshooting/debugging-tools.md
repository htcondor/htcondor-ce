Debugging Tools
===============

HTCondor-CE has its own separate set of of the HTCondor tools with **ce** in the name (i.e., `condor_ce_submit` vs
`condor_submit`). 
Some of the the commands are only for the CE (e.g., `condor_ce_run` and `condor_ce_trace`) but many of them are just
HTCondor commands configured to interact with the CE (e.g., `condor_ce_q`, `condor_ce_status`). 
It is important to differentiate the two: `condor_ce_config_val` will provide configuration values for your HTCondor-CE
while
`condor_config_val` will provide configuration values for your HTCondor batch system. 
If you are not running an HTCondor batch system, the non-CE commands will return errors.

condor_ce_trace
---------------

### Usage ###

`condor_ce_trace` is a useful tool for testing end-to-end job submission.
It contacts both the CE’s Schedd and Collector daemons to verify your permission to submit to the CE, displays the
submit script that it submits to the CE, and tracks the resultant job.

!!! note
    You must have generated a proxy (e.g., `voms-proxy-init`) and your DN must be added to your
    [chosen authentication method](../configuration/authentication.md).

``` console
user@host $ condor_ce_trace condorce.example.com
```

Replacing the `condorce.example.com` with the hostname of the CE. 
If you are familiar with the output of condor commands, the command also takes a `--debug` option that displays verbose
condor output.

### Troubleshooting ###

1.  **If the command fails with “Failed ping…”:** Make sure that the HTCondor-CE daemons are running on the CE
2.  **If you see “gsi@unmapped” in the “Remote Mapping” line:** Either your credentials are not mapped on the CE or
    authentication is not set up at all.
    To set up authentication, refer to our
    [configuration document](../configuration/authentication.md).
3.  **If the job submits but does not complete:** Look at the status of the job and perform the relevant
    [troubleshooting steps](common-issues.md).

condor_ce_host_network_check
----------------------------

### Usage ###

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

### Troubleshooting ###

If the tool reports that `Host network configuration not expected to work with HTCondor-CE`, ensure that forward and
reverse DNS resolution return the public IP and hostname.

condor_ce_run
-------------

### Usage ###

`condor_ce_run` is a tool that submits a simple job to your CE, so it is useful for quickly
submitting jobs through your CE. 
To submit a job to the CE and run the `env` command on the remote batch system:

!!! note
    You must have generated a proxy (e.g., `voms-proxy-init`) and your DN must be added to your
    [chosen authentication method](../configuration/authentication.md).

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
[this](../configuration/optional-configuration.md#limiting-or-disabling-locally-running-jobs) section of the install
documentation.

### Troubleshooting ###

1.  **If you do not see any results:** `condor_ce_run` does not display results until the job completes on the CE, which
    may take several minutes or longer if the CE is busy.
    In the meantime, can use [condor\_ce\_q](#condor_ce_q) in a separate terminal to track the job on the CE. If you
    never see any results, use [condor\_ce\_trace](#condor_ce_trace) to pinpoint errors.
2.  **If you see an error message that begins with “Failed to…”:** Check connectivity to the CE with
    [condor\_ce\_trace](#condor_ce_trace) or [condor\_ce\_ping](#condor_ce_ping)

condor_ce_submit
----------------

See [this documentation](../remote-job-submission.md) for details

condor_ce_ping
--------------

### Usage ###

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
    If you run the `condor_ce_ping` command on the CE that you are testing, omit the `-name` and `-pool`
    options. `condor_ce_ping` takes the same arguments as `condor_ping` and is documented in the
    [HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_ping.html).

### Troubleshooting ###

1.  **If you see “ERROR: couldn’t locate (null)”**, that means the HTCondor-CE schedd (the daemon that schedules jobs)
    cannot be reached.
    To track down the issue, increase debugging levels on the CE:

        MASTER_DEBUG = D_ALWAYS:2 D_CAT
        SCHEDD_DEBUG = D_ALWAYS:2 D_CAT

    Then look in the [MasterLog](logs.md#masterlog) and [SchedLog](logs.md#schedlog) for any errors.

2.  **If you see “gsi@unmapped” in the “Remote Mapping” line**, this means that either your credentials are not mapped
    on the CE or that authentication is not set up at all.
    To set up authentication, refer to our [configuration document](../configuration/authentication.md).


condor_ce_q
-----------

### Usage ###

`condor_ce_q` can display job status or specific job attributes for jobs that are still in the CE’s queue.
To list jobs that are queued on a CE:

``` console
user@host $ condor_ce_q -name condorce.example.com -pool condorce.example.com:9619
```

To inspect the full ClassAd for a specific job, specify the `-l` flag and the job ID:

``` console
user@host $ condor_ce_q -name condorce.example.com -pool condorce.example.com:9619 -l <JOB-ID>
```

!!! note
    If you run the `condor_ce_q` command on the CE that you are testing, omit the `-name` and `-pool` options.
    `condor_ce_q` takes the same arguments as `condor_q` and is documented in the
    [HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_q.html).

### Troubleshooting ###

If the jobs that you are submiting to a CE are not completing, `condor_ce_q` can tell you the status of your jobs.

1.  **If the schedd is not running:** You will see a lengthy message about being unable to contact the schedd.
    To track down the issue, increase the debugging levels on the CE with:

        MASTER_DEBUG = D_ALWAYS:2 D_CAT
        SCHEDD_DEBUG = D_ALWAYS:2 D_CAT

    To apply these changes, reconfigure HTCondor-CE:

        :::console
        root@host # condor_ce_reconfig

    Then look in the [MasterLog](logs.md#masterlog) and [SchedLog](logs.md#schedlog) on the CE for any errors.

1.  **If there are issues with contacting the collector:** You will see the following message:

        :::console
        user@host $ condor_ce_q -pool ce1.accre.vanderbilt.edu -name ce1.accre.vanderbilt.edu

        -- Failed to fetch ads from: <129.59.197.223:9620?sock`33630_8b33_4> : ce1.accre.vanderbilt.edu

    This may be due to network issues or bad HTCondor daemon permissions.
    To fix the latter issue, ensure that the `ALLOW_READ` configuration value is not set:

        :::console
        user@host $ condor_ce_config_val -v ALLOW_READ
        Not defined: ALLOW_READ

    If it is defined, remove it from the file that is returned in the output.

2.  **If a job is held:** There should be an accompanying `HoldReason` that will tell you why it is being held.
    The `HoldReason` is in the job’s ClassAd, so you can use the long form of `condor_ce_q` to extract its value:

        :::console
        user@host $ condor_ce_q -name condorce.example.com -pool condorce.example.com:9619 -l <Job ID> | grep HoldReason

3.  **If a job is idle:** The most common cause is that it is not matching any routes in the CE’s job router.
    To find out whether this is the case, use the [condor\_ce\_job\_router\_info](#condor_ce_job_router_info).


condor_ce_history
-----------------

### Usage ###

`condor_ce_history` can display job status or specific job attributes for jobs that have that have left the CE’s queue.
To list jobs that have run on the CE:

``` console
user@host $ condor_ce_history -name condorce.example.com -pool condorce.example.com:9619
```

To inspect the full ClassAd for a specific job, specify the `-l` flag and the job ID:

``` console
user@host $ condor_ce_history -name condorce.example.com -pool condorce.example.com:9619 -l <Job ID>
```

!!! note
    If you run the `condor_ce_history` command on the CE that you are testing, omit the `-name` and `-pool` options.
    `condor_ce_history` takes the same arguments as `condor_history` and is documented in the
    [HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_history.html).


condor_ce_job_router_info
-------------------------

### Usage ###

Use the `condor_ce_job_router_info` command to help troubleshoot your routes and how jobs will match to them. 
To see all of your routes (the output is long because it combines your routes with the
[JOB\_ROUTER\_DEFAULTS](../configuration/job-router-overview.md#deprecated-syntax) configuration variable):

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

### Troubleshooting ###

1.  **If the job does not match any route:** You can identify this case when you see `0 candidate jobs found` in the
    `condor_job_router_info` output.
    This message means that, when compared to your job’s ClassAd, the Umbrella constraint does not evaluate to `true`.
    When troubleshooting, look at all of the expressions prior to the `target.ProcId >= 0` expression, because it and
    everything following it is logic that the job router added so that routed jobs do not get routed again.
2.  **If your job matches more than one route:** the tool will tell you by showing all matching routes after the job ID:

        Checking Job src=162,0 against all routes
        Route Matches: Local_PBS
        Route Matches: Condor_Test

    To troubleshoot why this is occuring, look at the combined Requirements expressions for all routes and compare it to
    the job’s ClassAd provided.
    The combined Requirements expression is highlighted below:

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


    Both routes evaluate to `true` for the job’s ClassAd because it contained `osgTestPBS = true`.
    Make sure your routes are mutually exclusive, otherwise you may have jobs routed incorrectly! See the
    [job route configuration page](../configuration/job-router-overview.md) for more details.

3.  **If it is unclear why jobs are matching a route:** wrap the route's requirements expression in
    [debug()](../configuration/writing-job-routes.md#debugging-routes) and check the
    [JobRouterLog](logs.md#jobrouterlog) for more information.


condor_ce_router_q
------------------

### Usage ###

If you have multiple job routes and many jobs, `condor_ce_router_q` is a useful tool to see how jobs are being routed
and their statuses:

``` console
user@host $ condor_ce_router_q
```

`condor_ce_router_q` takes the same options as `condor_router_q` and `condor_q` and is documented in the
[HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_router_q.html)


condor_ce_status
----------------

### Usage ###

To see the daemons running on a CE, run the following command:

``` console
user@host $ condor_ce_status -any
```

`condor_ce_status` takes the same arguments as `condor_status`, which are documented in the
[HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_status.html).

!!! note ""Missing" Worker Nodes"
    An HTCondor-CE will not show any worker nodes (e.g. `Machine` entries in the `condor_ce_status -any` output) if
    it does not have any running GlideinWMS pilot jobs.
    This is expected since HTCondor-CE only forwards incoming pilot jobs to your batch system and does not match jobs to
    worker nodes.

### Troubleshooting ###

If the output of `condor_ce_status -any` does not show at least the following daemons:

- Collector
- Scheduler
- DaemonMaster
- Job_Router

Increase the [debug level](common-issues.md) and consult the [HTCondor-CE logs](logs.md) for errors.

condor_ce_config_val
--------------------

### Usage ###

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

`condor_ce_config_val` takes the same arguments as `condor_config_val` and is documented in the
[HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_config_val.html).


condor_ce_reconfig
------------------

### Usage ###

To ensure that your configuration changes have taken effect, run `condor_ce_reconfig`.

``` console
user@host $ condor_ce_reconfig
```

condor_ce_{on,off,restart}
--------------------------

### Usage ###

To turn on/off/restart HTCondor-CE daemons, use the following commands:

``` console
root@host # condor_ce_on
root@host # condor_ce_off
root@host # condor_ce_restart
```

The HTCondor-CE service uses the previous commands with default values. 
Using these commands directly gives you more fine-grained control over the behavior of HTCondor-CE's on/off/restart:

-   If you have installed a new version of HTCondor-CE and want to restart the CE under the new version, run the
    following command:

        :::console
        root@host # condor_ce_restart -fast

    This will cause HTCondor-CE to restart and quickly reconnect to all running jobs.

-   If you need to stop running new jobs, run the following:

        :::console
        root@host # condor_ce_off -peaceful

    This will cause HTCondor-CE to accept new jobs without starting them and will wait for currently running jobs to
    complete before shutting down.

Getting Help
------------

If you have any questions or issues about troubleshooting remote HTCondor-CEs, please [contact us](/#contact-us) for
assistance.
