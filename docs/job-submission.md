Submitting Jobs to an HTCondor-CE
=================================

This document outlines methods of manual submission to an HTCondor-CE. It is intended for site administrators wishing to verify the functionality of their HTCondor-CE installation and developers writing software to submit jobs to an HTCondor-CE (e.g., pilot jobs).

!!! note
    Most incoming jobs are pilots from factories and that manual submission does not reflect the standard method that jobs are submitted to OSG CE’s.

Submitting Jobs...
------------------

There are two main methods for submitting files to an HTCondor-CE: using the tools bundled with the `htcondor-ce-client` package and using the `condor_submit` command with a submit file. Both methods will test end-to-end job submission but the former method is simpler while the latter will walk you through writing your own submit file.

Before attempting to submit jobs, you will need to generate a proxy from a user certificate before running any jobs. To generate a proxy, run the following command on the host you plan on submitting from:

``` console
user@host $ voms-proxy-init
```

### Using HTCondor-CE tools

There are two HTCondor-CE tools that allow users to test the functionality of their HTCondor-CE: [condor\_ce\_trace](troubleshoot-htcondor-ce#condor_ce_trace) and [condor\_ce\_run](troubleshoot-htcondor-ce#condor_ce_run). The former is the preferred tool as it provides useful feedback if failure occurs while the latter is simply an automated submission tool. These commands may be run from any host that has `htcondor-ce-client` installed, which you may wish to do if you are testing availability of your CE from an external source.

#### condor_ce_trace

`condor_ce_trace` is a Python script that uses HTCondor's Python bindings to run diagnostics, including job submission, against your HTCondor-CE. To submit a job with `condor_ce_trace`, run the following command:

``` console
user@host $ condor_ce_trace --debug condorce.example.com
```

Replacing `condorce.example.com` with the hostname of the CE you wish to test. On success, you will see `Job status: Completed` and the environment of the job on the worker node it landed on. If you do not get the expected output, refer to the [troubleshooting guide](troubleshoot-htcondor-ce#condor_ce_trace).

##### Requesting resources

`condor_ce_trace` doesn't make any specific resource requests so its jobs are only given the default resources by the CE. To request specific resources (or other job attributes), you can specify the `--attribute` option on the command line:

``` console
user@host $ condor_ce_trace --debug --attribute='+resource1=value1'...--attribute='+resourceN=valueN' condorce.example.com
```

To submit a job that requests 4 cores, 4 GB of RAM, a wall clock time of 2 hours, and the 'osg' queue, run the following command:

``` console
user@host $ condor_ce_trace --debug --attribute='+xcount=4' --attribute='+maxMemory=4000' --attribute='+maxWallTime=120' --attribute='+remote_queue=osg' condorce.example.com
```

For a list of other attributes that can be set with the `--attribute` option, consult the [job attributes](#job-attributes) section.

!!! note
    Non HTCondor batch systems may need additional configuration to support these job attributes.  See the [job router recipes](/compute-element/job-router-recipes/#setting-batch-system-directives) for details on how to support them.

#### condor_ce_run

`condor_ce_run` is a Python script that calls `condor_submit` on a generated submit file and tracks its progress with `condor_q`. To submit a job with `condor_ce_run`, run the following command:

``` console
user@host $ condor_ce_run -r condorce.example.com:9619 /bin/env
```

Replacing `condorce.example.com` with the hostname of the CE you wish to test. The command will not return any output until it completes: When it does you will see the environment of the job on the worker noded it landed on. If you do not get the expected output, refer to the [troubleshooting guide](troubleshoot-htcondor-ce#condor_ce_run).

### Using a submit file...

If you are familiar with HTCondor, submitting a job to an HTCondor-CE using a submit file follows the same procedure as submitting a job to an HTCondor batch system: Write a submit file and use `condor_submit` (or in one of our cases, `condor_ce_submit`) to submit the job. This is by virtue of the fact that HTCondor-CE is just a special configuration of HTCondor. The major differences occur in the specific attributes for the submit files outlined below.

#### From the CE host

This method uses `condor_ce_submit` to submit directly to an HTCondor-CE. The only reason we use `condor_ce_submit` in this case is to take advantage of the already running daemons on the CE host.

1.  Write a submit file, `ce_test.sub`:

        ::file hl_lines="10"
        # Required for local HTCondor-CE submission
        universe = vanilla
        use_x509userproxy = true
        +Owner = undefined

        # Files
        executable = ce_test.sh
        output = ce_test.out
        error = ce_test.err
        log = ce_test.log

        # File transfer behavior
        ShouldTransferFiles = YES
        WhenToTransferOutput = ON_EXIT

        # Optional resource requests
        #+xcount = 4            # Request 4 cores
        #+maxMemory = 4000      # Request 4GB of RAM
        #+maxWallTime = 120     # Request 2 hrs of wall clock time
        #+remote_queue = "osg"  # Request the OSG queue

        # Run job once
        queue

    Replacing `ce_test.sh` with the path to the executable you wish to run.

    1. You can use any executable you choose for the `executable` field. If you don't have one in mind, you may use the following example test script:

            #!/bin/bash

            date
            hostname
            env

    2.  Mark the test script as executable:

            :::console
            user@host $ chmod +x ce_test.sh

2. Submit the job:

        :::console
        user@host $ condor_ce_submit ce_test.sub

#### From another host

For this method, you will need a functional HTCondor submit node. If you do not have one readily available, you can install the `condor` package from the OSG repository to get a simple submit node:

1.  Install HTCondor:

        :::console
        root@host # yum install condor

2.  Start the `condor` service:

        :::console
        root@host $ service condor start

Once the `condor` service is running, write a submit file and submit your job:

1.  Write a submit file, `ce_test.sub`:

        ::file hl_lines="4 7"
        # Required for remote HTCondor-CE submission
        universe = grid
        use_x509userproxy = true
        grid_resource = condor condorce.example.com condorce.example.com:9619

        # Files
        executable = ce_test.sh
        output = ce_test.out
        error = ce_test.err
        log = ce_test.log

        # File transfer behavior
        ShouldTransferFiles = YES
        WhenToTransferOutput = ON_EXIT

        # Optional resource requests
        #+xcount = 4            # Request 4 cores
        #+maxMemory = 4000      # Request 4GB of RAM
        #+maxWallTime = 120     # Request 2 hrs of wall clock time
        #+remote_queue = "osg"  # Request the OSG queue

        # Run job once
        queue

    Replacing `ce_test.sh` with the path to the executable you wish to run and `condorce.example.com` with the hostname of the CE you wish to test.
    !!! note
        The `grid_resource` line should start with `condor` and is not related to which batch system you are using.

    1.  You can use any executable you choose for the `executable` field. If you don't have one in mind, you may use the following example test script:

            #!/bin/bash

            date
            hostname
            env

    2.  Mark the test script as executable:

            :::console
            user@host $ chmod +x ce_test.sh

2. Submit the job:

        :::console
        user@host $ condor_submit ce_test.sub

#### Tracking job progress

When the job completes, stdout will be placed into `ce_test.out`, stderr will be placed into `ce_test.err`, and HTCondor logging information will be placed in `ce_test.log`. You can track job progress by looking at the condor queue by running the following command on the CE host:

``` console
user@host $ condor_ce_q
```

Using the following table to determine job status:

| This value in the `ST` column... | Means that the job is... |
|:---------------------------------|:-------------------------|
| I                                | idle                     |
| C                                | complete                 |
| X                                | being removed            |
| H                                | held                     |
| <                                | transferring input       |
| >                                | transferring output      |

How Job Routes Affect Your Job
------------------------------

Upon successful submission of your job, the Job Router takes control of your job by matching it to routes and submitting a transformed job to your batch system.

### Matching

See [this section](/compute-element/job-router-recipes#how-jobs-match-to-job-routes) for details on how jobs are matched
to job routes.

**Examples**

The following three routes only perform filtering and submission of routed jobs to an HTCondor batch system. The only differences are in the types of jobs that they match:

-   **Route 1:** Matches jobs whose attribute `foo` is equal to `bar`.
-   **Route 2:** Matches jobs whose attribute `foo` is equal to `baz`.
-   **Route 3:** Matches jobs whose attribute `foo` is neither equal to `bar` nor `baz`.

!!! note
    Setting a custom attribute for job submission requires the `+` prefix in your submit file but it is unnecessary in the job routes.

```
JOB_ROUTER_ENTRIES = [ \
     TargetUniverse = 5; \
     name = "Route 1"; \
     Requirements = (TARGET.foo =?= "bar"); \
] \
[ \
     TargetUniverse = 5; \
     name = "Route 2"; \
     Requirements = (TARGET.foo =?= "baz"); \
] \
[ \
     TargetUniverse = 5; \
     name = "Route 3"; \
     Requirements = (TARGET.foo =!= "bar") && (TARGET.foo =!= "baz"); \
]
```

If a user submitted their job with `+foo = bar` in their submit file, the job would match `Route 1`.

### Route defaults

[Route defaults](job-router-recipes#setting-a-default) can be set for batch system queue, maximum memory, number of cores to request, and maximum walltime. The submitting user can override any of these by setting the corresponding [attribute](#job-attributes) in their job.

**Examples**

The following route takes all incoming jobs and submits them to an HTCondor batch system requesting 1GB of memory.

```
JOB_ROUTER_ENTRIES = [ \
     TargetUniverse = 5; \
     name = "Route 1"; \
     set_default_maxMemory = 1000; \
]
```

A user could submit their job with the attribute `+maxMemory=2000` and that job would be submitted requesting 2GB memory instead of the default of 1GB.

Troubleshooting Your Jobs
-------------------------

#### Troubleshooting

All interactions between `condor_submit` and the CE will be recorded in the file specified by the `log` attribute in your submit file. This includes acknowledgement of the job in your local queue, connection to the CE, and a record of job completion:

```
000 (786.000.000) 12/09 16:49:55 Job submitted from host: <131.225.154.68:53134>
...
027 (786.000.000) 12/09 16:50:09 Job submitted to grid resource
    GridResource: condor condorce.example.com condorce.example.com:9619
    GridJobId: condor condorce.example.com condorce.example.com:9619 796.0
...
005 (786.000.000) 12/09 16:52:19 Job terminated.
        (1) Normal termination (return value 0)
                Usr 0 00:00:00, Sys 0 00:00:00  -  Run Remote Usage
                Usr 0 00:00:00, Sys 0 00:00:00  -  Run Local Usage
                Usr 0 00:00:00, Sys 0 00:00:00  -  Total Remote Usage
                Usr 0 00:00:00, Sys 0 00:00:00  -  Total Local Usage
        0  -  Run Bytes Sent By Job
        0  -  Run Bytes Received By Job
        0  -  Total Bytes Sent By Job
        0  -  Total Bytes Received By Job
```

If there are issues contacting the CE, you will see error messages about a 'Down Globus Resource':

```
020 (788.000.000) 12/09 16:56:17 Detected Down Globus Resource
    RM-Contact: fermicloud133.fnal.gov
...
026 (788.000.000) 12/09 16:56:17 Detected Down Grid Resource
    GridResource: condor condorce.example.com condorce.example.com:9619
```

This indicates a communication issue with your CE that can be diagnosed with [condor\_ce\_ping](troubleshoot-htcondor-ce#condor_ce_ping).

Reference
---------

Here are some other HTCondor-CE documents that might be helpful:

-   [HTCondor-CE overview and architecture](htcondor-ce-overview)
-   [Installing HTCondor-CE](install-htcondor-ce)
-   [Configuring HTCondor-CE job routes](job-router-recipes)
-   [The HTCondor-CE troubleshooting guide](troubleshoot-htcondor-ce)

### Job attributes

The following table is a reference of job attributes that can be included in HTCondor submit files and their GlobusRSL equivalents. A more comprehensive list of submit file attributes specific to HTCondor-CE can be found in the [HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_submit.html#SECTION0012574000000000000000).

| **HTCondor Attribute** | **Globus RSL** | **Summary** |
|------------------------------------------------------------------------------------------------------|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| [arguments](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_submit.html#93578)               | arguments               | Arguments that will be provided to the executable for the job.                                                                               |
| [error](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_submit.html#93627)                   | stderr                  | Path to the file on the client machine that stores stderr from the job.                                                                      |
| [executable](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_submit.html#93633)              | executable              | Path to the file on the client machine that the job will execute.                                                                            |
| [input](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_submit.html#93652)                   | stdin                   | Path to the file on the client machine that stores input to be piped into the stdin of the job.                                              |
| +maxMemory                                                                                           | maxMemory               | The amount of memory in MB that you wish to allocate to the job.                                                                             |
| +maxWallTime                                                                                         | maxWallTime             | The maximum walltime (in minutes) the job is allowed to run before it is removed.                                                            |
| [output](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_submit.html#93690)                  | stdout                  | Path to the file on the client machine that stores stdout from the job.                                                                      |
| +remote\_queue                                                                                       | queue                   | Assign job to the target queue in the scheduler. Note that the queue name should be in quotes.                                               |
| [transfer\_input\_files](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_submit.html#93968)  | file\_stage\_in         | A comma-delimited list of all the files and directories to be transferred into the working directory for the job, before the job is started. |
| [transfer\_output\_files](http://research.cs.wisc.edu/htcondor/manual/v8.6/condor_submit.html#93976) | transfer\_output\_files | A comma-delimited list of all the files and directories to be transferred back to the client, after the job completes.                       |
| +xcount                                                                                              | xcount                  | The number of cores to allocate for the job.                                                                                                 |

If you are setting an attribute to a string value, make sure enclose the string in double-quotes (`"`), otherwise HTCondor-CE will try to find an attribute by that name.
