Writing Routes For HTCondor-CE
==============================

The [JobRouter](http://research.cs.wisc.edu/htcondor/manual/v8.6/5_4HTCondor_Job.html) is at the heart of HTCondor-CE and allows admins to transform and direct jobs to specific batch systems. Customizations are made in the form of job routes where each route corresponds to a separate job transformation: If an incoming job matches a job route's requirements, the route creates a transformed job (referred to as the 'routed job') that is then submitted to the batch system. The CE package comes with default routes located in `/etc/condor-ce/config.d/02-ce-*.conf` that provide enough basic functionality for a small site.

If you have needs beyond delegating all incoming jobs to your batch system as they are, this document provides examples of common job routes and job route problems.

!!! note "Definitions"
    - **Incoming Job**: A job which was submitted to the CE from an outside source, such as a GlideinWMS Factory.

    - **Routed Job**: A job which was transformed by the JobRouter.

    - **Batch System**: The underlying batch system that the HTCondor-CE will submit.  This can be Slurm, PBS, HTCondor, SGE, LSF,...

Quirks and Pitfalls
-------------------

-   If a value is set in [JOB\_ROUTER\_DEFAULTS](#job_router_defaults) with `eval_set_<variable>`, override it by using `eval_set_<variable>` in the `JOB_ROUTER_ENTRIES`. Do this at your own risk as it may cause the CE to break.
-   Make sure to run `condor_ce_reconfig` after changing your routes, otherwise they will not take effect.
-   Do **not** set the job environment through the JobRouter. Instead, add any changes to the `[Local Settings]` section in `/etc/osg/config.d/40-localsettings.ini` and run osg-configure, as documented [here](/other/configuration-with-osg-configure#local-settings).
-   HTCondor batch system only: Local universe jobs are excluded from any routing.

How Job Routes are Constructed
------------------------------

Each job route’s [ClassAd](http://research.cs.wisc.edu/htcondor/manual/v8.6/4_1HTCondor_s_ClassAd.html) is constructed by combining each entry from the `JOB_ROUTER_ENTRIES` with the `JOB_ROUTER_DEFAULTS`. Attributes that are [set_*](#setting-attributes) in `JOB_ROUTER_ENTRIES` will override those [set_*](#setting-attributes) in `JOB_ROUTER_DEFAULTS`

### JOB_ROUTER_ENTRIES

`JOB_ROUTER_ENTRIES` is a configuration variable whose default is set in `/etc/condor-ce/config.d/02-ce-*.conf` but may be overriden by the administrator in `/etc/condor-ce/config.d/99-local.conf`. This document outlines the many changes you can make to `JOB_ROUTER_ENTRIES` to fit your site’s needs.

### JOB_ROUTER_DEFAULTS

`JOB_ROUTER_DEFAULTS` is a python-generated configuration variable that sets default job route values that are required for the HTCondor-CE's functionality. To view its contents in a readable format, run the following command:

    :::console
    user@host $ condor_ce_config_val JOB_ROUTER_DEFAULTS | sed 's/;/;\n/g'

!!! warning
    If a value is set in [JOB\_ROUTER\_DEFAULTS](#job_router_defaults) with `eval_set_<variable>`, override it by using `eval_set_<variable>` in the `JOB_ROUTER_ENTRIES`. Do this at your own risk as it may cause the CE to break.

!!! warning
    Do **not** set the `JOB_ROUTER_DEFAULTS` configuration variable yourself. This will cause the CE to stop functioning.

How Jobs Match to Job Routes
----------------------------

The job router considers jobs in the queue ([condor_ce_q](/compute-element/troubleshoot-htcondor-ce#condor_ce_q)) that
meet the following constraints:

- The job has not already been considered by the job router
- The job is associated with an unexpired x509 proxy
- The job's universe is standard or vanilla

If the job meets the above constraints, then the job's ClassAd is compared against each
[route's requirements](/compute-element/job-router-recipes/#filtering-jobs-based-on).
If the job only meets one route's requirements, the job is matched to that route.
If the job meets the requirements of multiple routes,  the route that is chosen depends on your version of HTCondor
(`condor_version`):

| If your version of HTCondor is... | Then the route is chosen by...                                                                                               |
|-----------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| < 8.7.1                           | **Round-robin** between all matching routes. In this case, we recommend making each route's requirements mutually exclusive. |
| >= 8.7.1                          | **First matching route** where routes are considered in the same order that they are configured                              |

If you're using HTCondor >= 8.7.1 and would like to use round-robin matching, add the following text to a file in
`/etc/condor-ce/config.d/`:

```
JOB_ROUTER_ROUND_ROBIN_SELECTION = True
```

Generic Routes
--------------

This section contains general information about job routes that can be used regardless of the type of batch system at your site. New routes should be placed in `/etc/condor-ce/config.d/99-local.conf`, not the original `02-ce-*.conf`.

### Required fields

The minimum requirements for a route are that you specify the type of batch system that jobs should be routed to and a name for each route. Default routes can be found in `/usr/share/condor-ce/config.d/02-ce-<batch system>-defaults.conf`, provided by the `osg-ce-<batch system>` packages.

#### Batch system

Each route needs to indicate the type of batch system that jobs should be routed to. For HTCondor batch systems, the `TargetUniverse` attribute needs to be set to `5` or `"vanilla"`. For all other batch systems, the `TargetUniverse` attribute needs to be set to `9` or `"grid"` and the `GridResource` attribute needs to be set to `"batch <batch system>"` (where `<batch system>` can be one of `pbs`, `slurm`, `lsf`, or `sge`).

```hl_lines="3 7 8"
JOB_ROUTER_ENTRIES @=jre
[
  TargetUniverse = 5;
  name = "Route jobs to HTCondor";
]
[
  GridResource = "batch pbs";
  TargetUniverse = 9;
  name = "Route jobs to PBS";
]
@jre
```

#### Route name

To identify routes, you will need to assign a name to the route with the `name` attribute:

```hl_lines="4"
JOB_ROUTER_ENTRIES @=jre
[
  TargetUniverse = 5;
  name = "Route jobs to HTCondor";
]
@jre
```

The name of the route will be useful in debugging since it shows up in the output of [condor\_ce\_job\_router\_info](/compute-element/troubleshoot-htcondor-ce#condor_ce_job_router_info), the [JobRouterLog](/compute-element/troubleshoot-htcondor-ce#jobrouterlog), and in the ClassAd of the routed job, which can be viewed with [condor\_ce\_q](/compute-element/troubleshoot-htcondor-ce#condor_ce_q) or [condor\_ce\_history](/compute-element/troubleshoot-htcondor-ce#condor_ce_history).

### Writing multiple routes

!!! note
    Before writing multiple routes, consider the details of [how jobs match to job routes](#how-jobs-match-to-job-routes)

If your batch system needs incoming jobs to be sorted (e.g. if different VO's need to go to separate queues),
you will need to write multiple job routes where each route is enclosed by square brackets.
The following routes takes incoming jobs that have a `queue` attribute set to `"analy"` and routes them to the site's
HTCondor batch system.
Any other jobs will be sent to that site's PBS batch system.

```hl_lines="2 6 7 12"
JOB_ROUTER_ENTRIES @=jre
[
  TargetUniverse = 5;
  name = "Route jobs to HTCondor";
  Requirements = (TARGET.queue =?= "analy");
]
[
  GridResource = "batch pbs";
  TargetUniverse = 9;
  name = "Route jobs to PBS";
  Requirements = (TARGET.queue =!= "analy");
]
@jre
```

### Writing comments

To write comments you can use `#` to comment a line:

```hl_lines="5"
JOB_ROUTER_ENTRIES @=jre
[
  TargetUniverse = 5;
  name = "# comments";
  # This is a comment
]
@jre
```

### Setting attributes for all routes

To set an attribute that will be applied to all routes, you will need to ensure that `MERGE_JOB_ROUTER_DEFAULT_ADS` is set to `True` (check the value with [condor\_ce\_config\_val](troubleshoot-htcondor-ce#condor_ce_config_val)) and use the [set_](#setting-attributes) function in the `JOB_ROUTER_DEFAULTS`. The following configuration sets the `Periodic_Hold` attribute for all routes:

```hl_lines="7"
# Use the defaults generated by the condor_ce_router_defaults script.  To add
# additional defaults, add additional lines of the form:
#
#   JOB_ROUTER_DEFAULTS = $(JOB_ROUTER_DEFAULTS) [set_foo = 1;]
#
MERGE_JOB_ROUTER_DEFAULT_ADS=True
JOB_ROUTER_DEFAULTS = $(JOB_ROUTER_DEFAULTS) [set_Periodic_Hold = (NumJobStarts >= 1 && JobStatus == 1) || NumJobStarts > 1;]
```

### Filtering jobs based on…

To filter jobs, use the `Requirements` attribute. Jobs will evaluate against the ClassAd expression set in the `Requirements` and if the expression evaluates to `TRUE`, the route will match. More information on the syntax of ClassAd's can be found in the [HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/4_1HTCondor_s_ClassAd.html). For an example on how incoming jobs interact with filtering in job routes, consult [this document](/compute-element/submit-htcondor-ce).

When setting requirements, you need to prefix job attributes that you are filtering with `TARGET.` so that the job route knows to compare the attribute of the incoming job rather than the route’s own attribute. For example, if an incoming job has a `queue = "analy"` attribute, then the following job route will not match:

```hl_lines="6"
JOB_ROUTER_ENTRIES @=jre
[
  TargetUniverse = 5;
  name = "Filtering by queue";
  queue = "not-analy";
  Requirements = (queue =?= "analy");
]
@jre
```

This is because when evaluating the route requirement, the job route will compare its own `queue` attribute to "analy" and see that it does not match. You can read more about comparing two ClassAds in the [HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/4_1HTCondor_s_ClassAd.html#SECTION00513300000000000000).

!!! note
    If you have an HTCondor batch system, note the difference with [set\_requirements](#setting-routed-job-requirements).

!!! note
    Before writing multiple routes, consider the details of [how jobs match to job routes](#how-jobs-match-to-job-routes).

#### Glidein queue

To filter jobs based on their glidein queue attribute, your routes will need a `Requirements` expression using the incoming job's `queue` attribute. The following entry routes jobs to PBS if the incoming job (specified by `TARGET`) is an `analy` (Analysis) glidein:

```hl_lines="5"
JOB_ROUTER_ENTRIES @=jre
[
  TargetUniverse = 5;
  name = "Filtering by queue";
  Requirements = (TARGET.queue =?= "analy");
]
@jre
```

#### Job submitter

To filter jobs based on who submitted it, your routes will need a `Requirements` expression using the incoming job's `Owner` attribute. The following entry routes jobs to the HTCondor batch system if the submitter is `usatlas2`:

```hl_lines="5"
JOB_ROUTER_ENTRIES @=jre
[
  TargetUniverse = 5;
  name = "Filtering by job submitter";
  Requirements = (TARGET.Owner =?= "usatlas2");
]
@jre
```

Alternatively, you can match based on regular expression. The following entry routes jobs to the PBS batch system if the submitter's name begins with `usatlas`:

```hl_lines="6"
JOB_ROUTER_ENTRIES @=jre
[
  GridResource = "batch pbs";
  TargetUniverse = 9;
  name = "Filtering by job submitter (regular expression)";
  Requirements = regexp("^usatlas", TARGET.Owner);
]
@jre
```

#### VOMS attribute

To filter jobs based on the subject of the job's proxy, your routes will need a `Requirements` expression using the incoming job's `x509UserProxyFirstFQAN` attribute. The following entry routes jobs to the PBS batch system if the proxy subject contains `/cms/Role=Pilot`:

```hl_lines="6"
JOB_ROUTER_ENTRIES @=jre
[
  GridResource = "batch pbs";
  TargetUniverse = 9;
  name = "Filtering by VOMS attribute (regex)";
  Requirements = regexp("\/cms\/Role\=pilot", TARGET.x509UserProxyFirstFQAN);
]
@jre
```

### Setting a default…

This section outlines how to set default job limits, memory, cores, and maximum walltime. For an example on how users can override these defaults, consult [this document](submit-htcondor-ce#route-defaults).

#### Maximum number of jobs

To set a default limit to the maximum number of jobs per route, you can edit the configuration variable `CONDORCE_MAX_JOBS` in `/etc/condor-ce/config.d/01-ce-router.conf`:

```
CONDORCE_MAX_JOBS = 10000
```

!!! note
    The above configuration is to be placed directly into the HTCondor-CE configuration, not into a job route.

#### Maximum memory

To set a default maximum memory (in MB) for routed jobs, set the attribute `default_maxMemory`:

```hl_lines="7"
JOB_ROUTER_ENTRIES @=jre
[
  GridResource = "batch pbs";
  TargetUniverse = 9;
  name = "Request memory";
  # Set the requested memory to 1 GB
  set_default_maxMemory = 1000;
]
@jre
```

#### Number of cores to request

To set a default number of cores for routed jobs, set the attribute `default_xcount`:

```hl_lines="7"
JOB_ROUTER_ENTRIES @=jre
[
  GridResource = "batch pbs";
  TargetUniverse = 9;
  name = "Request CPU";
  # Set the requested cores to 8
  set_default_xcount = 8;
]
@jre
```

#### Maximum walltime

To set a default maximum walltime (in minutes) for routed jobs, set the attribute `default_maxWallTime`:

```hl_lines="7"
JOB_ROUTER_ENTRIES @=jre
[
  GridResource = "batch pbs";
  TargetUniverse = 9;
  name = "Setting WallTime";
  # Set the max walltime to 1 hr
  set_default_maxWallTime = 60;
]
@jre
```

### Editing attributes…

The following functions are operations that affect job attributes and are evaluated in the following order:

1.  `copy_*`
2.  `delete_*`
3.  `set_*`
4.  `eval_set_*`

After each job route’s ClassAd is [constructed](#how-job-routes-are-constructed), the above operations are evaluated in order. For example, if the attribute `foo` is set using `eval_set_foo` in the `JOB_ROUTER_DEFAULTS`, you'll be unable to use `delete_foo` to remove it from your jobs since the attribute is set using `eval_set_foo` after the deletion occurs according to the order of operations. To get around this, we can take advantage of the fact that operations defined in `JOB_ROUTER_DEFAULTS` get overridden by the same operation in `JOB_ROUTER_ENTRIES`. So to 'delete' `foo`, we would add `eval_set_foo = ""` to the route in the `JOB_ROUTER_ENTRIES`, resulting in `foo` being absent from the routed job.

More documentation can be found in the [HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/5_4HTCondor_Job.html#SECTION00644000000000000000).

#### Copying attributes

To copy the value of an attribute of the incoming job to an attribute of the routed job, use `copy_`. The following route copies the `environment` attribute of the incoming job and sets the attribute `Original_Environment` on the routed job to the same value:

```hl_lines="6"
JOB_ROUTER_ENTRIES @=jre
[
  GridResource = "batch pbs";
  TargetUniverse = 9;
  name = "Copying attributes";
  copy_environment = "Original_Environment";
]
@jre
```

#### Removing attributes

To remove an attribute of the incoming job from the routed job, use `delete_`. The following route removes the `environment` attribute from the routed job:

```hl_lines="6"
JOB_ROUTER_ENTRIES @=jre
[
  GridResource = "batch pbs";
  TargetUniverse = 9;
  name = "Copying attributes";
  delete_environment = True;
]
@jre
```

#### Setting attributes

To set an attribute on the routed job, use `set_`. The following route sets the Job's `Rank` attribute to 5:

```hl_lines="6"
JOB_ROUTER_ENTRIES @=jre
[
  GridResource = "batch pbs";
  TargetUniverse = 9;
  name = "Setting an attribute";
  set_Rank = 5;
]
@jre
```

#### Setting attributes with ClassAd expressions

To set an attribute to a ClassAd expression to be evaluated, use `eval_set`. The following route sets the `Experiment` attribute to `atlas.osguser` if the Owner of the incoming job is `osguser`:

!!! note
    If a value is set in JOB\_ROUTER\_DEFAULTS with `eval_set_<variable>`, override it by using `eval_set_<variable>` in the `JOB_ROUTER_ENTRIES`.

```hl_lines="6"
JOB_ROUTER_ENTRIES @=jre
[
  GridResource = "batch pbs";
  TargetUniverse = 9;
  name = "Setting an attribute with a !ClassAd expression";
  eval_set_Experiment = strcat("atlas.", Owner);
]
@jre
```

### Limiting the number of jobs

This section outlines how to limit the number of total or idle jobs in a specific route (i.e., if this limit is reached, jobs will no longer be placed in this route).

!!! note
    If you are using an HTCondor batch system, limiting the number of jobs is not the preferred solution: HTCondor manages fair share on its own via [user priorities and group accounting](http://research.cs.wisc.edu/htcondor/manual/v8.6/3_6User_Priorities.html).

#### Total jobs

To set a limit on the number of jobs for a specific route, set the [MaxJobs](http://research.cs.wisc.edu/htcondor/manual/v8.6/5_4HTCondor_Job.html#57134) attribute:

```hl_lines="6 12"
JOB_ROUTER_ENTRIES @=jre
[
  GridResource = "batch pbs";
  TargetUniverse = 9;
  name = "Limit the total number of jobs to 100";
  MaxJobs = 100;
]
[
  GridResource = "batch pbs";
  TargetUniverse = 9;
  name = "Limit the total number of jobs to 75";
  MaxJobs = 75;
]
@jre
```

#### Idle jobs

To set a limit on the number of idle jobs for a specific route, set the [MaxIdleJobs](http://research.cs.wisc.edu/htcondor/manual/v8.6/5_4HTCondor_Job.html#57135) attribute:

```hl_lines="5 10"
JOB_ROUTER_ENTRIES @=jre
[
  TargetUniverse = 5;
  name = "Limit the total number of idle jobs to 100";
  MaxIdleJobs = 100;
]
[
  TargetUniverse = 5;
  name = "Limit the total number of idle jobs to 75";
  MaxIdleJobs = 75;
]
@jre
```

### Debugging routes

To help debug expressions in your routes, you can use the `debug()` function. First, set the debug mode for the JobRouter by editing a file in `/etc/condor-ce/config.d/` to read

```
JOB_ROUTER_DEBUG = D_ALWAYS:2 D_CAT
```

Then wrap the problematic attribute in `debug()`:

```hl_lines="6"
JOB_ROUTER_ENTRIES @=jre
[
  GridResource = "batch pbs";
  TargetUniverse = 9;
  name = "Debugging a difficult !ClassAd expression";
  eval_set_Experiment = debug(strcat("atlas", Name));
]
@jre
```

You will find the debugging output in `/var/log/condor-ce/JobRouterLog`.

Routes for HTCondor Batch Systems
---------------------------------

This section contains information about job routes that can be used if you are running an HTCondor batch system at your site.

### Setting periodic hold, release or remove

To release, remove or put a job on hold if it meets certain criteria, use the `PERIODIC_*` family of attributes. By default, periodic expressions are evaluated once every 300 seconds but this can be changed by setting `PERIODIC_EXPR_INTERVAL` in your CE's configuration.

In this example, we set the routed job on hold if the job is idle and has been started at least once or if the job has tried to start more than once.  This will catch jobs which are starting and stopping multiple times.

```hl_lines="6 10"
JOB_ROUTER_ENTRIES @=jre
[
  TargetUniverse = 5;
  name = "Setting periodic statements";
  # Puts the routed job on hold if the job's been idle and has been started at least once or if the job has tried to start more than once
  set_Periodic_Hold = (NumJobStarts >= 1 && JobStatus == 1) || NumJobStarts > 1;
  # Remove routed jobs if their walltime is longer than 3 days and 5 minutes
  set_Periodic_Remove = ( RemoteWallClockTime > (3*24*60*60 + 5*60) );
  # Release routed jobs if the condor_starter couldn't start the executable and 'VMGAHP_ERR_INTERNAL' is in the HoldReason
  set_Periodic_Release = HoldReasonCode == 6 && regexp("VMGAHP_ERR_INTERNAL", HoldReason);
]
@jre
```

### Setting routed job requirements

If you need to set requirements on your routed job, you will need to use `set_Requirements` instead of `Requirements`. The `Requirements` attribute filters jobs coming into your CE into different job routes whereas `set_Requirements` will set conditions on the routed job that must be met by the worker node it lands on. For more information on requirements, consult the [HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/2_5Submitting_Job.html#SECTION00357000000000000000).

To ensure that your job lands on a Linux machine in your pool:

```hl_lines="4"
JOB_ROUTER_ENTRIES @=jre
[
  TargetUniverse = 5;
  set_Requirements =  OpSys == "LINUX";
]
@jre
```

### Setting accounting groups

To assign jobs to an HTCondor accounting group to manage fair share on your local batch system, we recommend using [UID and ExtAttr tables](/compute-element/install-htcondor-ce#htcondor-accounting-groups).

Routes for non-HTCondor Batch Systems
-------------------------------------

This section contains information about job routes that can be used if you are running a non-HTCondor batch system at your site.

### Setting a default batch queue

To set a default queue for routed jobs, set the attribute `default_queue`:

```hl_lines="6"
JOB_ROUTER_ENTRIES @=jre
[
  GridResource = "batch pbs";
  TargetUniverse = 9;
  name = "Setting batch system queues";
  set_default_queue = "osg_queue";
]
@jre
```

### Setting batch system directives

To write batch system directives that are not supported in the route examples above, you will need to edit the job submit script for your local batch system in `/etc/blahp/` (e.g., if your local batch system is PBS, edit `/etc/blahp/pbs_local_submit_attributes.sh`). This file is sourced during submit time and anything printed to stdout is appended to the batch system job submit script. ClassAd attributes can be passed from the routed job to the local submit attributes script via the `default_remote_cerequirements` attribute, which can take the following form:

```
default_remote_cerequirements = "foo == X && bar == \"Y\" && ..."
```

This sets `foo` to value `X` and `bar` to the string `Y` (escaped double-quotes are required for string values) in the environment of the local submit attributes script. The following example sets the maximum walltime to 1 hour and the accounting group to the `x509UserProxyFirstFQAN` attribute of the job submitted to a PBS batch system

```hl_lines="5"
JOB_ROUTER_ENTRIES @=jre [
     GridResource = "batch pbs";
     TargetUniverse = 9;
     name = "Setting job submit variables";
     set_default_remote_cerequirements = strcat("Walltime == 3600 && AccountingGroup =="", x509UserProxyFirstFQAN, "\"");
]
@jre
```

With `/etc/blahp/pbs_local_submit_attributes.sh` containing.

```
#!/bin/bash
echo "#PBS -l walltime=$Walltime"
echo "#PBS -A $AccountingGroup"
```

This results in the following being appended to the script that gets submitted to your batch system:

```
#PBS -l walltime=3600
#PBS -A <CE job's x509UserProxyFirstFQAN attribute>
```

Reference
---------

Here are some other HTCondor-CE documents that might be helpful:

-   [HTCondor-CE overview and architecture](htcondor-ce-overview)
-   [Installing HTCondor-CE](install-htcondor-ce)
-   [The HTCondor-CE troubleshooting guide](troubleshoot-htcondor-ce)
-   [Submitting jobs to HTCondor-CE](submit-htcondor-ce)

### Example Configurations ###

#### AGLT2's job routes ####

Atlas AGLT2 is using an HTCondor batch system. Here are some things to note about their routes.

-   Setting various HTCondor-specific attributes like `Rank`, `AccountingGroup`, `JobPrio` and `Periodic_Remove` (see the [HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/12_Appendix_A.html) for more). Some of these are site-specific like `LastandFrac`, `IdleMP8Pressure`, `localQue`, `IsAnalyJob` and `JobMemoryLimit`.
-   There is a difference between `Requirements` and `set_requirements`. The `Requirements` attribute matches jobs to specific routes while the `set_requirements` sets the `Requirements` attribute on the *routed* job, which confines which machines that the routed job can land on.

Source: <https://www.aglt2.org/wiki/bin/view/AGLT2/CondorCE#The_JobRouter_configuration_file_content>

```
JOB_ROUTER_ENTRIES @=jre
# Still to do on all routes, get job requirements and add them here
# Route no 1
# Analysis queue
  [
    GridResource = "condor localhost localhost";
    eval_set_GridResource = strcat("condor ", "$(FULL_HOSTNAME)", " $(JOB_ROUTER_SCHEDD2_POOL)");
    Requirements = target.queue=="analy";
    Name = "Analysis Queue";
    TargetUniverse = 5;
    eval_set_IdleMP8Pressure = $(IdleMP8Pressure);
    eval_set_LastAndFrac = $(LastAndFrac);
    set_requirements = ( ( TARGET.TotalDisk =?= undefined ) || ( TARGET.TotalDisk >= 21000000 ) ) && ( TARGET.Arch == "X86_64" ) && ( TARGET.OpSys == "LINUX" ) && ( TARGET.Disk >= RequestDisk ) && ( TARGET.Memory >= RequestMemory ) && ( TARGET.HasFileTransfer ) && (IfThenElse((Owner == "atlasconnect" || Owner == "muoncal"),IfThenElse(IdleMP8Pressure,(TARGET.PARTITIONED =!= TRUE),True),IfThenElse(LastAndFrac,(TARGET.PARTITIONED =!= TRUE),True)));
    eval_set_AccountingGroup = strcat("group_gatekpr.prod.analy.",Owner);
    set_localQue = "Analysis";
    set_IsAnalyJob = True;
    set_JobPrio = 5;
    set_Rank = (SlotID + (64-TARGET.DETECTED_CORES))*1.0;
    set_JobMemoryLimit = 4194000;
    set_Periodic_Remove = ( ( RemoteWallClockTime > (3*24*60*60 + 5*60) ) || (ImageSize > JobMemoryLimit) );
  ]
# Route no 2
# splitterNT queue
  [
    GridResource = "condor localhost localhost";
    eval_set_GridResource = strcat("condor ", "$(FULL_HOSTNAME)", " $(JOB_ROUTER_SCHEDD2_POOL)");
    Requirements = target.queue == "splitterNT";
    Name = "Splitter ntuple queue";
    TargetUniverse = 5;
    set_requirements = ( ( TARGET.TotalDisk =?= undefined ) || ( TARGET.TotalDisk >= 21000000 ) ) && ( TARGET.Arch == "X86_64" ) && ( TARGET.OpSys == "LINUX" ) && ( TARGET.Disk >= RequestDisk ) && ( TARGET.Memory >= RequestMemory ) && ( TARGET.HasFileTransfer );
    eval_set_AccountingGroup = "group_calibrate.muoncal";
    set_localQue = "Splitter";
    set_IsAnalyJob = False;
    set_JobPrio = 10;
    set_Rank = (SlotID + (64-TARGET.DETECTED_CORES))*1.0;
    set_JobMemoryLimit = 4194000;
    set_Periodic_Remove = ( ( RemoteWallClockTime > (3*24*60*60 + 5*60) ) || (ImageSize > JobMemoryLimit) );
  ]
# Route no 3
# splitter queue
  [
    GridResource = "condor localhost localhost";
    eval_set_GridResource = strcat("condor ", "$(FULL_HOSTNAME)", " $(JOB_ROUTER_SCHEDD2_POOL)");
    Requirements = target.queue == "splitter";
    Name = "Splitter queue";
    TargetUniverse = 5;
    set_requirements = ( ( TARGET.TotalDisk =?= undefined ) || ( TARGET.TotalDisk >= 21000000 ) ) && ( TARGET.Arch == "X86_64" ) && ( TARGET.OpSys == "LINUX" ) && ( TARGET.Disk >= RequestDisk ) && ( TARGET.Memory >= RequestMemory ) && ( TARGET.HasFileTransfer );
    eval_set_AccountingGroup = "group_calibrate.muoncal";
    set_localQue = "Splitter";
    set_IsAnalyJob = False;
    set_JobPrio = 15;
    set_Rank = (SlotID + (64-TARGET.DETECTED_CORES))*1.0;
    set_JobMemoryLimit = 4194000;
    set_Periodic_Remove = ( ( RemoteWallClockTime > (3*24*60*60 + 5*60) ) || (ImageSize > JobMemoryLimit) );
  ]
# Route no 4
# xrootd queue
  [
    GridResource = "condor localhost localhost";
    eval_set_GridResource = strcat("condor ", "$(FULL_HOSTNAME)", " $(JOB_ROUTER_SCHEDD2_POOL)");
    Requirements = target.queue == "xrootd";
    Name = "Xrootd queue";
    TargetUniverse = 5;
    set_requirements = ( ( TARGET.TotalDisk =?= undefined ) || ( TARGET.TotalDisk >= 21000000 ) ) && ( TARGET.Arch == "X86_64" ) && ( TARGET.OpSys == "LINUX" ) && ( TARGET.Disk >= RequestDisk ) && ( TARGET.Memory >= RequestMemory ) && ( TARGET.HasFileTransfer );
    eval_set_AccountingGroup = strcat("group_gatekpr.prod.analy.",Owner);
    set_localQue = "Analysis";
    set_IsAnalyJob = True;
    set_JobPrio = 35;
    set_Rank = (SlotID + (64-TARGET.DETECTED_CORES))*1.0;
    set_JobMemoryLimit = 4194000;
    set_Periodic_Remove = ( ( RemoteWallClockTime > (3*24*60*60 + 5*60) ) || (ImageSize > JobMemoryLimit) );
  ]
# Route no 5
# Tier3Test queue
  [
    GridResource = "condor localhost localhost";
    eval_set_GridResource = strcat("condor ", "$(FULL_HOSTNAME)", " $(JOB_ROUTER_SCHEDD2_POOL)");
    Requirements = target.queue == "Tier3Test";
    Name = "Tier3 Test Queue";
    TargetUniverse = 5;
    set_requirements = ( ( TARGET.TotalDisk =?= undefined ) || ( TARGET.TotalDisk >= 21000000 ) ) && ( TARGET.Arch == "X86_64" ) && ( TARGET.OpSys == "LINUX" ) && ( TARGET.Disk >= RequestDisk ) && ( TARGET.Memory >= RequestMemory ) && ( TARGET.HasFileTransfer ) && ( IS_TIER3_TEST_QUEUE =?= True );
    eval_set_AccountingGroup = strcat("group_gatekpr.prod.analy.",Owner);
    set_localQue = "Tier3Test";
    set_IsTier3TestJob = True;
    set_IsAnalyJob = True;
    set_JobPrio = 20;
    set_Rank = (SlotID + (64-TARGET.DETECTED_CORES))*1.0;
    set_JobMemoryLimit = 4194000;
    set_Periodic_Remove = ( ( RemoteWallClockTime > (3*24*60*60 + 5*60) ) || (ImageSize > JobMemoryLimit) );
  ]
# Route no 6
# mp8 queue
  [
    GridResource = "condor localhost localhost";
    eval_set_GridResource = strcat("condor ", "$(FULL_HOSTNAME)", " $(JOB_ROUTER_SCHEDD2_POOL)");
    Requirements = target.queue=="mp8";
    Name = "MCORE Queue";
    TargetUniverse = 5;
    set_requirements = ( ( TARGET.TotalDisk =?= undefined ) || ( TARGET.TotalDisk >= 21000000 ) ) && ( TARGET.Arch == "X86_64" ) && ( TARGET.OpSys == "LINUX" ) && ( TARGET.Disk >= RequestDisk ) && ( TARGET.Memory >= RequestMemory ) && ( TARGET.HasFileTransfer ) && (( TARGET.Cpus == 8 && TARGET.CPU_TYPE =?= "mp8" ) || TARGET.PARTITIONED =?= True );
    eval_set_AccountingGroup = strcat("group_gatekpr.prod.mcore.",Owner);
    set_localQue = "MP8";
    set_IsAnalyJob = False;
    set_JobPrio = 25;
    set_Rank = 0.0;
    eval_set_RequestCpus = 8;
    set_JobMemoryLimit = 33552000;
    set_Slot_Type = "mp8";
    set_Periodic_Remove = ( ( RemoteWallClockTime > (3*24*60*60 + 5*60) ) || (ImageSize > JobMemoryLimit) );
  ]
# Route no 7
# Installation queue, triggered by usatlas2 user
  [
    GridResource = "condor localhost localhost";
    eval_set_GridResource = strcat("condor ", "$(FULL_HOSTNAME)", " $(JOB_ROUTER_SCHEDD2_POOL)");
    Requirements = target.queue is undefined && target.Owner == "usatlas2";
    Name = "Install Queue";
    TargetUniverse = 5;
    set_requirements = ( ( TARGET.TotalDisk =?= undefined ) || ( TARGET.TotalDisk >= 21000000 ) ) && ( TARGET.Arch == "X86_64" ) && ( TARGET.OpSys == "LINUX" ) && ( TARGET.Disk >= RequestDisk ) && ( TARGET.Memory >= RequestMemory ) && ( TARGET.HasFileTransfer ) && ( TARGET.IS_INSTALL_QUE =?= True ) && (TARGET.AGLT2_SITE == "UM" );
    eval_set_AccountingGroup = strcat("group_gatekpr.other.",Owner);
    set_localQue = "Default";
    set_IsAnalyJob = False;
    set_IsInstallJob = True;
    set_JobPrio = 15;
    set_Rank = (SlotID + (64-TARGET.DETECTED_CORES))*1.0;
    set_JobMemoryLimit = 4194000;
    set_Periodic_Remove = ( ( RemoteWallClockTime > (3*24*60*60 + 5*60) ) || (ImageSize > JobMemoryLimit) );
  ]
# Route no 8
# Default queue for usatlas1 user
  [
    GridResource = "condor localhost localhost";
    eval_set_GridResource = strcat("condor ", "$(FULL_HOSTNAME)", " $(JOB_ROUTER_SCHEDD2_POOL)");
    Requirements = target.queue is undefined && regexp("usatlas1",target.Owner);
    Name = "ATLAS Production Queue";
    TargetUniverse = 5;
    set_requirements = ( ( TARGET.TotalDisk =?= undefined ) || ( TARGET.TotalDisk >= 21000000 ) ) && ( TARGET.Arch == "X86_64" ) && ( TARGET.OpSys == "LINUX" ) && ( TARGET.Disk >= RequestDisk ) && ( TARGET.Memory >= RequestMemory ) && ( TARGET.HasFileTransfer );
    eval_set_AccountingGroup = strcat("group_gatekpr.prod.prod.",Owner);
    set_localQue = "Default";
    set_IsAnalyJob = False;
    set_Rank = (SlotID + (64-TARGET.DETECTED_CORES))*1.0;
    set_JobMemoryLimit = 4194000;
    set_Periodic_Remove = ( ( RemoteWallClockTime > (3*24*60*60 + 5*60) ) || (ImageSize > JobMemoryLimit) );
  ]
# Route no 9
# Default queue for any other usatlas account
  [
    GridResource = "condor localhost localhost";
    eval_set_GridResource = strcat("condor ", "$(FULL_HOSTNAME)", " $(JOB_ROUTER_SCHEDD2_POOL)");
    Requirements = target.queue is undefined && (regexp("usatlas2",target.Owner) || regexp("usatlas3",target.Owner));
    Name = "Other ATLAS Production";
    TargetUniverse = 5;
    set_requirements = ( ( TARGET.TotalDisk =?= undefined ) || ( TARGET.TotalDisk >= 21000000 ) ) && ( TARGET.Arch == "X86_64" ) && ( TARGET.OpSys == "LINUX" ) && ( TARGET.Disk >= RequestDisk ) && ( TARGET.Memory >= RequestMemory ) && ( TARGET.HasFileTransfer );
    eval_set_AccountingGroup = strcat("group_gatekpr.other.",Owner);
    set_localQue = "Default";
    set_IsAnalyJob = False;
    set_Rank = (SlotID + (64-TARGET.DETECTED_CORES))*1.0;
    set_JobMemoryLimit = 4194000;
    set_Periodic_Remove = ( ( RemoteWallClockTime > (3*24*60*60 + 5*60) ) || (ImageSize > JobMemoryLimit) );
  ]
# Route no 10
# Anything else. Set queue as Default and assign to other VOs
  [
    GridResource = "condor localhost localhost";
    eval_set_GridResource = strcat("condor ", "$(FULL_HOSTNAME)", " $(JOB_ROUTER_SCHEDD2_POOL)");
    Requirements = target.queue is undefined && ifThenElse(regexp("usatlas",target.Owner),false,true);
    Name = "Other Jobs";
    TargetUniverse = 5;
    set_requirements = ( ( TARGET.TotalDisk =?= undefined ) || ( TARGET.TotalDisk >= 21000000 ) ) && ( TARGET.Arch == "X86_64" ) && ( TARGET.OpSys == "LINUX" ) && ( TARGET.Disk >= RequestDisk ) && ( TARGET.Memory >= RequestMemory ) && ( TARGET.HasFileTransfer );
    eval_set_AccountingGroup = strcat("group_VOgener.",Owner);
    set_localQue = "Default";
    set_IsAnalyJob = False;
    set_Rank = (SlotID + (64-TARGET.DETECTED_CORES))*1.0;
    set_JobMemoryLimit = 4194000;
    set_Periodic_Remove = ( ( RemoteWallClockTime > (3*24*60*60 + 5*60) ) || (ImageSize > JobMemoryLimit) );
  ]
  @jre
```

#### BNL's job routes ####

Atlas BNL T1, they are using an HTCondor batch system. Here are some things to note about their routes:

-   Setting various HTCondor-specific attributes like `JobLeaseDuration`, `Requirements` and `Periodic_Hold` (see the [HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/12_Appendix_A.html) for more). Some of these are site-specific like `RACF_Group`, `Experiment`, `Job_Type` and `VO`.
-   Jobs are split into different routes based on the [GlideIn](#glidein-queue) queue that they're in.
-   There is a difference between `Requirements` and `set_requirements`. The `Requirements` attribute matches *incoming* jobs to specific routes while the `set_requirements` sets the `Requirements` attribute on the *routed* job, which confines which machines that the routed job can land on.

Source: <http://www.usatlas.bnl.gov/twiki/bin/view/Admins/HTCondorCE.html>

```
JOB_ROUTER_ENTRIES @=jre
   [
     GridResource = "condor localhost localhost";
     eval_set_GridResource = strcat("condor ", "$(FULL_HOSTNAME)", "$(FULL_HOSTNAME)");
     TargetUniverse = 5;
     name = "BNL_Condor_Pool_long";
     Requirements = target.queue=="analysis.long";
     eval_set_RACF_Group = "long";
     set_Experiment = "atlas";
     set_requirements = ( ( Arch == "INTEL" || Arch == "X86_64" ) && ( CPU_Experiment == "atlas" ) ) && ( TARGET.OpSys == "LINUX" ) && ( TARGET.Disk >= RequestDisk ) && ( TARGET.Memory >= RequestMemory ) && ( TARGET.HasFileTransfer );
     set_Job_Type = "cas";
     set_JobLeaseDuration = 3600;
     set_Periodic_Hold = (NumJobStarts >= 1 && JobStatus == 1) || NumJobStarts > 1;
     eval_set_VO = x509UserProxyVOName;
   ]
   [
     GridResource = "condor localhost localhost";
     eval_set_GridResource = strcat("condor ", "$(FULL_HOSTNAME)", "$(FULL_HOSTNAME)");
     TargetUniverse = 5;
     name = "BNL_Condor_Pool_short";
     Requirements = target.queue=="analysis.short";
     eval_set_RACF_Group = "short";
     set_Experiment = "atlas";
     set_requirements = ( ( Arch == "INTEL" || Arch == "X86_64" ) && ( CPU_Experiment == "atlas" ) ) && ( TARGET.OpSys == "LINUX" ) && ( TARGET.Disk >= RequestDisk ) && ( TARGET.Memory >= RequestMemory ) && ( TARGET.HasFileTransfer );
     set_Job_Type = "cas";
     set_JobLeaseDuration = 3600;
     set_Periodic_Hold = (NumJobStarts >= 1 && JobStatus == 1) || NumJobStarts > 1;
     eval_set_VO = x509UserProxyVOName;
   ]
   [
     GridResource = "condor localhost localhost";
     eval_set_GridResource = strcat("condor ", "$(FULL_HOSTNAME)", "$(FULL_HOSTNAME)");
     TargetUniverse = 5;
     name = "BNL_Condor_Pool_grid";
     Requirements = target.queue=="grid";
     eval_set_RACF_Group = "grid";
     set_Experiment = "atlas";
     set_requirements = ( ( Arch == "INTEL" || Arch == "X86_64" ) && ( CPU_Experiment == "atlas" ) ) && ( TARGET.OpSys == "LINUX" ) && ( TARGET.Disk >= RequestDisk ) && ( TARGET.Memory >= RequestMemory ) && ( TARGET.HasFileTransfer );
     set_Job_Type = "cas";
     set_JobLeaseDuration = 3600;
     set_Periodic_Hold = (NumJobStarts >= 1 && JobStatus == 1) || NumJobStarts > 1;
     eval_set_VO = x509UserProxyVOName;
   ]
   [
     GridResource = "condor localhost localhost";
     eval_set_GridResource = strcat("condor ", "$(FULL_HOSTNAME)", "$(FULL_HOSTNAME)");
     TargetUniverse = 5;
     name = "BNL_Condor_Pool";
     Requirements = target.queue is undefined;
     eval_set_RACF_Group = "grid";
     set_requirements = ( ( Arch == "INTEL" || Arch == "X86_64" ) && ( CPU_Experiment == "rcf" ) ) && ( TARGET.OpSys == "LINUX" ) && ( TARGET.Disk >= RequestDisk ) && ( TARGET.Memory >= RequestMemory ) && ( TARGET.HasFileTransfer );
     set_Experiment = "atlas";
     set_Job_Type = "cas";
     set_JobLeaseDuration = 3600;
     set_Periodic_Hold = (NumJobStarts >= 1 && JobStatus == 1) || NumJobStarts > 1;
     eval_set_VO = x509UserProxyVOName;
   ]
   @jre
```
