Releases
========

HTCondor-CE 5 is distributed via RPM and are available from the following Yum repositories:

- [HTCondor development](https://research.cs.wisc.edu/htcondor/yum/)
- [Open Science Grid](https://opensciencegrid.org/docs/common/yum/)


Updating to HTCondor-CE 5
-------------------------

!!! note "Updating from HTCondor-CE <=3"
    If updating to HTCondor-CE 5 from HTCondor-CE <= 3, be sure to also consult the HTCondor-CE 4
    [upgrade instructions](../v4/releases.md#updating-to-htcondor-ce-4).

HTCondor-CE 5 is a major release that adds many features and overhauls the default configuration.
As such, upgrades from older versions of HTCondor-CE may require manual intervention:

### Support for ClassAd transforms added to the JobRouter ###

!!! danger "Transforms will override `JOB_ROUTER_ENTRIES` routes with the same name"
    Even if you do not plan on immediately using the new syntax, it's important to note that route transforms will
    override `JOB_ROUTER_ENTRIES` routes with the same name.
    In other words, the route transform names returned by `condor_ce_config_val -dump -v JOB_ROUTER_ROUTE_` should only
    appear in your list of used routes returned by `condor_ce_config_val JOB_ROUTER_ROUTE_NAMES` if you
    intend to use the new transform syntax.

HTCondor-CE now includes default [ClassAd transforms](https://htcondor.readthedocs.io/en/latest/misc-concepts/transforms.html)
equivalent to its `JOB_ROUTER_DEFAULTS`, allowing administrators to write job routes using the transform synatx.
The old syntax continues to be the default in HTCondor-CE 5.
Writing routes in the new syntax provides many benefits including:

-   Statements being evaluated in the order they are written
-   Use of variables that are not included in the resultant job ad
-   Use of simple case statements.

Additionally, it is now easier to include transforms that should be evaluated before or after your routes by including
transforms in the lists of `JOB_ROUTER_PRE_ROUTE_TRANSFORMS` and `JOB_ROUTER_PRE_ROUTE_TRANSFORMS`, respectively.
To use the new transform syntax:

1.  Disable use of `JOB_ROUTER_ENTRIES` by setting the following in `/etc/condor-ce/config.d/`:

        :::console
        JOB_ROUTER_USE_DEPRECATED_ROUTER_ENTRIES = False

1.  Set `JOB_ROUTER_ROUTE_<ROUTE_NAME>` to a job route in the new transform syntax where `<ROUTE_NAME>` is the name of
    the route that you'd like to be reflected in logs and tool output.

1.  Add the above `<ROUTE_NAME>` to the list of routes in `JOB_ROUTER_ROUTE_NAMES`

### No longer set `$HOME` by default ###

Older versions of HTCondor-CE set `$HOME` in the routed job to the user's `$HOME` directory on the HTCondor-CE.
To re-enable this behavior, set `USE_CE_HOME_DIR = True` in `/etc/condor-ce/config.d/`.

HTCondor-CE 5 Version History
-----------------------------

This section contains release notes for each version of HTCondor-CE 5.
Full HTCondor-CE version history can be found on [GitHub](https://github.com/htcondor/htcondor-ce/releases).

### 5.1.0 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v5.1.0) includes the following new features:

-   Add support for [ClassAd transforms](https://htcondor.readthedocs.io/en/latest/misc-concepts/transforms.html)
    to the JobRouter ([HTCONDOR-243](https://opensciencegrid.atlassian.net/browse/HTCONDOR-243))

This release also includes the following bug-fixes:

-   APEL reporting scripts now use `PER_JOB_HISTORY_DIR` to collect job data. 
    ([HTCONDOR_293](https://opensciencegrid.atlassian.net/browse/HTCONDOR-293))

### 5.0.0 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v5.0.0) includes the following new features:

-   Python 3 and Enterprise Linux 8 support
    ([HTCONDOR_13](https://opensciencegrid.atlassian.net/browse/HTCONDOR-13))
-   HTCondor-CE no longer sets `$HOME` in routed jobs by default
    ([HTCONDOR-176](https://opensciencegrid.atlassian.net/browse/HTCONDOR-176))
-   Whole node jobs (local HTCondor batch systems only) now make use of GPUs
    ([HTCONDOR-103](https://opensciencegrid.atlassian.net/browse/HTCONDOR-103))
-   HTCondor-CE Central Collectors now prefer GSI over SSL authentication
    ([HTCONDOR-237](https://opensciencegrid.atlassian.net/browse/HTCONDOR-237))
-   HTCondor-CE registry now validates the value of submitted client codes
    ([HTCONDOR-241](https://opensciencegrid.atlassian.net/browse/HTCONDOR-241))
-   Automatically remove CE jobs that exceed their `maxWalltime` (if defined) or the configuration value of
    `ROUTED_JOB_MAX_TIME` (default: 4320 sec/72 hrs)

This release also includes the following bug-fixes:

-   Fix a circular configuration definition in the HTCondor-CE View that resulted in 100% CPU usage by the
    `condor_gangliad` daemon ([HTCONDOR-161](https://opensciencegrid.atlassian.net/browse/HTCONDOR-161))


Getting Help
------------

If you have any questions about the release process or run into issues with an upgrade, please
[contact us](../index.md#contact-us) for assistance.
