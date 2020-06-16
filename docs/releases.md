Releases
========

HTCondor-CE 4 is distributed via RPM and is available from the following Yum repositories:

- [HTCondor development](https://research.cs.wisc.edu/htcondor/yum/)
- [Open Science Grid](https://opensciencegrid.org/docs/common/yum/)

Updating to HTCondor-CE 4
-------------------------

HTCondor-CE 4 is a major release that adds many features and overhauls the default configuration.
As such, upgrades from older versions of HTCondor-CE may require manual intervention:

- **Disabled job retries by default** since most jobs submitted through HTCondor-CEs are actually resource requests
  (i.e. pilot jobs) instead of jobs containing user payloads.
  Therefore, it's preferred to prevent these jobs from retrying and instead wait for additional resource requests to be
  submitted.
  To re-enable job retries, set the following in your configuration:

        ENABLE_JOB_RETRIES = True

- **Simplified remote CE requirements format:**
  [remote CE requirements](/batch-system-integration#setting-batch-system-directives) are a way to specify batch system
  directives that aren't directly supported in the job router for non-HTCondor batch systems.
  In the past, specifying these directives were often quite complicated. For example, a snippet from an example job
  route:

        set_default_remote_cerequirements = strcat("Walltime == 3600 && AccountingGroup =="", x509UserProxyFirstFQAN, "\"");

    The HTCondor 8.8 series allows users to specify the same logic using a simplified format within job routes.
    The same expression above can be written as the following snippet:

        set_WallTime = 3600;
        set_AccountingGroup = x509UserProxyFirstFQAN;
        set_default_CERequirements = "Walltime,AccountingGroup";

- **Reorganized HTCondor-CE configuration:** configuration that admins are expected to change is in
  `/etc/condor-ce/config.d/`, other configuration is in `/usr`.
  Watch out for `*.rpmnew` files and merge changes into your existing configuration, especially
  `/etc/condor-ce/condor_mapfile.rpmnew`.

- **OSG domain changes:** OSG builds of HTCondor-CE now use the standard `htcondor.org` domain for mapped principles.
  For example, `UID_DOMAIN` is now `users.htcondor.org` instead of `users.opensciencegrid.org`.
  If you've made changes to the default HTCondor-CE security configuration (check with `condor_ce_config_val -dump`),
  you may need to update any configuration to use `*.htcondor.org` instead of `*.opensciencegrid.org`.

HTCondor-CE 4 Version History
-----------------------------

This section contains release notes for each version of HTCondor-CE 4.
Full HTCondor-CE version history can be found on [GitHub](https://github.com/htcondor/htcondor-ce/releases).

### 4.4.0 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v4.4.0) includes the following new features:

- Add plug-in interface to HTCondor-CE View and separate out OSG-specific code and configuration
- Add configuration option (COMPLETED_JOB_EXPIRATION) for how many days completed jobs may stay in the queue

This release also includes the following bug-fixes:

- Replace APEL uploader SchedD cron with init and systemd services
- Fix HTCondor-CE View SchedD query that caused "Info" tables to be blank

### 4.3.0 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v4.3.0) includes the following new features:

- Add the CE registry web application to the Central Collector.
  The registry provides an interface to OSG site administrators of HTCondor-CEs to retrieve an HTCondor IDTOKEN for
  authenticating pilot job submissions.
- Identify broken job routes upon startup
- Add benchmarking parameters to the BDII provider via `HTCONDORCE_SPEC` in the configuration.
  See `/etc/condor-ce/config.d/99-ce-bdii.conf`

This release also includes the following bug-fixes:

- Fix handling of unmapped GSI users in the Central Collector
- Fix reference to old BDII configuration values

### 4.2.1 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v4.2.1) includes the following bug fixes:

- Drop vestigial Central Collector configuration generator script and service
- Fix unmapped GSI/SSL regular expressions and allow unmapped entities to advertise to the Central Collector

### 4.2.0 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v4.2.0) includes the following new features:

- Add SSL support for reporting to Central Collectors
- GLUE2 validation improvements for the BDII provider

### 4.1.0 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v4.1.0) includes the following new features:

- **Added the ability to configure the environment of routed jobs:** Administrators may now add or override environment
  variables for resultant batch system jobs.
- **Simplified APEL configuration**: HTCondor-CE provides appropriate default configuration for its APEL scripts so
  administrators only need to configure their HTCondor worker nodes as well as the APEL parser, client, and SSM.
  Details can be found in the [documentation](/installation/htcondor-ce#uploading-accounting-records-to-apel).

This release also includes the following bug-fixes:

- Fixed the ability to specify grid certificate locations for SSL authentication
- Refined the APEL record filter to ignore jobs that have not yet started
- Fixed an issue where `condor_ce_q` required authentication
- Re-enabled the ability for local users to submit jobs to the CE queue
- Fixed an issue where some jobs were capped at 72 minutes instead of 72 hours
- Improved BDII provider error handling

### 4.0.1 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v4.0.1) fixes a stacktrace that can occur on
`condor-ce` service startup when the required `QUEUE_SUPER_USER_MAY_IMPERSONATE = .*` configuration is not set for
HTCondor batch systems ([#245](https://github.com/htcondor/htcondor-ce/issues/245)).

### 4.0.0 ###

[This release]((https://github.com/htcondor/htcondor-ce/releases/tag/v4.0.0)) includes the following new features:

- **SciTokens support** if using an HTCondor version that supports SciTokens (e.g. the OSG-distributed HTCondor 8.9.2).
- **Disabled job retries by default** since most jobs submitted through HTCondor-CEs are actually resource requests
  (i.e. pilot jobs) instead of jobs containing user payloads.
  Therefore, it's preferred to prevent these jobs from retrying and instead wait for additional resource requests to be
  submitted.
  To re-enable job retries, set the following in your configuration:

        ENABLE_JOB_RETRIES = True

- **Simplified daemon authentication:** HTCondor-CE now uses
  [FS authentication](https://htcondor.readthedocs.io/en/stable/admin-manual/security.html#file-system-authentication)
  between its own daemons instead of GSI.
- **Simplified remote CE requirements format:**
  [Remote CE requirements](/batch-system-integration#setting-batch-system-directives)
  are a way to specify batch system directives that aren't directly supported in the job router for non-HTCondor batch systems.
  In the past, specifying these directives were often quite complicated. For example, a snippet from an example job route:

        set_default_remote_cerequirements = strcat("Walltime == 3600 && AccountingGroup =="", x509UserProxyFirstFQAN, "\"");

    The HTCondor 8.8 series allows users to specify the same logic using a simplified format within job routes.
    The same expression above can be written as the following snippet:

        set_WallTime = 3600;
        set_AccountingGroup = x509UserProxyFirstFQAN;
        set_default_CERequirements = "Walltime,AccountingGroup";

- **Reorganized HTCondor-CE configuration:** configuration that admins are expected to change is in
  `/etc/condor-ce/config.d/`, other configuration is in `/usr`.
  Watch out for `*.rpmnew` files, particularly for `/etc/condor-ce/condor_mapfile.rpmnew` and
  `/etc/condor-ce/config.d/*.conf.rpmnew`, and merge changes into your existing configuration.
- **OSG domain changes:** OSG builds of HTCondor-CE now use the standard `htcondor.org` domain for mapped principles.
  For example, `UID_DOMAIN` is now `users.htcondor.org` instead of `users.opensciencegrid.org`.
  If you've made changes to the default HTCondor-CE configuration, you may need to update any configuration to use
  `*.htcondor.org`.
- **Moved most OSG-specific configuration** into the OSG CE metapackage
  ([SOFTWARE-3813](https://jira.opensciencegrid.org/browse/SOFTWARE-3813))
- **Increased the default maximum walltime** to 72 hours

Getting Help
------------

If you have any questions about the release process or run into issues with an upgrade, please
[contact us](/#contact-us) for assistance.
