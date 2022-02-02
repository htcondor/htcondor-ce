#!/bin/bash

# HTCondor insists on a domain name
sed /etc/hosts -e "s/`hostname`/`hostname`.htcondor.org `hostname`/" > /etc/hosts.new
/bin/cp -f /etc/hosts.new /etc/hosts
