Releases
========

HTCondor-CE 6 is distributed via RPM and are available from the following Yum repositories:

- [HTCondor stable and current channels](https://research.cs.wisc.edu/htcondor/downloads/)
- [Open Science Grid](https://opensciencegrid.org/docs/common/yum/)


Known Issues
------------

Known bugs affecting HTCondor-CEs can be found in
[Jira](https://opensciencegrid.atlassian.net/issues/?jql=project%20%3D%20HTCONDOR%20AND%20status%20not%20in%20(done%2C%20abandoned)%20and%20component%20%3D%20htcondor-ce%20and%20issuetype%20%3D%20bug)
In particular, the following bugs are of note:

-   C-style comments, e.g. `/* comment */`, in `JOB_ROUTER_ENTRIES` will prevent the JobRouter from routing jobs
    ([HTCONDOR-864](https://opensciencegrid.atlassian.net/browse/HTCONDOR-864)).
    For the time being, remove any comments if you are still using the
    [deprecated syntax](configuration/job-router-overview.md#deprecated-syntax).

Updating to HTCondor-CE 6
-------------------------

!!! note "Updating from HTCondor-CE < 5"
    If updating to HTCondor-CE 6 from HTCondor-CE < 5, be sure to also consult the HTCondor-CE 5
    [upgrade instructions](../v5/releases.md#500).

!!! tip "Finding relevant configuration changes"
    When updating HTCondor-CE RPMs, `.rpmnew` and `.rpmsave` files may be created containing new defaults that you
    should merge or new defaults that have replaced your customzations, respectively.
    To find these files for HTCondor-CE, run the following command:

        :::console
        root@host # find /etc/condor-ce/ -name '*.rpmnew' -name '*.rpmsave'

HTCondor-CE 6 is a major release that aligns its security model with
[HTCondor 9.0's improved security model](https://htcondor.readthedocs.io/en/lts/version-history/upgrading-from-88-to-90-series.html).
As such, upgrades from older versions of HTCondor-CE may require manual intervention.

HTCondor-CE 6 Version History
-----------------------------

This section contains release notes for each version of HTCondor-CE 6.
Full HTCondor-CE version history can be found on [GitHub](https://github.com/htcondor/htcondor-ce/releases).

### 6.0.0 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v6.0.0) includes the following new features:

-   Align HTCondor-CE security configuration with HTCondor defaults
-   Add example configuration on how to ban users
-   Add condor\_ce\_transform\_ads command
-   Improve essential directory checking and creation at startup

Getting Help
------------

If you have any questions about the release process or run into issues with an upgrade, please
[contact us](../index.md#contact-us) for assistance.
