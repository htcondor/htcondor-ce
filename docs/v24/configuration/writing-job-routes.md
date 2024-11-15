Writing Job Routes
==================

This document contains documentation for HTCondor-CE Job Router configurations with examples for the
[ClassAd transform](job-router-overview.md#classad-transforms).
Configuration from this page should be written to files in `/etc/condor-ce/config.d/`, whose contents are parsed in
lexicographic order with subsequent variables overriding earlier ones.

Each example is displayed in code blocks:

    ```
    This is an example for the ClassAd transform syntax
    ```

Required Fields
---------------

The minimum requirements for a route are that you specify the type of batch system that jobs should be routed to and a
name for each route.
Default routes can be found in `/usr/share/condor-ce/config.d/02-ce-<batch system>-defaults.conf`, provided by the
`htcondor-ce-<batch system>` packages.

### Route name

To identify routes, you will need to assign a name to the route, in the name of the configuration macro
(i.e., `JOB_ROUTER_ROUTE_<name>`):

    ```hl_lines="1"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      UNIVERSE VANILLA
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

!!! warning "Naming restrictions"
    -   Route names should only contain alphanumeric and `_` characters.
    -   Routes specified by `JOB_ROUTER_ROUTE_*` will override routes with the same name in `JOB_ROUTER_ENTRIES`

The name of the route will be useful in debugging since it shows up in the output of
[condor\_ce\_job\_router\_info](../troubleshooting/debugging-tools.md#condor_ce_job_router_info);
the [JobRouterLog](../troubleshooting/logs.md#jobrouterlog);
in the ClassAd of the routed job, which can be viewed with `condor_q` and `condor_history` for HTCondor batch systems;
and in the ClassAd of the routed job, which can be vieweed with 
[condor\_ce\_q](../troubleshooting/debugging-tools.md#condor_ce_q) or
[condor\_ce\_history](../troubleshooting/debugging-tools.md#condor_ce_history) for non-HTCondor batch systems.

### Batch system

Each route needs to indicate the type of batch system that jobs should be routed to.
For HTCondor batch systems, the `UNIVERSE` command or `TargetUniverse` attribute needs to be set to `"VANILLA"` or `5`,
respectively.
For all other batch systems, the `GridResource` attribute needs to be set to `"batch <batch system>"`
(where `<batch system>` can be one of `pbs`, `slurm`, `lsf`, or `sge`).


    ```hl_lines="2 6 7"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      UNIVERSE VANILLA
    @jrt

    JOB_ROUTER_ROUTE_My_Slurm @=jrt
      GridResource = "batch slurm"
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool My_Slurm
    ```

Writing Multiple Routes
-----------------------

If your batch system needs incoming jobs to be sorted (e.g. if different VO's need to go to separate queues), you will
need to write multiple job routes where each route is a separate `JOB_ROUTER_ROUTE_*` macro.
Additionally, the route names must be added to `JOB_ROUTER_ROUTE_NAMES` in the order that you want their requirements
statements compared to incoming jobs.

The following routes takes incoming jobs that have a `queue` attribute set to `"prod"` and sets `IsProduction = True`.
All other jobs will be routed with `IsProduction = False`.

    ```hl_lines="1 7 12"
    JOB_ROUTER_ROUTE_Production_Jobs @=jrt
      REQUIREMENTS queue == "prod"
      UNIVERSE VANILLA
      SET IsProduction = True
    @jrt

    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      UNIVERSE VANILLA
      SET IsProduction = False
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Production_Jobs Condor_Pool
    ```

Writing Comments
----------------

To write comments you can use `#` to comment a line:

    ```hl_lines="2"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      # This is a comment
      UNIVERSE VANILLA
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

Setting Attributes for All Routes
---------------------------------

### ClassAd transform

With the ClassAd transform syntax, any function from the [Editing Attributes section](#editing-attributes) can be
applied before or after your routes are considered by appending the names of transforms specified by
`JOB_ROUTER_TRANSFORM_<name>` to the lists of `JOB_ROUTER_PRE_ROUTE_TRANSFORM_NAMES` and
`JOB_ROUTER_POST_ROUTE_TRANSFORM_NAMES`,
respectively.
The following configuration sets the `Periodic_Hold` attribute for all routed jobs before any route transforms are
applied:

```
JOB_ROUTER_TRANSFORM_Periodic_Hold
  SET Periodic_Hold = (NumJobStarts >= 1 && JobStatus == 1) || NumJobStarts > 1
@jrt

JOB_ROUTER_PRE_ROUTE_TRANSFORM_NAMES = $(JOB_ROUTER_PRE_ROUTE_TRANSFORM_NAMES) Periodic_Hold
```

To apply the same transform after your pre-route and route transforms, append the name of the transform to
`JOB_ROUTER_POST_ROUTE_TRANSFORM_NAMES` instead:

```
JOB_ROUTER_POST_ROUTE_TRANSFORM_NAMES = $(JOB_ROUTER_POST_ROUTE_TRANSFORM_NAMES) Periodic_Hold
```

Filtering Jobs Based On…
------------------------

To filter jobs, use the route's `REQUIREMENTS` attribute.
Incoming jobs will be evaluated against the ClassAd expression set in the route's requirements and if the expression
evaluates to `TRUE`, the route will match.
More information on the syntax of ClassAd's can be found in the
[HTCondor manual](https://htcondor.readthedocs.io/en/lts/misc-concepts/classad-mechanism.html).
For an example on how incoming jobs interact with filtering in job routes, consult
[this document](../remote-job-submission.md).

!!! note
    If you have an HTCondor batch system, note the difference with
    [set\_requirements](htcondor-routes.md#setting-routed-job-requirements):

### Pilot job queue ###

To filter jobs based on their pilot job queue attribute, your routes will need a requirements expression using the
incoming job's `queue` attribute.
The following entry routes jobs to HTCondor if the incoming job (specified by `TARGET`) is an `analy` (Analysis) glidein:

    ```hl_lines="2"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      REQUIREMENTS queue == "prod"
      UNIVERSE VANILLA
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

### Mapped user ###

To filter jobs based on what local account the incoming job was mapped to, your routes will need a requirements
expression using the incoming job's `Owner` attribute.
The following entry routes jobs to the HTCondor batch system if the mapped user is `usatlas2`:

    ```hl_lines="2"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      REQUIREMENTS Owner == "usatlas2"
      UNIVERSE VANILLA
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

Alternatively, you can match based on regular expression.
The following entry routes jobs to the HTCondor batch system if the mapped user begins with `usatlas`:

    ```hl_lines="2"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      REQUIREMENTS regexp("^usatlas", Owner)
      UNIVERSE VANILLA
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

### VOMS attribute ###

To filter jobs based on the subject of the job's proxy, your routes will need a requirements expression using the
incoming job's `x509UserProxyFirstFQAN` attribute.
The following entry routes jobs to the HTCondor batch system if the proxy subject contains `/cms/Role=Pilot`:


    ```hl_lines="2"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      REQUIREMENTS regexp("\/cms\/Role\=pilot", x509UserProxyFirstFQAN)
      UNIVERSE VANILLA
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

Setting a Default…
------------------

This section outlines how to set default job limits, memory, cores, and maximum walltime.
For an example on how users can override these defaults, consult
[this document](../remote-job-submission.md#submit-the-job).

### Maximum number of jobs ###

To set a default limit to the maximum number of jobs per route, you can edit the configuration variable
`CONDORCE_MAX_JOBS` in `/etc/condor-ce/config.d/01-ce-router.conf`:

```
CONDORCE_MAX_JOBS = 10000
```

!!! note
    The above configuration is to be placed directly into the HTCondor-CE configuration instead of a job route or
    transform.

### Maximum memory ###

To set a default maximum memory (in MB) for routed jobs, set the variable `default_maxMemory`:

    ```hl_lines="4"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      UNIVERSE VANILLA
      # Set the requested memory to 1 GB
      default_maxMemory = 1000
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

### Number of cores to request ###

To set a default number of cores for routed jobs, set the variable `default_xcount`:


    ```hl_lines="4"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      UNIVERSE VANILLA
      # Set the requested memory to 1 GB
      default_xcount = 8
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

### Number of gpus to request ###

To set a default number of GPUs for routed jobs, set the job ClassAd attribute `RequestGPUs` in the route
transform:

    ```hl_lines="4"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      UNIVERSE VANILLA
      # If the job does not already have a RequestGPUs value set it to 1
      DEFAULT RequestGPUs = 1
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

The `DEFAULT` keyword works for any job attribute other than those mentioned above that require the use of
alternative names for defaulting in the CE.

### Maximum walltime ###

To set a default number of cores for routed jobs, set the variable `default_maxWallTime`:

    ```hl_lines="4"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      UNIVERSE VANILLA
      # Set the max walltime to 1 hr
      default_maxWallTime = 60
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

Setting Job Environments
------------------------

HTCondor-CE offers two different methods for setting environment variables of routed jobs:

- `CONDORCE_PILOT_JOB_ENV` configuration, which should be used for setting environment variables for all routed jobs to
  static strings.
- `default_pilot_job_env` or `set_default_pilot_job_env` job route configuration, which should be used for setting
  environment variables:
    - Per job route
    - To values based on incoming job attributes
    - Using [ClassAd functions](https://htcondor.readthedocs.io/en/lts/misc-concepts/classad-mechanism.html#predefined-functions)

Both of these methods use the new HTCondor format of the
[environment command](https://htcondor.readthedocs.io/en/lts/man-pages/condor_submit.html#index-14), which is
described by environment variable/value pairs separated by whitespace and enclosed in double-quotes.
For example, the following HTCondor-CE configuration would result in the following environment for all routed jobs:


=== "HTCondor-CE Configuration"

    ```
    CONDORCE_PILOT_JOB_ENV = "WN_SCRATCH_DIR=/nobackup/ http_proxy=proxy.wisc.edu"
    ```

=== "Resulting Environment"

    ```bash
    WN_SCRATCH_DIR=/nobackup/
    http_proxy=proxy.wisc.edu
    ```

Contents of `CONDORCE_PILOT_JOB_ENV` can reference other HTCondor-CE configuration using HTCondor's configuration
[$() macro expansion](https://htcondor.readthedocs.io/en/lts/admin-manual/introduction-to-configuration.html#configuration-file-macros).
For example, the following HTCondor-CE configuration would result in the following environment for all routed jobs:

=== "HTCondor-CE Configuration"

    ```
    LOCAL_PROXY = proxy.wisc.edu
    CONDORCE_PILOT_JOB_ENV = "WN_SCRATCH_DIR=/nobackup/ http_proxy=$(LOCAL_PROXY)"
    ```

=== "Resulting Environment"

    ```bash
    WN_SCRATCH_DIR=/nobackup/
    http_proxy=proxy.wisc.edu
    ```

To set environment variables per job route, based on incoming job attributes, or using ClassAd functions, add
`default_pilot_job_env` to your job route configuration:
For example, the following HTCondor-CE configuration would result in this environment for a job with these attributes:

    ```hl_lines="3 4 5" 
    JOB_ROUTER_Condor_Pool @=jrt
      UNIVERSE VANILLA
      default_pilot_job_env = strcat("WN_SCRATCH_DIR=/nobackup",
                                     " PILOT_COLLECTOR=", JOB_COLLECTOR,
                                     " ACCOUNTING_GROUP=", toLower(JOB_VO))
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

=== "Incoming Job Attributes"

    ```
    JOB_COLLECTOR = "collector.wisc.edu"
    JOB_VO = "GLOW"
    ```

=== "Resulting Environment"

    ```bash 
    WN_SCRATCH_DIR=/nobackup/
    PILOT_COLLECTOR=collector.wisc.edu
    ACCOUNTING_GROUP=glow
    ```

!!!tip "Debugging job route environment expressions"
    While constructing `default_pilot_job_env` or `set_default_pilot_job_env` expressions, try wrapping your expression
    in [debug()](#debugging-routes) to help with any issues that may arise.
    Make sure to remove `debug()` after you're done!

Editing Attributes…
-------------------

The following functions are operations that can be used to take incoming job attributes and modify them for the routed
job:

1.  `COPY`, `copy_*`
2.  `DELETE`, `delete_*`
3.  `SET`, `set_*`
4.  `EVALSET`, `eval_set_*`

The above operations are evaluated in order:

-   Each function is evaluated in order of appearance.
    For example, the following will set `FOO` in the routed job to the incoming job's `Owner` attribute and then
    subsequently remove `FOO` from the routed job:

        JOB_ROUTER_Condor_Pool @=jrt
          EVALSET FOO = "$(MY.Owner)"
          DELETE FOO
        @jrt

More documentation can be found in the
[HTCondor manual](https://htcondor.readthedocs.io/en/lts/grid-computing/job-router.html#routing-table-entry-commands-and-macro-values)

### Copying attributes

To copy the value of an attribute of the incoming job to an attribute of the routed job, use `COPY`:
The following route copies the `Environment` attribute of the incoming job and sets the attribute `Original_Environment`
on the routed job to the same value:


    ```hl_lines="3"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      UNIVERSE VANILLA
      COPY Environment Original_Environment
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

### Removing attributes

To remove an attribute of the incoming job from the routed job, use `DELETE`.
The following route removes the `Environment` attribute from the routed job:


    ```hl_lines="3"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      UNIVERSE VANILLA
      DELETE Environment
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

### Setting attributes

To set an attribute on the routed job, use `SET`.
The following route sets the Job's `Rank` attribute to 5:

    ```hl_lines="3"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      UNIVERSE VANILLA
      SET Rank = 5
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

### Setting attributes with ClassAd expressions

To set an attribute to a ClassAd expression to be evaluated, use `EVALSET`.
The following route sets the `Experiment` attribute to `atlas.osguser` if the Owner of the incoming job is `osguser`:

    ```hl_lines="3"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      UNIVERSE VANILLA
      EVALSET Experiment = strcat("atlas.", Owner)
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

Limiting the Number of Jobs
---------------------------

This section outlines how to limit the number of total or idle jobs in a specific route
(i.e., if this limit is reached, jobs will no longer be placed in this route).

!!! note
    If you are using an HTCondor batch system, limiting the number of jobs is not the preferred solution:
    HTCondor manages fair share on its own via
    [user priorities and group accounting](https://htcondor.readthedocs.io/en/lts/admin-manual/cm-configuration.html#user-priorities-and-negotiation).

### Total jobs

To set a limit on the number of jobs for a specific route,
set the [MaxJobs](https://htcondor.readthedocs.io/en/lts/grid-computing/job-router.html#index-6) attribute:

    ```hl_lines="3"
    JOB_ROUTER_ROUTE_Condor_Poole @=jrt
      UNIVERSE VANILLA
      MaxJobs = 100
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

### Idle jobs

To set a limit on the number of idle jobs for a specific route,
set the [MaxIdleJobs](https://htcondor.readthedocs.io/en/lts/grid-computing/job-router.html#index-7) attribute:

    ```hl_lines="3"
    JOB_ROUTER_ROUTE_Condor_Poole @=jrt
      UNIVERSE VANILLA
      MaxIdleJobs = 100
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

Debugging Routes
----------------

To help debug expressions in your routes, you can use the `debug()` function.
First, set the debug mode for the JobRouter by editing a file in `/etc/condor-ce/config.d/` to read

```
JOB_ROUTER_DEBUG = D_ALWAYS:2 D_CAT
```

Then wrap the problematic attribute in `debug()`:

    ```hl_lines="2"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      EVALSET Experiment = debug(strcat("atlas", Name))

    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

You will find the debugging output in `/var/log/condor-ce/JobRouterLog`.

Getting Help
------------

If you have any questions or issues with configuring job routes, please [contact us](../../index.md#contact-us) for assistance.
