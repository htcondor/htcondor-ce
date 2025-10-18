Job Router Configuration Overview
=================================

The [HTCondor Job Router](https://htcondor.readthedocs.io/en/lts/grid-computing/job-router.html) is at the heart of
HTCondor-CE and allows admins to transform and direct jobs to specific batch systems.
Customizations are made in the form of job routes where each route corresponds to a separate job transformation:
If an incoming job matches a job route's requirements, the route creates a transformed job (referred to as the 'routed
job') that is then submitted to the batch system.
The CE package comes with default routes located in `/etc/condor-ce/config.d/02-ce-*.conf` that provide enough basic
functionality for a small site.

If you have needs beyond delegating all incoming jobs to your batch system as they are, this document provides an
overview of how to configure your HTCondor-CE Job Router

!!! note "Definitions"
    - **Incoming Job**: A job which was submitted to HTCondor-CE from an external source.
    - **Routed Job**: A job that has been transformed by the Job Router.

Route Syntaxes
--------------

HTCondor-CE 5 introduced the ability to write job routes using [ClassAd transform syntax](#classad-transforms).

### ClassAd transforms ###

The HTCondor [ClassAd transforms](https://htcondor.readthedocs.io/en/lts/classads/transforms.html) were
originally introduced to HTCondor to perform in-place transformations of user jobs submitted to an HTCondor pool.
In the HTCondor 8.9 series, the Job Router was updated to support transforms and HTCondor-CE 5 adds the configuration
necessary to support routes written as ClassAd transforms.
If configured to use transform-based routes, HTCondor-CE routes and transforms jobs that by chaining ClassAd transforms
in the following order:

1.  Each transform in `JOB_ROUTER_PRE_ROUTE_TRANSFORM_NAMES` whose requirements are met by the job
1.  The first transform from `JOB_ROUTER_ROUTE_NAMES` whose requirements are met by the job.
    See [the section on route matching](#how-jobs-match-to-routes) below.
1.  Each transform in `JOB_ROUTER_POST_ROUTE_TRANSFORM_NAMES` whose requirements are met by the job

### Required syntax ###

For existing HTCondor-CEs, it's required that administrators stop using the deprecated syntax and
transition to ClassAd transforms now.

For new HTCondor-CEs, it's required that administrators start with ClassAd transforms.
The [ClassAd transform](#classad-transforms) syntax provides many benefits including:

-   Statements being evaluated in [the order they are written](writing-job-routes.md#editing-attributes)
-   Use of variables that are not included in the resultant job ad
-   Use simple case-like logic

Additionally, it is now easier to include job transformations that should be evaluated before or after your routes by
including transforms in the lists of `JOB_ROUTER_PRE_ROUTE_TRANSFORM_NAMES` and `JOB_ROUTER_POST_ROUTE_TRANSFORM_NAMES`,
respectively.

### Converting to ClassAd transforms ###

For existing HTCondor-CE's utilizing the deprecated syntax can do the following steps to convert to using the ClassAd
transform syntax:

1.  Output the current configuration by running the following:

        condor_ce_config_val -summary > summary-file

2.  Convert the stored configuration by running the following:

        condor_transform_ads -convert:file summary-file > 90-converted-job-routes.conf

3.  Place the `90-converted-job-routes.conf` from the previous command into the `/etc/condor-ce/config.d`.

    !!! note "Potential need to rename generated config"
        The files in `/etc/condor-ce/config.d` are read in lexicographical order.
        So if you define your current job router configuration in `/etc/condor-ce/config.d` in a file that is read
        later, e.g. `95-local.conf`, you will need to rename your generated config file, e.g. `96-generated-job-routes.conf`.

4.  Tweak new job routes as needed. For assistance please reach out to [htcondor-users@cs.wisc.edu](mailto:htcondor-users@cs.wisc.edu)
6.  Restart the HTCondor-CE

!!! note "Not Using Custom Job Routes?"
    Conversion of job router syntax from the deprecated syntax to ClassAd transform syntax needs to occur if custom job
    routes have been configured.

How Jobs Match to Routes
------------------------

The Job Router considers incoming jobs in the HTCondor-CE SchedD (i.e., jobs visible in
[condor_ce_q](../troubleshooting/debugging-tools.md#condor_ce_q)) that meet the following constraints:

- The job has not already been considered by the Job Router
- The job's universe is standard or vanilla

If the incoming job meets the above constraints, then the job is matched to the first route in `JOB_ROUTER_ROUTE_NAMES`
whose requirements are satisfied by the job's ClassAd.
Additionally:

-   Transforms in
    `JOB_ROUTER_PRE_ROUTE_TRANSFORM_NAMES` and `JOB_ROUTER_POST_ROUTE_TRANSFORM_NAMES` may also have their own
    requirements that determine whether or not that transform is applied.

Getting Help
------------

If you have any questions or issues with configuring job routes, please [contact us](../../index.md#contact-us) for
assistance.
