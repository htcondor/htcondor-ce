Releases
========

HTCondor-CE 3 is distributed via RPM and is available from the following Yum repositories:

- [HTCondor stable](https://research.cs.wisc.edu/htcondor/yum/)
- [Open Science Grid](https://opensciencegrid.org/docs/common/yum/)

HTCondor-CE 3 Version History
-----------------------------

This section contains release notes for each version of HTCondor-CE 3.
HTCondor-CE version history can be found on [GitHub](https://github.com/htcondor/htcondor-ce/releases).

### 3.4.0 ###

[This release](https://github.com/htcondor/htcondor-ce/releases/tag/v3.4.0) includes the following new features:

- **Add the ability to configure the environment of routed jobs:** Administrators may now add or override environment
  variables for resultant batch system jobs.
- **Simplified APEL configuration**: HTCondor-CE provides appropriate default configuration for its APEL scripts so
  administrators only need to configure their HTCondor worker nodes as well as the APEL parser, client, and SSM.
  Details can be found in the [documentation](/installation/htcondor-ce#uploading-accounting-records-to-apel).

This release also includes the following bug-fixes:

- Refined the APEL record filter to ignore jobs that have not yet started
- Improved BDII provider error handling

### 3.3.0 ###

- Add APEL support for HTCondor-CE and HTCondor backends
- Store malformed ads reporting to htcondor-ce-collector

### 3.2.2 ###

- Make blahp requirement binary package specific ([SOFTWARE-3623](https://jira.opensciencegrid.org/browse/SOFTWARE-3623))
- Added `condor_ce_store_cred` for PASSWORD authentication
- Use new multi-line syntax configuration syntax ([SOFTWARE-3637](https://jira.opensciencegrid.org/browse/SOFTWARE-3637))
- Update MyOSG URL and queries

### 3.2.1 ###

- Explicitly set ALLOW_READ to support HTCondor 8.9 ([SOFTWARE-3538](https://jira.opensciencegrid.org/browse/SOFTWARE-3538))
- Add timeouts to the BDII provider

### 3.2.0 ###

- Map certs with VOMS attr before local daemons ([SOFTWARE-3489](https://jira.opensciencegrid.org/browse/SOFTWARE-3489))
- Send CEView keepalives as the condor user ([SOFTWARE-3486](https://jira.opensciencegrid.org/browse/SOFTWARE-3486))

### 3.1.4 ###

- Fix condor_ce_trace failures caused by transferring /usr/bin/env ([SOFTWARE-3387](https://jira.opensciencegrid.org/browse/SOFTWARE-3387))
- Fix regex for RDIG certs (SOFTWARE-3399)
- Don't require authz check for `condor_ce_q` ([SOFTWARE-3414](https://jira.opensciencegrid.org/browse/SOFTWARE-3414))

### 3.1.3 ###

Fix condor_ce_info_status using the wrong port for the central collector
([SOFTWARE-3381](https://jira.opensciencegrid.org/browse/SOFTWARE-3381))

### 3.1.2-3 ###

Ensure that all BDII files exist for the condor repository

### 3.1.2-2 ###

This version enables building of the BDII sub-package for the condor repository

### 3.1.2 ###

- Require `voms-clients-cpp` explicitly ([SOFTWARE-3201](https://jira.opensciencegrid.org/browse/SOFTWARE-3201))
- Add daemon mapping for Let's Encrypt certificates ([SOFTWARE-3236](https://jira.opensciencegrid.org/browse/SOFTWARE-3236))

### 3.1.1 ###

- Allow InCommon host certs
- Drop vestigal HTCondor-related configuration
- Add documentation for mapping multiple VOMS attributes

### 3.1.0 ###

- Removed OSG-specific code and configuration from builds intended for the HTCondor repo
- Updated the CERN BDII provider
- Removed packaging necessary for EL5 builds

### 3.0.4 ###

Handle missing `MyType` attribute in condor 8.7.5

### 3.0.3 ###

- Fix `condor_ce_ping` with IPv6 addresses ([SOFTWARE-3030](https://jira.opensciencegrid.org/browse/SOFTWARE-3030))
- Fix for CEView being killed after 24h ([SOFTWARE-2820](https://jira.opensciencegrid.org/browse/SOFTWARE-3030))
- Import the `web_utils` library for `condor_ce_metric`

### 3.0.2 ###

- Fix traceback if `JOB_ROUTER_ENTRIES` not present ([SOFTWARE-2814](https://jira.opensciencegrid.org/browse/SOFTWARE-2814))
- Improve POSIX compatability

### 3.0.1 ###

Fix bug that resulted in losing track of some payload jobs in the Collector audit plugin

### 3.0.0 ###

HTCondor-CE 3.0.0 adds user job auditing using HTCondor's collector plugin feature, which requires HTCondor 8.6.5.

- Add the audit_payloads function.  This logs the starting and stopping of
  all payloads that were started from pilot systems based on condor.
- Do not hold jobs with expired proxy ([SOFTWARE-2803](https://jira.opensciencegrid.org/browse/SOFTWARE-2803))
- Only warn about configuration if osg-configure is present ([SOFTWARE-2805](https://jira.opensciencegrid.org/browse/SOFTWARE-2805))
- CEView VO tab throws 500 error on inital installation ([SOFTWARE-2826](https://jira.opensciencegrid.org/browse/SOFTWARE-2826))

Getting Help
------------

If you have any questions about the release process or run into issues with an upgrade, please
[contact us](/#contact-us) for assistance.
