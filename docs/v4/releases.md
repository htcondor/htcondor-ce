Releases
========

HTCondor-CE 4 are distributed via RPM and are available from the following Yum repositories:

- [HTCondor development](https://research.cs.wisc.edu/htcondor/yum/)
- [Open Science Grid](https://opensciencegrid.org/docs/common/yum/)


!!! tip "Installing older versions"
    To install an older version of HTCondor-CE available in the above Yum repositories,
    first find all of the available versions:

        :::console
        # yum search --show-duplicates htcondor-ce

    Then pick an version and install it with the following command:

        :::console
        # yum install htcondor-ce-4.3.0


HTCondor-CE 4 Version History
-----------------------------

This section contains release notes for each version of HTCondor-CE 4.
Full HTCondor-CE version history can be found on [GitHub](https://github.com/htcondor/htcondor-ce/releases).

### 4.5.1 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v4.5.1) includes the following changes:

-   Fix an issue with an overly aggressive default `SYSTEM_PERIODIC_REMOVE`
    ([HTCONDOR-350](https://opensciencegrid.atlassian.net/browse/HTCONDOR-350))
-   Use the `GlobalJobID` attribute as the APEL record `lrmsID` (#426)

### 4.5.0 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v4.5.0) includes the following new features:

-   Whole node jobs (HTCondor batch systems only) now make use of GPUs
    ([HTCONDOR-103](https://opensciencegrid.atlassian.net/browse/HTCONDOR-103))
-   Added `USE_CE_HOME_DIR` configuration variable (default: `True`) to allow users to disable setting `$HOME` in the
    routed job's environment based on the HTCondor-CE user's home directory
-   HTCondor-CE Central Collectors now prefer GSI over SSL authentication
    ([HTCONDOR-237](https://opensciencegrid.atlassian.net/browse/HTCONDOR-237))
-   HTCondor-CE registry now validates the value of submitted client codes
    ([HTCONDOR-241](https://opensciencegrid.atlassian.net/browse/HTCONDOR-241))
-   Automatically remove CE jobs that exceed their `maxWalltime` (if defined) or the configuration value of
    `ROUTED_JOB_MAX_TIME` (default: 4320 sec/72 hrs)

This release also includes the following bug-fixes:

-   Fixed a circular configuration definition in the HTCondor-CE View that resulted in 100% CPU usage by the
    `condor_gangliad` daemon ([HTCONDOR-161](https://opensciencegrid.atlassian.net/browse/HTCONDOR-161))

### 4.4.1 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v4.4.1) includes the following bug-fixes:

- Fixed a stacktrace with the BDII provider when `HTCONDORCE_SPEC` isn't defined in the local HTCondor configuration
- Fixed a race condition that could result in removed jobs being put on hold
- Improved performance of the HTCondor-CE View

### 4.4.0 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v4.4.0) includes the following new features:

- Add plug-in interface to HTCondor-CE View and separate out OSG-specific code and configuration
- Add configuration option (`COMPLETED_JOB_EXPIRATION`) for how many days completed jobs may stay in the queue

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
  Details can be found in the [documentation](installation/htcondor-ce.md#uploading-accounting-records-to-apel).

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

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v4.0.0) includes the following new features:

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
  [Remote CE requirements](batch-system-integration.md#setting-batch-system-directives)
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
[contact us](index.md#contact-us) for assistance.
