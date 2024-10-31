For Non-HTCondor Batch Systems
==============================

This page contains information about job routes that can be used if you are running a non-HTCondor pool at your site.

Setting a default batch queue
-----------------------------

To set a default queue for routed jobs, set the variable `default_queue`:

    ```hl_lines="3"
    JOB_ROUTER_ROUTE_Slurm_Cluster @=jrt
      GridResource = "batch slurm"
      default_queue = osg_queue
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Slurm_Cluster
    ```

Setting batch system directives
-------------------------------

To write batch system directives that are not supported in the route examples above, you will need to edit the job
submit script for your local batch system in `/etc/blahp/`
(e.g., if your local batch system is Slurm, edit `/etc/blahp/slurm_local_submit_attributes.sh`).
This file is sourced during submit time and anything printed to stdout is appended to the generated batch system job
submit script.
ClassAd attributes can be passed from the routed job to the local submit attributes script via
`default_CERequirements` attribute, which takes a comma-separated list of other attributes:

    ```
    SET foo = "X"
    SET bar = "Y"
    SET default_CERequirements = "foo,bar"
    ```

This sets `foo` to the string `X` and `bar` to the string `Y` in the environment of the local submit attributes script.

The following example sets the maximum walltime to 1 hour and the accounting group to the `x509UserProxyFirstFQAN`
attribute of the job submitted to a PBS batch system:

    ```hl_lines="4 5 6"
    JOB_ROUTER_ROUTE_Slurm_Cluster @=jrt
         GridResource = "batch slurm"
         SET Walltime = 3600
         SET AccountingGroup = x509UserProxyFirstFQAN
         SET default_CERequirements = "WallTime,AccountingGroup"
    @jrt

    JOB_ROUTER_ROUTE_NAMES = Slurm_Cluster
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
#PBS -A <Incoming job's x509UserProxyFirstFQAN attribute>
```

Getting Help
------------

If you have any questions or issues with configuring job routes, please [contact us](../../index.md#contact-us) for
assistance.
