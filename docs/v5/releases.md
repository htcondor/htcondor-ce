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

### No longer set `$HOME` by default ###

Older versions of HTCondor-CE set `$HOME` in the routed job to the user's `$HOME` directory on the HTCondor-CE.
To re-enable this behavior, set `USE_CE_HOME_DIR = True` in `/etc/condor-ce/config.d/`.

HTCondor-CE 5 Version History
-----------------------------

This section contains release notes for each version of HTCondor-CE 5.
Full HTCondor-CE version history can be found on [GitHub](https://github.com/htcondor/htcondor-ce/releases).

### 5.1.0 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v5.1.0) includes the following bug-fixes:

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
