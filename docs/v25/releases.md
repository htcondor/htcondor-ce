Releases
========

HTCondor-CE 25 is distributed via RPM and are available from the following Yum repositories:

- [HTCondor LTS and Feature Releases](https://htcondor.org/htcondor/download/)
- [The OSG Consortium](https://osg-htc.org/docs/common/yum/)


Known Issues
------------

Known bugs affecting HTCondor-CEs can be found in
[Jira](https://opensciencegrid.atlassian.net/issues/?jql=project%20%3D%20HTCONDOR%20AND%20status%20not%20in%20(done%2C%20abandoned)%20and%20component%20%3D%20htcondor-ce%20and%20issuetype%20%3D%20bug)

Updating to HTCondor-CE 25
--------------------------

!!! note "Updating from HTCondor-CE < 24"
    If updating to HTCondor-CE 25 from HTCondor-CE < 24, be sure to also consult the HTCondor-CE 24
    [upgrade instructions](../v24/releases.md).

!!! tip "Finding relevant configuration changes"
    When updating HTCondor-CE RPMs, `.rpmnew` and `.rpmsave` files may be created containing new defaults that you
    should merge or new defaults that have replaced your customization, respectively.
    To find these files for HTCondor-CE, run the following command:

        :::console
        root@host # find /etc/condor-ce/ -name '*.rpmnew' -name '*.rpmsave'

HTCondor-CE 25 no longer accepts the original job router syntax.
If you have custom job routes, you must use the new, more flexible,
[ClassAd transform](../configuration/job-router-overview/#classad-transforms)
job router syntax.

If you have added custom job routes, make sure that you
[convert](../configuration/job-router-overview/#converting-to-classad-transforms)
any jobs routes to the new, more flexible,
[ClassAd transform](../configuration/job-router-overview/#classad-transforms)
syntax.

HTCondor-CE 25 Version History
------------------------------

This section contains release notes for each version of HTCondor-CE 25.
Full HTCondor-CE version history can be found on [GitHub](https://github.com/htcondor/htcondor-ce/releases).

### **September 29, 2025:** 25.0.1 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v25.0.1) includes the following new features:

-   Initial HTCondor-CE 25.0.1 release

Getting Help
------------

If you have any questions about the release process or run into issues with an upgrade, please
[contact us](../index.md#contact-us) for assistance.
