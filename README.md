HTCondor-CE
===========

[![Build Status](https://travis-ci.org/opensciencegrid/htcondor-ce.svg?branch=master)](https://travis-ci.org/opensciencegrid/htcondor-ce)

---

A site grid gatekeeper technology based solely on HTCondor components.

This package is simply a thin set of wrappers around HTCondor, allowing you to
run a HTCondor-CE without disrupting a site HTCondor install.

For example, `condor_ce_q` is the HTCondor-CE equivalent to `condor_q` for the
HTCondor-CE processes.  This package took much of its inspiration - and base 
code - from OSGs condor-cron package.

Sites are encouraged to install the sub-package `htcondor-ce-condor` or
`htcondor-ce-pbs`, depending on which batch manager they run.

## Branches ##

The `master` branch contains the version for the most recent OSG
release. Previous major versions can be found in `vN` branches, where `N` is
the HTCondor-CE major version.

As of 7/11/17:

`master`: HTCondor-CE 3.x for OSG 3.4 (condor-8.6.x, condor-8.7.x)    
`v2`: HTCondor-CE 2.x for OSG 3.3 (condor-8.4.x)

