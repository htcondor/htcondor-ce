Releases
========

HTCondor-CE is distributed via RPM and is available from the following Yum repositories:

- [HTCondor](https://research.cs.wisc.edu/htcondor/yum/)
- [Open Science Grid](https://opensciencegrid.org/docs/common/yum/)

Versions
--------

HTCondor-CE version history can be found on [GitHub](https://github.com/htcondor/htcondor-ce/releases).

### Updating to HTCondor-CE 4 ###

HTCondor-CE 4 is a major release that adds many features and overhauls the default configuration.
As such, upgrades from older versions of HTCondor-CE may require manual intervention:

- **Disabled job retries by default** since most jobs submitted through HTCondor-CEs are actually resource requests
  (i.e. pilot jobs) instead of jobs containing user payloads.
  Therefore, it's preferred to prevent these jobs from retrying and instead wait for additional resource requests to be
  submitted.
  To re-enable job retries, set the following in your configuration:

        ENABLE_JOB_RETRIES = True

- **Simplified remote CE requirements format:**
  [Remote CE requirements](https://opensciencegrid.org/docs/compute-element/job-router-recipes/#setting-batch-system-directives)
  are a way to specify batch system directives that aren't directly supported in the job router for non-HTCondor batch systems.
  In the past, specifying these directives were often quite complicated. For example, a snippet from an example job
  route:

        set_default_remote_cerequirements = strcat("Walltime == 3600 && AccountingGroup =="", x509UserProxyFirstFQAN, "\"");

    The HTCondor 8.8 series allows users to specify the same logic using a simplified format within job routes.
    The same expression above can be written as the following snippet:

        set_WallTime = 3600;
        set_AccountingGroup = x509UserProxyFirstFQAN;
        set_default_CERequirements = "Walltime,AccountingGroup";

- **Reorganize HTCondor-CE configuration:** configuration that admins are expected to change is in
  `/etc/condor-ce/config.d/`, other configuration is in `/usr`.
  Watch out for `*.rpmnew` files and merge changes into your existing configuration, especially
  `/etc/condor-ce/condor_mapfile.rpmnew`.

- **OSG domain changes:** OSG builds of HTCondor-CE now use the standard `htcondor.org` domain for mapped principles.
  For example, `UID_DOMAIN` is now `users.htcondor.org` instead of `users.opensciencegrid.org`.
  If you've made changes to the default HTCondor-CE security configuration (check with `condor_ce_config_val -dump`),
  you may need to update any configuration to use `*.htcondor.org` instead of `*.opensciencegrid.org`.

Getting Help
------------

If you have any questions about the release process or run into issues with an upgrade, please
[contact us](/#contact-us) for assistance.
