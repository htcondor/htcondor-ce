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
   ApelSpec = [HEPSPEC=14.37; SI2K=2793]
   STARTD_ATTRS = $(STARTD_ATTRS) ApelSpec
   # ... define a performance factor compared to the average
   ApelScaling = 1.414  # this machine is above average
   STARTD_ATTRS = $(STARTD_ATTRS) ApelScaling
   ```

4. Start and enable the `condor-ce-apel.timer` on each HTCondor-CE

References
----------

- [Initial HTCondor-CE APEL interface scripts](https://twiki.cern.ch/twiki/bin/view/LCG/HtCondorCeAccounting)
