HTCondor-CE
===========

A site grid gatekeeper technology based solely on HTCondor components.

This package is simply a thin set of wrappers around Condor, allowing you to
run a Condor-CE without disrupting a site Condor install.

For example, `condor_ce_q` is the HTCondor-CE equivalent to `condor_q` for the
HTCondor-CE processes.  This package took much of its inspiration - and base 
code - from OSGs condor-cron package.

Sites are encouraged to install the sub-package `htcondor-ce-condor` or
`htcondor-ce-pbs`, depending on which batch manager they run.

