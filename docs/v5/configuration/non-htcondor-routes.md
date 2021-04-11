For Non-HTCondor Batch Systems
==============================

This section contains information about job routes that can be used if you are running a non-HTCondor batch system at your site.

Setting a default batch queue
-----------------------------

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

Setting batch system directives
-------------------------------

To write batch system directives that are not supported in the route examples above, you will need to edit the job submit script for your local batch system in `/etc/blahp/` (e.g., if your local batch system is PBS, edit `/etc/blahp/pbs_local_submit_attributes.sh`). This file is sourced during submit time and anything printed to stdout is appended to the batch system job submit script. ClassAd attributes can be passed from the routed job to the local submit attributes script via `set_default_CERequirements`, which takes a comma-separated list of other attributes:

```
set_foo = X;
set_bar = "Y";
set_default_CERequirements = "foo,bar";
```

This sets `foo` to value `X` and `bar` to the string `Y` in the environment of the local submit attributes script.

The following example sets the maximum walltime to 1 hour and the accounting group to the `x509UserProxyFirstFQAN` attribute of the job submitted to a PBS batch system:

```hl_lines="5"
JOB_ROUTER_ENTRIES @=jre [
     GridResource = "batch pbs";
     TargetUniverse = 9;
     name = "Setting job submit variables";
     set_Walltime = 3600;
     set_AccountingGroup = x509UserProxyFirstFQAN;
     set_default_CERequirements = "WallTime,AccountingGroup";
]
@jre
```

With `/etc/blahp/pbs_local_submit_attributes.sh` containing:

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

Getting Help
------------

If you have any questions or issues with configuring job routes, please [contact us](../../index.md#contact-us) for assistance.
