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

To release or put routed jobs on hold if they meet certain criteria, use the `Periodic*` family of attributes.
By default, periodic expressions are evaluated once every 300 seconds but this can be changed by setting
`PERIODIC_EXPR_INTERVAL` in your local HTCondor configuration.

In this example, we set the routed job on hold if the job is idle and has been started at least once or if the job has
tried to start more than once.
This will catch jobs which are starting and stopping multiple times.

```hl_lines="5 8"
JOB_ROUTER_ROUTE_Condor_Pool @=jrt
  UNIVERSE VANILLA
  # Puts the routed job on hold if the job's been idle and has been started at least
  # once or if the job has tried to start more than once
  SET PeriodicHold ((NumJobStarts >= 1 && JobStatus == 1) || NumJobStarts > 1)
  # Release routed jobs if the condor_starter couldn't start the executable and 
  # 'VMGAHP_ERR_INTERNAL' is in the HoldReason
  SET PeriodicRelease = (HoldReasonCode == 6 && regexp("VMGAHP_ERR_INTERNAL", HoldReason))
@jrt

JOB_ROUTER_ROUTE_NAMES = Condor_Pool
```
Setting routed job requirements
-------------------------------

If you need to set requirements on your routed job, you will need to use `SET REQUIREMENTS`
instead of `Requirements`.
The `Requirements` attribute filters jobs coming into your CE into different job routes whereas the set function will
set conditions on the routed job that must be met by the worker node it lands on.
For more information on requirements, consult the
[HTCondor manual](https://htcondor.readthedocs.io/en/lts/users-manual/submitting-a-job.html#about-requirements-and-rank).

To ensure that your job lands on a Linux machine in your pool:

```hl_lines="3"
JOB_ROUTER_ROUTE_Condor_Pool @jrt
  UNIVERSE VANILLA
  SET Requirements = (TARGET.OpSys == "LINUX")
@jrt

JOB_ROUTER_ROUTE_NAMES = Condor_Pool
```

### Preserving original job requirements ###

To preserve and include the original job requirements, rather than just setting new requirements, you can use `COPY
Requirements` or `copy_Requirements` to store the current value of `Requirements` to another variable, which we'll call
`original_requirements`.
To do this, replace the above `SET Requirements` or `set_Requirements` lines with:

```
SET Requirements = ($(MY.Requirements)) && (<YOUR REQUIREMENTS EXPRESSION>)
```

### Setting the accounting group based on the credential of the submitted job ###

A common need in the CE is to want to set the accounting identity of the routed job using information from the credential
of the submitter of the job.  This originally was done using information from the x509 certificate, in particular `X509UserProxyVOName`
and `x509UserProxySubject`.  With the switch to SCITOKENs, the equivalent job attributes are `AuthTokenIssuer` and `AuthTokenSubject`. 

It is important to understand that the *condor_schedd* treats `AuthTokenSubject` and `AuthTokenIssuer` as secure attributes. The values
of these attributes cannot be supplied by the *condor_job_router* directly, they will be set based on what credential the *condor_job_router*
uses to submit the routed job.  Because of this the value of these attributes in the routed job is almost never the same as the value in the
original job.  This is different from the way the `x509*` job attributes behaved.

Because of this, the default CE config will copy all attributes that match `AuthToken*` to `orig_AuthToken*` before the route transforms are applied.

Example of setting the accounting group from AuthToken or x509 attributes.

```
JOB_ROUTER_CLASSAD_USER_MAP_NAMES = $(JOB_ROUTER_CLASSAD_USER_MAP_NAMES) AcctGroupMap
CLASSAD_USER_MAPFILE_AcctGroupMap = <path-to-mapfile>

JOB_ROUTER_TRANSFORM_SetAcctGroup @=end
   REQUIREMENTS (orig_AuthTokenSubject ?: x509UserProxySubject) isnt undefined
   EVALSET AcctGroup UserMap("AcctGroupMap", orig_AuthTokenSubject ?: x509UserProxySubject, AcctGroup)
   EVALSET AccountingGroup join(".", AcctGroup, Owner)
@end

JOB_ROUTER_PRE_ROUTE_TRANSFORMS = $(JOB_ROUTER_PRE_ROUTE_TRANSFORMS) SetAcctGroup
```

Refer to the HTCondor documentation for [information on mapfiles](https://htcondor.readthedocs.io/en/lts/admin-manual/security.html?highlight=mapfile#the-unified-map-file-for-authentication).


Getting Help
------------

If you have any questions or issues with configuring job routes, please [contact us](../../index.md#contact-us) for
assistance.
