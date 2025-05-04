HTCondor-CE APEL Scripts
=========================

This folder contains [APEL](https://github.com/apel/apel) accounting record generation scripts, services and configuration for HTCondor-CE with an HTCondor batch system.
The scripts work by parsing per-job history files to blah and batch record files.
Since APEL is not used in the OSG, the `htcondor-ce-apel` package is excluded from OSG builds.

Usage
-----

To create and publish APEL records, use the following instructions

1. Install HTCondor-CE APEL on each HTCondor-CE

        yum install htcondor-ce-apel

2. Configure the APEL parser and client on each HTCondor-CE

    * In `client.cfg` set `[spec_updated] site_name` and at least
      `[spec_updated] manual_spec1`.
    * In `parser.cfg` define where and how to parse the records
      ```ini
      [blah]
      enabled = true
      dir = /var/lib/condor-ce/apel/
      filename_prefix = blah
      [batch]
      enabled = true
      dir = /var/lib/condor-ce/apel/
      filename_prefix = batch
      type = HTCondor
      ```

3. Optionally define the absolute or relative performance of any StartD
   ```
   # In the StartD condor config:
   # define an absolute performance for specific benchmarks, or ...
   ApelSpecs = [HEPSPEC=14.37; SI2K=2793]
   STARTD_ATTRS = $(STARTD_ATTRS) ApelSpecs
   # ... define a performance factor compared to the average
   ApelScaling = 1.414  # this machine is above average
   STARTD_ATTRS = $(STARTD_ATTRS) ApelScaling
   ```

4. Optionally define mapping for APEL accounting groups for jobs without VOMS proxy
  ```
  # in the /etc/condor/apel_acct_group.map map Owner or token issuer & subject, e.g.
  # map local job owner "dteam" to APEL accounting group /dteam
  * dteam /dteam
  # map all local owners starting with "ops" to the APEL accounting group /ops
  * /^ops.*$/ /ops
  # map ATLAS token issuer and subject to the APEL accounting group
  * /^https\:\/\/atlas\-auth\.cern\.ch\/,7dee38a3\-6ab8\-4fe2\-9e4c\-58039c21d817$/ /atlas/Role=production/Capability=NULL
  * /^https\:\/\/atlas\-auth\.cern\.ch\/,5c5d2a4d\-9177\-3efa\-912f\-1b4e5c9fb660$/ /atlas/Role=lcgadmin/Capability=NULL
  * /^https\:\/\/atlas\-auth\.cern\.ch\/,750e9609\-485a\-4ed4\-bf16\-d5cc46c71024$/ /atlas/Role=pilot/Capability=NULL
  * /^https\:\/\/atlas\-auth\.cern\.ch\/,.*$/ /atlas/Role=NULL/Capability=NULL
  # map DUNE token issuer and subject to the APEL accounting group
  * /^https\:\/\/cilogon\.org\/dune,dunepilot\@fnal\.gov$/ /dune/Role=pilot/Capability=NULL
  * /^https\:\/\/cilogon\.org\/dune,.*$/ /dune/Role=NULL/Capability=NULL
  # no way to map individual Fermilab experiments hidden behind one token identity
  #* /^https\:\/\/cilogon\.org\/fermilab,fermilabpilot\@fnal\.gov$/ NoVA? Minerva? Mu2e? ...
  ```

5. Start and enable the `condor-ce-apel.timer` on each HTCondor-CE

The default behaviour when a StartD does not properly report performance information
changed in HTCondor-CE v 5.1.6 to assume average performance in this case.
To restore the previous behaviour of quarantining the metadata of affected jobs,
set `APEL_SCALE_DEFAULT = undefined` in the HTCondor-CE configuration.

References
----------

- [Initial HTCondor-CE APEL interface scripts](https://twiki.cern.ch/twiki/bin/view/LCG/HtCondorCeAccounting)
