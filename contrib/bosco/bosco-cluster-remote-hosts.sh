#!/bin/bash

# Source condor-ce environment
[ -f /usr/share/condor-ce/condor_ce_env_bootstrap ] &&
   . /usr/share/condor-ce/condor_ce_env_bootstrap

export OVERRIDE_DIR=/etc/condor-ce/bosco_override
/usr/share/condor-ce/bosco-cluster-remote-hosts.py

