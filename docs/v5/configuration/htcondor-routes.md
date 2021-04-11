For HTCondor Batch Systems
==========================

This section contains information about job routes that can be used if you are running an HTCondor batch system at your site.

Setting periodic hold, release or remove
----------------------------------------

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

Setting routed job requirements
-------------------------------

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

### Preserving original job requirements ###

To preserve and include the original job requirements, rather than just setting new requirements, you can use
`copy_Requirements` to store the current value of `Requirements` to another variable, which we'll call
`original_requirements`.
To do this, replace the above `set_Requirements` line with:

```
copy_Requirements = "original_requirements";
set_Requirements = original_requirements && ...;
```

Getting Help
------------

If you have any questions or issues with configuring job routes, please [contact us](../../index.md#contact-us) for assistance.
