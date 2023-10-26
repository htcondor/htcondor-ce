Releases
========

HTCondor-CE 23 is distributed via RPM and are available from the following Yum repositories:

- [HTCondor stable and current channels](https://research.cs.wisc.edu/htcondor/downloads/)
- [Open Science Grid](https://opensciencegrid.org/docs/common/yum/)


Known Issues
------------

Known bugs affecting HTCondor-CEs can be found in
[Jira](https://opensciencegrid.atlassian.net/issues/?jql=project%20%3D%20HTCONDOR%20AND%20status%20not%20in%20(done%2C%20abandoned)%20and%20component%20%3D%20htcondor-ce%20and%20issuetype%20%3D%20bug)

Updating to HTCondor-CE 23
--------------------------

!!! note "Updating from HTCondor-CE < 6"
    If updating to HTCondor-CE 23 from HTCondor-CE < 5, be sure to also consult the HTCondor-CE 6
    [upgrade instructions](../v6/releases.md#500).

!!! tip "Finding relevant configuration changes"
    When updating HTCondor-CE RPMs, `.rpmnew` and `.rpmsave` files may be created containing new defaults that you
    should merge or new defaults that have replaced your customzations, respectively.
    To find these files for HTCondor-CE, run the following command:

        :::console
        root@host # find /etc/condor-ce/ -name '*.rpmnew' -name '*.rpmsave'

HTCondor-CE 23 is very close in functionality to HTCondor-CE 6.
As such, upgrading should be very easy.

HTCondor-CE 23 Version History
------------------------------

This section contains release notes for each version of HTCondor-CE 23.
Full HTCondor-CE version history can be found on [GitHub](https://github.com/htcondor/htcondor-ce/releases).

### 23.0.0 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v23.0.0) includes the following new features:

-   Add grid CA and host certificate/key locations to default SSL search paths
-   Verifies that HTCondor-CE can access the local HTCondor's SPOOL directory
-   Can use ``condor_ce_trace`` without SciToken to test batch system integration
-   ``condor_ce_upgrade_check`` checks compatibility with HTCondor 23.0
-   Adds deprecation warnings for old job router configuration syntax

Getting Help
------------

If you have any questions about the release process or run into issues with an upgrade, please
[contact us](../index.md#contact-us) for assistance.
