condor-ce
=========

A site grid gatekeeper technology based solely on Condor components.

This package is simply a thin set of wrappers around Condor, allowing you to
run a Condor-CE without disrupting a site Condor install.

For example, "condor_ce_q" is the Condor-CE equivalent to "condor_q" for the
Condor-CE processes.  This package took much of its inspiration - and base 
code - from OSGs condor-cron package.

Sites are encouraged to install the sub-package "condor-ce-condor" or
"condor-ce-pbs", depending on which batch manager they run.

