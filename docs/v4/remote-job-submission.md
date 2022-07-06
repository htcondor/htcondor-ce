Submitting Jobs Remotely to an HTCondor-CE
==========================================

This document outlines how to submit jobs to an HTCondor-CE from a remote client using two different methods:

-   With dedicated tools for quickly verifying end-to-end job submission, and
-   From an existing HTCondor submit host, useful for developing pilot submission infrastructure

If you are the administrator of an HTCondor-CE, consider verifying your HTCondor-CE using the
[administrator-focused documentation](verification.md).

Before Starting
---------------

Before attempting to submit jobs to an HTCondor-CE as documented below, ensure the following:

-   The HTCondor-CE administrator has independently [verified their HTCondor-CE](verification.md)
-   The HTCondor-CE administrator has added your credential information (e.g. SciToken or grid proxy) to the HTCondor-CE
    [authentication configuration](installation/htcondor-ce.md#configuring-authentication)
-   Your credentials are valid and unexpired

Submission with Debugging Tools
-------------------------------

The HTCondor-CE client contains debugging tools designed to quickly test an HTCondor-CE.
To use these tools, install the RPM package from the [relevant Yum repository](releases.md):

``` console
root@host # yum install htcondor-ce-client
```

### Verify end-to-end submission ###

The HTCondor-CE client package includes a debugging tool that perform tests of end-to-end job submission called
[condor\_ce\_trace](troubleshooting/troubleshooting.md#condor_ce_trace).
To submit a diagnostic job with `condor_ce_trace`, run the following command:

``` console
user@host $ condor_ce_trace --debug <CE HOST>
```

Replacing `<CE HOST>` with the hostname of the CE you wish to test.
On success, you will see `Job status: Completed` and the job's environment on the worker node where it ran.
If you do not see the expected output, refer to the
[troubleshooting guide](troubleshooting/troubleshooting.md#condor_ce_trace).

!!! note "CONDOR_CE_TRACE_ATTEMPTS"
    For a busy site cluster, it may take longer than the default 5 minutes to test end-to-end submission.
    To extend the length of time that `condor_ce_trace` waits for the job to complete, prepend the command with
    `_condor_CONDOR_CE_TRACE_ATTEMPTS=<TIME IN SECONDS>`.

### (Optional) Requesting resources ###

`condor_ce_trace` doesn't make any specific resource requests so its jobs are only given the default resources as
configured by the HTCondor-CE you are debugging.
To request specific resources (or other job attributes), you can specify the `--attribute` option on the command line:

``` console
user@host $ condor_ce_trace --debug \
                            --attribute='+resource1=value1'... \
                            --attribute='+resourceN=valueN' \
                            ce.htcondor.org
```

For example, the following command submits a test job requesting 4 cores, 4 GB of RAM, a wall clock time of 2 hours, and
the 'osg' queue, run the following command:

``` console
user@host $ condor_ce_trace --debug \
                            --attribute='+xcount=4' \
                            --attribute='+maxMemory=4000' \
                            --attribute='+maxWallTime=120' \
                            --attribute='+remote_queue=osg' \
                            ce.htcondor.org
```

For a list of other attributes that can be set with the `--attribute` option, consult the
[submit file commands](#submit-file-commands) section.

!!! note
    Non-HTCondor batch systems may need additional HTCondor-CE configuration to support these job attributes.
    See the [batch system integration](batch-system-integration.md#setting-batch-system-directives)
    for details on how to support them.

Submission with HTCondor Submit
-------------------------------

If you need to submit more complicated jobs than a trace job as described [above](#submission-with-debugging-tools)
(e.g. for developing piilot job submission infrastructures) and have access to an HTCondor submit host,
you can use standard HTCondor submission tools.

### Submit the job ###

To submit jobs to a remote HTCondor-CE (or any other externally facing HTCondor SchedD) from an HTCondor submit host,
you need to construct an HTCondor submit file describing an
[HTCondor-C job](https://htcondor.readthedocs.io/en/v9_0/grid-computing/grid-universe.html#htcondor-c-the-condor-grid-type):

1.  Write a submit file, `ce_test.sub`:

        # Required for remote HTCondor-CE submission
        universe = grid
        use_x509userproxy = true
        grid_resource = condor ce.htcondor.org ce.htcondor.org:9619

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

        # Submit a single job
        queue

    Replacing `ce_test.sh` with the path to the executable you wish to run and `ce.htcondor.org` with the hostname
    of the CE you wish to test.

    !!! note
        The `grid_resource` line should start with `condor` and is not related to which batch system you are using.

1. Submit the job:

        :::console
        user@host $ condor_submit ce_test.sub

### Tracking job progress ###

You can track job progress by by querying the local queue:

``` console
user@host $ condor__q
```

As well as the remote HTCondor-CE queue:

``` console
user@host $ condor__q -name <CE HOST> -pool <CE HOST>:9619
```

Replacing `<CE HOST>` with the FQDN of the HTCondor-CE.
For reference, `condor_q -help status` will provide details of job status codes.

```
user@host $ condor_q -help status | tail

    JobStatus codes:
	 1 I IDLE
	 2 R RUNNING
	 3 X REMOVED
	 4 C COMPLETED
	 5 H HELD
	 6 > TRANSFERRING_OUTPUT
	 7 S SUSPENDED
```

### Troubleshooting ###

All interactions between `condor_submit` and the HTCondor-CE will be recorded in the file specified by the `log` command
in your submit file.
This includes acknowledgement of the job in your local queue, connection to the CE, and a record of job completion:

```
000 (786.000.000) 12/09 16:49:55 Job submitted from host: <131.225.154.68:53134>
...
027 (786.000.000) 12/09 16:50:09 Job submitted to grid resource
    GridResource: condor ce.htcondor.org ce.htcondor.org:9619
    GridJobId: condor ce.htcondor.org ce.htcondor.org:9619 796.0
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

If there are issues contacting the HTCondor-CE, you will see error messages about a `Down Globus Resource`:

```
020 (788.000.000) 12/09 16:56:17 Detected Down Globus Resource
    RM-Contact: ce.htcondor.org
...
026 (788.000.000) 12/09 16:56:17 Detected Down Grid Resource
    GridResource: condor ce.htcondor.org ce.htcondor.org:9619
```

This indicates a communication issue with the HTCondor-CE that may be diagnosed with
[condor\_ce\_ping](troubleshooting/troubleshooting.md#condor_ce_ping).

Submit File Commands
--------------------

The following table is a reference of commands that are commonly included in HTCondor submit files used for HTCondor-CE
resource allocation requests.
A more comprehensive list of submit file commands specific to HTCondor can be found in the
[HTCondor manual](https://htcondor.readthedocs.io/en/v9_0/man-pages/condor_submit.html).

!!!tip "HTCondor string values"
    If you are setting an attribute to a string value, make sure enclose the string in double-quotes (`"`)

| **Command**                                                                                                 | **Description**                                                                                                                                                                              |
|-------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [arguments](https://htcondor.readthedocs.io/en/v9_0/man-pages/condor_submit.html#index-13)                | Arguments that will be provided to the executable for the resource allocation request.                                                                                                       |
| [error](https://htcondor.readthedocs.io/en/v9_0/man-pages/condor_submit.html#index-18)                    | Path to the file on the client host that stores stderr from the resource allocation request.                                                                                                 |
| [executable](https://htcondor.readthedocs.io/en/v9_0/man-pages/condor_submit.html#index-19)               | Path to the file on the client host that the resource allocation request will execute.                                                                                                       |
| [input](https://htcondor.readthedocs.io/en/v9_0/man-pages/condor_submit.html#index-23)                    | Path to the file on the client host that stores input to be piped into the stdin of the resource allocation request.                                                                         |
| +maxMemory                                                                                                  | The amount of memory in MB that you wish to allocate to the resource allocation request.                                                                                                     |
| +maxWallTime                                                                                                | The maximum walltime (in minutes) the resource allocation request is allowed to run before it is removed.                                                                                    |
| [output](https://htcondor.readthedocs.io/en/v9_0/man-pages/condor_submit.html#index-37)                   | Path to the file on the client host that stores stdout from the resource allocation request.                                                                                                 |
| +remote\_queue                                                                                              | Assign resource allocation request to the target queue in the scheduler.                                                                                                                     |
| [transfer\_input\_files](https://htcondor.readthedocs.io/en/v9_0/man-pages/condor_submit.html#index-110)  | A comma-delimited list of all the files and directories to be transferred into the working directory for the resource allocation request, before the resource allocation request is started. |
| [transfer\_output\_files](https://htcondor.readthedocs.io/en/v9_0/man-pages/condor_submit.html#index-113) | A comma-delimited list of all the files and directories to be transferred back to the client, after the resource allocation request completes.                                               |
| +WantWholeNode                                                                                              | When set to `True`, request entire node for the resource allocation request (HTCondor batch systems only)                                                                                    |
| +xcount                                                                                                     | The number of cores to allocate for the resource allocation request.                                                                                                                         |

Getting Help
------------

If you have any questions or issues with job submission, please [contact us](../index.md#contact-us) for assistance.
