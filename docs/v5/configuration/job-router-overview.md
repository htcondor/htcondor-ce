Job Router Configuration Overview
=================================

The [JobRouter](https://htcondor.readthedocs.io/en/latest/grid-computing/job-router.html) is at the heart of HTCondor-CE
and allows admins to transform and direct jobs to specific batch systems.
Customizations are made in the form of job routes where each route corresponds to a separate job transformation:
If an incoming job matches a job route's requirements, the route creates a transformed job (referred to as the 'routed
job') that is then submitted to the batch system.
The CE package comes with default routes located in `/etc/condor-ce/config.d/02-ce-*.conf` that provide enough basic
functionality for a small site.

If you have needs beyond delegating all incoming jobs to your batch system as they are, this document provides examples
of common job routes and job route problems.

!!! note "Definitions"
    - **Incoming Job**: A job which was submitted to the CE from an external source.
    - **Routed Job**: A job that has been transformed by the JobRouter.

Quirks and Pitfalls
-------------------

-   If a value is set in [JOB\_ROUTER\_DEFAULTS](#job_router_defaults) with `eval_set_<variable>`, override it by using `eval_set_<variable>` in the `JOB_ROUTER_ENTRIES`. Do this at your own risk as it may cause the CE to break.
-   Make sure to run `condor_ce_reconfig` after changing your routes, otherwise they will not take effect.
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

The job router considers jobs in the queue ([condor_ce_q](troubleshooting/troubleshooting.md#condor_ce_q)) that
meet the following constraints:

- The job has not already been considered by the job router
- The job is associated with an unexpired x509 proxy
- The job's universe is standard or vanilla

If the job meets the above constraints, then the job's ClassAd is compared against each
[route's requirements](#filtering-jobs-based-on).
If the job only meets one route's requirements, the job is matched to that route.
If the job meets the requirements of multiple routes,  the route that is chosen depends on your version of HTCondor
(`condor_version`):

| If your version of HTCondor is... | Then the route is chosen by...                                                                                               |
|-----------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| < 8.7.1                           | **Round-robin** between all matching routes. In this case, we recommend making each route's requirements mutually exclusive. |
| >= 8.7.1, < 8.9.5                 | **First matching route** where routes are considered in hash-table order. In this case, we recommend making each route's requirements mutually exclusive. |
| >= 8.9.5                          | **First matching route** where routes are considered in the order specified by [JOB_ROUTER_ROUTE_NAMES](https://htcondor.readthedocs.io/en/latest/admin-manual/configuration-macros.html#JOB_ROUTER_ROUTE_NAMES) |

!!! bug "Job Route Order"
    For HTCondor versions < 8.9.5 (as well as versions >= 8.7.1 and < 8.8.7) the order of job routes does not match the
    order in which they are configured.
    As a result, we recommend updating to at least HTCondor 8.9.5 (or 8.8.7) and specifying the names of your routes in
    `JOB_ROUTER_ROUTE_NAMES` in the order that you'd like them considered.

If you are using HTCondor >= 8.7.1 and would like to use round-robin matching, add the following text to a file in
`/etc/condor-ce/config.d/`:

```
JOB_ROUTER_ROUND_ROBIN_SELECTION = True
```
