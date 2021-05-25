For HTCondor Batch Systems
==========================

This page contains information about job routes that can be used if you are running an HTCondor pool at your site.

Setting periodic hold or release
--------------------------------

!!! warning "Avoid setting `PERIODIC_REMOVE` expressions"
    The HTCondor Job Router will automatically resubmit jobs that are removed by the underlying batch system, which can
    result in unintended churn.
    Therefore, it is recommended to append removal expressions to HTCondor-CE's configuration by adding the following to
    a file in `/etc/condor-ce/config.d/`

        SYSTEM_PERIODIC_REMOVE = $(SYSTEM_PERIODIC_REMOVE) || <YOUR REMOVE EXPRESSION>

To release or put routed jobs on hold if they meet certain criteria, use the `Periodic_*` family of attributes.
By default, periodic expressions are evaluated once every 300 seconds but this can be changed by setting
`PERIODIC_EXPR_INTERVAL` in your local HTCondor configuration.

In this example, we set the routed job on hold if the job is idle and has been started at least once or if the job has
tried to start more than once.
This will catch jobs which are starting and stopping multiple times.

=== "ClassAd Transform"

    ```hl_lines="5 8"
    JOB_ROUTER_ROUTE_Condor_Pool @=jrt
      TargetUniverse = 5
      # Puts the routed job on hold if the job's been idle and has been started at least
      # once or if the job has tried to start more than once
      SET Periodic_Hold ((NumJobStarts >= 1 && JobStatus == 1) || NumJobStarts > 1)
      # Release routed jobs if the condor_starter couldn't start the executable and 
      # 'VMGAHP_ERR_INTERNAL' is in the HoldReason
      SET Periodic_Release = (HoldReasonCode == 6 && regexp("VMGAHP_ERR_INTERNAL", HoldReason))
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```
=== "Deprecated Syntax"

    ```hl_lines="7 10"
    JOB_ROUTER_ENTRIES @=jre
    [
      TargetUniverse = 5;
      name = "Condor_Pool";
      # Puts the routed job on hold if the job's been idle and has been started at least
      # once or if the job has tried to start more than once
      set_Periodic_Hold = (NumJobStarts >= 1 && JobStatus == 1) || NumJobStarts > 1;
      # Release routed jobs if the condor_starter couldn't start the executable and
      # 'VMGAHP_ERR_INTERNAL' is in the HoldReason
      set_Periodic_Release = HoldReasonCode == 6 && regexp("VMGAHP_ERR_INTERNAL", HoldReason);
    ]
    @jre

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

Setting routed job requirements
-------------------------------

If you need to set requirements on your routed job, you will need to use `SET REQUIREMENTS` or `set_Requirements`
instead of `Requirements` for ClassAd transform and deprecated syntaxes, respectively.
The `Requirements` attribute filters jobs coming into your CE into different job routes whereas the set function will
set conditions on the routed job that must be met by the worker node it lands on.
For more information on requirements, consult the
[HTCondor manual](https://htcondor.readthedocs.io/en/latest/users-manual/submitting-a-job.html#about-requirements-and-rank).

To ensure that your job lands on a Linux machine in your pool:

=== "ClassAd Transform"

    ```hl_lines="3"
    JOB_ROUTER_ROUTE_Condor_Pool @jrt
      TargetUniverse = 5
      SET Requirements = (TARGET.OpSys == "LINUX")
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

=== "Deprecated Syntax"

    ```hl_lines="5"
    JOB_ROUTER_ENTRIES @=jre
    [
      TargetUniverse = 5;
      name = "Condor_Pool";
      set_Requirements =  (TARGET.OpSys == "LINUX");
    ]
    @jre

    JOB_ROUTER_ROUTE_NAMES = Condor_Pool
    ```

### Preserving original job requirements ###

To preserve and include the original job requirements, rather than just setting new requirements, you can use `COPY
Requirements` or `copy_Requirements` to store the current value of `Requirements` to another variable, which we'll call
`original_requirements`.
To do this, replace the above `SET Requirements` or `set_Requirements` lines with:

=== "ClassAd Transform"

    ```
    SET Requirements = ($(MY.Requirements)) && (<YOUR REQUIREMENTS EXPRESSION>)
    ```

=== "Deprecated Syntax"

    ```
    copy_Requirements = "original_requirements";
    set_Requirements = original_requirements && ...;
    ```

Getting Help
------------

If you have any questions or issues with configuring job routes, please [contact us](../../index.md#contact-us) for
assistance.
