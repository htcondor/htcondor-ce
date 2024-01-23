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

HTCondor-CE 5 introduces the ability to write job routes using [ClassAd transform syntax](#classad-transforms) in
addition to the [existing configuration syntax](#deprecated-syntax).
The old route configuration syntax continues to be the default in HTCondor-CE 5 but there are benefits to transitioning
to the new syntax as [outlined below](#choosing-a-syntax).

### ClassAd transforms ###

The HTCondor [ClassAd transforms](https://htcondor.readthedocs.io/en/lts/classads/transforms.html) were
originally introduced to HTCondor to perform in-place transformations of user jobs submitted to an HTCondor pool.
In the HTCondor 8.9 series, the Job Router was updated to support transforms and HTCondor-CE 5 adds the configuration
necessary to support routes written as ClassAd transforms.
If configured to use trasnform-based routes, HTCondor-CE routes and transforms jobs that by chaining ClassAd transforms
in the following order:

1.  Each transform in `JOB_ROUTER_PRE_ROUTE_TRANSFORM_NAMES` whose requirements are met by the job
1.  The first transform from `JOB_ROUTER_ROUTE_NAMES` whose requirements are met by the job.
    See [the section on route matching](#how-jobs-match-to-routes) below.
1.  Each transform in `JOB_ROUTER_PRE_ROUTE_TRANSFORM_NAMES` whose requirements are met by the job

### Deprecated syntax ###

!!! warning "Planned Removal of Deprecated Syntax"
    -   `JOB_ROUTER_DEFAULTS`, `JOB_ROUTER_ENTRIES`, `JOB_ROUTER_ENTRIES_CMD`, and `JOB_ROUTER_ENTRIES_FILE` are
    deprecated and will be removed for *V24* of the HTCondor Software Suite. New configuration syntax for the job router
    is defined using `JOB_ROUTER_ROUTE_NAMES` and `JOB_ROUTER_ROUTE_[name]`.
    -   For new syntax example vist:
    [HTCondor Documentation - Job Router](https://htcondor.readthedocs.io/en/lts/grid-computing/job-router.html#an-example-configuration)
    -   **Note:** The removal will occur during the lifetime of the HTCondor *V23* feature series.

Since the inception of HTCondor-CE, job routes have been written as a
[list of ClassAds](https://htcondor.readthedocs.io/en/lts/grid-computing/job-router.html#deprecated-router-configuration).
Each job route’s [ClassAd](https://htcondor.readthedocs.io/en/lts/classads/classad-mechanism.html) is constructed
by combining each entry from the `JOB_ROUTER_ENTRIES` with the `JOB_ROUTER_DEFAULTS`:

-   `JOB_ROUTER_ENTRIES` is a configuration variable whose default is set in `/etc/condor-ce/config.d/02-ce-*.conf` but
    may be overriden by the administrator in subsequent files in `/etc/condor-ce/config.d/`.
-   `JOB_ROUTER_DEFAULTS` is a generated configuration variable that sets default job route values that are required for
    HTCondor-CE's functionality.
    To view its contents in a readable format, run the following command:

        :::console
        user@host $ condor_ce_config_val JOB_ROUTER_DEFAULTS | sed 's/;/;\n/g'

Take care when modifying attributes in `JOB_ROUTER_DEFAULTS`: you may
[add new attributes](writing-job-routes.md#setting-attributes-for-all-routes) and override attributes that are
[set_*](writing-job-routes.md#setting-attributes) in `JOB_ROUTER_DEFAULTS`.

!!! danger "The following may break your HTCondor-CE"
    -   Do **not** set the `JOB_ROUTER_DEFAULTS` configuration variable yourself. This will cause the CE to stop
        functioning.
    -   If a value is set in `JOB_ROUTER_DEFAULTS` with `eval_set_<variable>`, override it by using
        `eval_set_<variable>` in the `JOB_ROUTER_ENTRIES`.
        Do this at your own risk as it may cause the CE to break.

### Choosing a syntax ###

For existing HTCondor-CEs, it's recommended that administrators continue to use the deprecated syntax (the default) and
transition to ClassAd transforms at their own pace.

For new HTCondor-CEs, it's recommended that administrators start with ClassAd transforms.
The [ClassAd transform](#classad-transforms) syntax provides many benefits including:

-   Statements being evaluated in [the order they are written](writing-job-routes.md#editing-attributes)
-   Use of variables that are not included in the resultant job ad
-   Use of simple case statements

Additionally, it is now easier to include job transformations that should be evaluated before or after your routes by
including transforms in the lists of `JOB_ROUTER_PRE_ROUTE_TRANSFORM_NAMES` and `JOB_ROUTER_PRE_ROUTE_TRANSFORM_NAMES`,
respectively.

How Jobs Match to Routes
------------------------

The Job Router considers incoming jobs in the HTCondor-CE SchedD (i.e., jobs visible in
[condor_ce_q](../troubleshooting/debugging-tools.md#condor_ce_q)) that meet the following constraints:

- The job has not already been considered by the Job Router
- The job's universe is standard or vanilla

If the incoming job meets the above constraints, then the job is matched to the first route in `JOB_ROUTER_ROUTE_NAMES`
whose requirements are satisfied by the job's ClassAd.
Additionally:

-   **If you are using the [ClassAd transform syntax](#classad-transforms),** transforms in
    `JOB_ROUTER_PRE_ROUTE_TRANSFORM_NAMES` and `JOB_ROUTER_PRE_ROUTE_TRANSFORM_NAMES` may also have their own
    requirements that determine whether or not that transform is applied.
-   **If you are using the [deprecated syntax](#deprecated-syntax),** you may configure the Job Router to evenly
    distribute jobs across all matching routes (i.e., round-robin matching).
    To do so, add the following configuration to a file in `/etc/condor-ce/config.d/`:

        JOB_ROUTER_ROUND_ROBIN_SELECTION = True

Getting Help
------------

If you have any questions or issues with configuring job routes, please [contact us](../../index.md#contact-us) for
assistance.