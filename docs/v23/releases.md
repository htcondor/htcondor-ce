Releases
========

HTCondor-CE 23 is distributed via RPM and are available from the following Yum repositories:

- [HTCondor LTS and Feature Releases](https://htcondor.org/htcondor/download/)
- [The OSG Consortium](https://osg-htc.org/docs/common/yum/)


Known Issues
------------

Known bugs affecting HTCondor-CEs can be found in
[Jira](https://opensciencegrid.atlassian.net/issues/?jql=project%20%3D%20HTCONDOR%20AND%20status%20not%20in%20(done%2C%20abandoned)%20and%20component%20%3D%20htcondor-ce%20and%20issuetype%20%3D%20bug)

Updating to HTCondor-CE 23
--------------------------

!!! note "Updating from HTCondor-CE < 6"
    If updating to HTCondor-CE 23 from HTCondor-CE < 6, be sure to also consult the HTCondor-CE 6
    [upgrade instructions](../v6/releases.md#600).

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

### **October 30, 2024:** 23.10.1 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v23.10.1) includes the following new features:

-   Fix certificate subject parsing in `condor_ce_host_network_check`

### **October 30, 2024:** 23.0.17 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v23.0.17) includes the following new features:

-   Remove obsolete GSI configuration

### **August 8, 2024:** 23.9.1 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v23.9.1) includes the following new features:

-   Use new Job Router syntax by default
-   Update configuration files to work with HTCondor 23.9.1 and later
-   Use `BatchQueue` job attribute in CE routes

### **July 24, 2024:** 23.0.13 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v23.0.13) includes the following new features:

-   Package `condor_ce_upgrade_check`

### **July 16, 2024:** 23.0.12 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v23.0.12) includes the following new features:

-   Fix whole node GPU request expression for non-HTCondor batch systems

### **April 11, 2024:** 23.0.8 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v23.0.8) includes the following new features:

-   Fix memory request being ignored for whole node jobs

### **March 14, 2024:** 23.0.6 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v23.0.6) includes the following new features:

-   Fix CE job route transform for job environment
-   Fix `CERequirements` when the `default_CERequirements` is not set
-   Add `condor_ce_test_token` tool to generate short lived SciToken for tests
-   Remove GSI from security method list to eliminate annoying warnings

### **January 4, 2024:** 23.0.3 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v23.0.3) includes the following new features:

-   Ensure that jobs requesting GPUs land on HTCondor EPs with GPUs

### **November 16, 2023:** 23.0.1 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v23.0.1) includes the following new features:

-   Add `condor_ce_test_token` command

### **September 21, 2023:** 23.0.0 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v23.0.0) includes the following new features:

-   Add grid CA and host certificate/key locations to default SSL search paths
-   Verifies that HTCondor-CE can access the local HTCondor's `SPOOL` directory
-   Can use `condor_ce_trace` without SciToken to test batch system integration
-   `condor_ce_upgrade_check` checks compatibility with HTCondor 23.0
-   Adds deprecation warnings for old job router configuration syntax

Getting Help
------------

If you have any questions about the release process or run into issues with an upgrade, please
[contact us](../index.md#contact-us) for assistance.
