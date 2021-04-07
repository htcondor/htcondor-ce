Troubleshooting Remote HTCondor-CEs
===================================

Since HTCondor-CE is built on top of HTCondor, it's possible to perform quite a bit of troubleshooting from a remote
client with access to the HTCondor command-line tools.
For testing end-to-end resource request submission or remote interactive-like access, a grid operator will need access
to a host with the `htcondor-ce-client` installed.
This document outlines the steps that a grid operator can perform in order to troubleshoot a remote HTCondor-CE.

Verifying Network Connectivity
------------------------------

Before performing any troubleshooting of the remote HTCondor-CE service, it's important to verify that the HTCondor-CE
can be contacted on its HTCondor-CE port (default: `9619`) at the specified fully qualified domain name (FQDN).

### Verifying DNS ###

!!! tip "Reverse DNS and GSI authentication"
    GSI authentication requires that the HTCondor-CE host has a reverse DNS record but that record is not required to
    match the forward DNS record! For example, if you have an `A` record `htcondor-ce.chtc.wisc.edu -> 123.4.5.678`, a
    `PTR` of `123.4.5.678 -> chtc.wisc.edu` would satisfy the GSI authentication requirement.

As noted in the [HTCondor-CE installation document](../installation/htcondor-ce.md), an HTCondor-CE must have forward
and reverse DNS records.
To verify DNS, use a tool like `nslookup`:

```console
$ nslookup htcondor-ce.chtc.wisc.edu
Server:		144.92.254.254
Address:	144.92.254.254#53

Non-authoritative answer:
Name:	htcondor-ce.chtc.wisc.edu
Address: 128.104.100.65
Name:	htcondor-ce.chtc.wisc.edu
Address: 2607:f388:107c:501:216:3eff:fe89:aa3

$ nslookup 128.104.100.65
65.100.104.128.in-addr.arpa	name = htcondor-ce.chtc.wisc.edu.

Authoritative answers can be found from:
104.128.in-addr.arpa	nameserver = dns2.itd.umich.edu.
104.128.in-addr.arpa	nameserver = adns1.doit.wisc.edu.
104.128.in-addr.arpa	nameserver = adns3.doit.wisc.edu.
104.128.in-addr.arpa	nameserver = adns2.doit.wisc.edu.
adns2.doit.wisc.edu	internet address = 144.92.20.99
dns2.itd.umich.edu	internet address = 192.12.80.222
adns3.doit.wisc.edu	internet address = 144.92.104.21
adns1.doit.wisc.edu	internet address = 144.92.9.21
adns2.doit.wisc.edu	has AAAA address 2607:f388:d:2::1006
adns2.doit.wisc.edu	has AAAA address 2607:f388::a53:2
adns3.doit.wisc.edu	has AAAA address 2607:f388:2:2001::100b
adns3.doit.wisc.edu	has AAAA address 2607:f388::a53:3
adns1.doit.wisc.edu	has AAAA address 2607:f388:2:2001::100a
adns1.doit.wisc.edu	has AAAA address 2607:f388::a53:1
```

If not, the HTCondor-CE administrator will have to register the appropriate DNS records.

### Verifying service connectivity ###

After verifying DNS, check to see if the remote HTCondor-CE is listening on the appropriate port:

```console
$ telnet htcondor-ce.chtc.wisc.edu 9619
Trying 128.104.100.65...
Connected to htcondor-ce.chtc.wisc.edu.
Escape character is '^]'.
```

If not, the HTCondor-CE administrator will have to ensure that the service is running and/or open up their firewall.

Verifying Configuration
-----------------------

Once you've verified network connectivity, you can start verifying the HTCondor-CE daemons.

### Inspecting daemons ###

To inspect the running daemons of a remote HTCondor-CE,
use [condor_status](https://htcondor.readthedocs.io/en/latest/man-pages/condor_status.html):

```console
$ condor_status -any -pool htcondor-ce.chtc.wisc.edu:9619
MyType             TargetType         Name

Collector          None               My Pool - htcondor-ce.chtc.wisc.edu@htcondor-ce.c
Job_Router         None               htcondor-ce@htcondor-ce.chtc.wisc.edu
Scheduler          None               htcondor-ce.chtc.wisc.edu
DaemonMaster       None               htcondor-ce.chtc.wisc.edu
Submitter          None               nu_lhcb@users.htcondor.org
```

If you don't see the appropriate daemons, ask the administrator to following
[these troubleshooting steps](troubleshooting.md#daemons-fail-to-start).

!!! note "Submitter ad"
    When querying daemons for an HTCondor-CE, you may see `Submitter` ads for each user with jobs in the queue.
    These ads are used to collect per-user stats that are available to the HTCondor-CE administrator.

You can inspect the details of a specific daemon with per-daemon and `-long` options:

```console
$ condor_status -pool htcondor-ce.chtc.wisc.edu:9619 -collector -long
ActiveQueryWorkers = 0
ActiveQueryWorkersPeak = 1
AddressV1 = "{[ p=\"primary\"; a=\"128.104.100.65\"; port=9619; n=\"Internet\"; alias=\"htcondor-ce.chtc.wisc.edu\"; spid=\"collector\"; noUDP=true; ], [ p=\"IPv4\"; a=\"128.104.100.65\"; port=9619; n=\"Internet\"; alias=\"htcondor-ce.chtc.wisc.edu\"; spid=\"collector\"; noUDP=true; ], [ p=\"IPv6\"; a=\"2607:f388:107c:501:216:3eff:fe89:aa3\"; port=9619; n=\"Internet\"; alias=\"htcondor-ce.chtc.wisc.edu\"; spid=\"collector\"; noUDP=true; ]}"
CollectorIpAddr = "<128.104.100.65:9619?addrs=128.104.100.65-9619+[2607-f388-107c-501-216-3eff-fe89-aa3]-9619&alias=htcondor-ce.chtc.wisc.edu&noUDP&sock=collector>"
CondorAdmin = "root@htcondor-ce.chtc.wisc.edu"
CondorPlatform = "$CondorPlatform: x86_64_CentOS7 $"
CondorVersion = "$CondorVersion: 8.9.8 Jun 29 2020 BuildID: 508520 PackageID: 8.9.8-0.508520 $"
CurrentJobsRunningAll = 0
CurrentJobsRunningGrid = 0
CurrentJobsRunningJava = 0
```

### Inspecting resource requests ###

To inspect resource requests submitted to a remote HTCondor-CE,
use [condor_q](https://htcondor.readthedocs.io/en/latest/man-pages/condor_q.html):

```console
$ condor_q -all -name htcondor-ce.chtc.wisc.edu -pool htcondor-ce.chtc.wisc.edu:9619

-- Schedd: htcondor-ce.chtc.wisc.edu : <128.104.100.65:9619?... @ 10/29/20 15:31:45
OWNER   BATCH_NAME    SUBMITTED   DONE   RUN    IDLE   HOLD  TOTAL JOB_IDS
nu_lhcb ID: 24631   10/18 12:06     33      _      _      _     35 24631.5-15
nu_lhcb ID: 24632   10/18 12:23      7      _      _      _      9 24632.2-4
nu_lhcb ID: 24635   10/18 14:23      3      _      _      _      5 24635.0-1
nu_lhcb ID: 24636   10/18 14:40      5      _      _      _      9 24636.0-6
nu_lhcb ID: 24637   10/18 14:58      7      _      _      _      8 24637.2
nu_lhcb ID: 24638   10/18 15:15      7      _      _      _      8 24638.1
```

You can inspect the details of a specific resource request with the `-long` option:

```console
$ condor_q -all -name htcondor-ce.chtc.wisc.edu -pool htcondor-ce.chtc.wisc.edu:9619 -long 24631.5
Arguments = ""
BufferBlockSize = 32768
BufferSize = 524288
BytesRecvd = 58669.0
BytesSent = 184201.0
ClusterId = 24631
Cmd = "DIRAC_Ullq7V_pilotwrapper.py"
CommittedSlotTime = 0
CommittedSuspensionTime = 0
CommittedTime = 0
```

### Retrieving HTCondor-CE configuration ###

To verify a remote HTCondor-CE configuration,
use [condor_config_val](https://htcondor.readthedocs.io/en/latest/man-pages/condor_config_val.html):

```console
$ condor_config_val -name htcondor-ce.chtc.wisc.edu -pool htcondor-ce.chtc.wisc.edu:9619 -dump
# Configuration from master on htcondor-ce.chtc.wisc.edu <128.104.100.65:9619?addrs=128.104.100.65-9619+[2607-f388-107c-501-216-3eff-fe89-aa3]-9619&alias=htcondor-ce.chtc.wisc.edu&noUDP&sock=master_1744571_b0a0>
ABORT_ON_EXCEPTION = false
ACCOUNTANT_HOST = 
ACCOUNTANT_LOCAL_DOMAIN = 
ActivationTimer = ifThenElse(JobStart =!= UNDEFINED, (time() - JobStart), 0)
ActivityTimer = (time() - EnteredCurrentActivity)
ADD_WINDOWS_FIREWALL_EXCEPTION = $(CondorIsAdmin)
ADVERTISE_IPV4_FIRST = $(PREFER_IPV4)
ALL_DEBUG = D:CAT D_ALWAYS:2
ALLOW_ADMIN_COMMANDS = true
```

If you know the name of the configuration variable, you can query for it directly:

```console
$ condor_config_val -name htcondor-ce.chtc.wisc.edu -pool htcondor-ce.chtc.wisc.edu:9619 -verbose JOB_ROUTER_SCHEDD2_NAME
JOB_ROUTER_SCHEDD2_NAME = htcondor-ce.chtc.wisc.edu
 # at: /etc/condor-ce/config.d/02-ce-condor.conf, line 20
 # raw: JOB_ROUTER_SCHEDD2_NAME = $(FULL_HOSTNAME)
```

Verifying Resource Request Submission
-------------------------------------

After verifying that all the remote HTCondor-CE [daemons are up](#inspecting-daemons),
you can start submitting resource requests!

### Verifying authentication ###

Before submitting a successful resource request, you will want to verify that you have submit privileges.
For this, you will need a credential such as a grid proxy:

```console
$ voms-proxy-info
subject   : /DC=org/DC=cilogon/C=US/O=University of Wisconsin-Madison/CN=Brian Lin A2266246/CN=41319870
issuer    : /DC=org/DC=cilogon/C=US/O=University of Wisconsin-Madison/CN=Brian Lin A2266246
identity  : /DC=org/DC=cilogon/C=US/O=University of Wisconsin-Madison/CN=Brian Lin A2266246
type      : RFC compliant proxy
strength  : 1024 bits
path      : /tmp/x509up_u1000
timeleft  : 3:55:22
```

After you have retrieved your credential, verify that you have the ability to submit requests to the remote HTCondor-CE
(i.e., `WRITE` access) with [condor_ping](https://htcondor.readthedocs.io/en/latest/man-pages/condor_ping.html):

```console
$ export _condor_SEC_CLIENT_AUTHENTICATION_METHODS=SCITOKENS,GSI
$ export _condor_SEC_TOOL_DEBUG=D_SECURITY:2  # Extremely verbose debugging for troubleshooting authentication issues
$ condor_ping -name htcondor-ce.chtc.wisc.edu \
              -pool htcondor-ce.chtc.wisc.edu:9619 \
              -verbose \
              -debug \
               WRITE
[...]
Remote Version:              $CondorVersion: 8.9.8 Jun 29 2020 BuildID: 508520 PackageID: 8.9.8-0.508520 $
Local  Version:              $CondorVersion: 8.9.9 Aug 26 2020 BuildID: 515894 PackageID: 8.9.9-0.515894 PRE-RELEASE-UWCS $
Session ID:                  htcondor-ce:2980451:1604006441:0
Instruction:                 WRITE
Command:                     60021
Encryption:                  none
Integrity:                   MD5
Authenticated using:         GSI
All authentication methods:  FS,GSI
Remote Mapping:              blin@users.htcondor.org
Authorized:                  TRUE
```

If `condor_ping` fails,
ask the administrator to follow [this troubleshooting section](troubleshooting.md#jobs-fail-to-submit-to-the-ce),
set `SCHEDD_DEBUG = $(SCHEDD_DEBUG) D_SECURITY:2`,
and cross-check the [HTCondor-CE SchedLog](troubleshooting.md#schedlog) for authentication issues.

### Submitting a trace request ###

!!! note "HTCondor-CE client"
    This section requires an installation of the `htcondor-ce-client`.

The easiest way to troubleshoot end-to-end resource request submission is `condor_ce_trace`,
available in the `htcondor-ce-client`.
Follow [this documentation](../remote-job-submission.md#submission-with-debugging-tools) for detailed instructions for
installing and using `condor_ce_trace`.

Advanced Troubleshooting
------------------------

!!! note "HTCondor-CE client"
    This section requires an installation of the `htcondor-ce-client`.

If the issue at hand is complicated or the communication turnaround time with the administrator is too long,
it is often more expedient to grant the operator direct access to the HTCondor-CE host.
Instead of direct login access, HTCondor-CE has the ability to allow a remote operator to run commands on the host as an
unprivileged user.
This requires [permission to submit resource requests](#verifying-authentication) as well as an HTCondor-CE that is
configured to run local universe jobs:

```console
$ condor_config_val -name htcondor-ce.chtc.wisc.edu -pool htcondor-ce.chtc.wisc.edu:9619 -verbose START_LOCAL_UNIVERSE
START_LOCAL_UNIVERSE = TotalLocalJobsRunning + TotalSchedulerJobsRunning < 20
 # at: /etc/condor-ce/config.d/03-managed-fork.conf, line 11
 # raw: START_LOCAL_UNIVERSE = TotalLocalJobsRunning + TotalSchedulerJobsRunning < 20
 # default: TotalLocalJobsRunning < 200
```

After verifying that you can submit resource requests and that the HTCondor-CE supports local universe,
use [condor_ce_run](troubleshooting.md#condor_ce_run) to run commands on the remote HTCondor-CE host:

```console
$ condor_ce_run -lr htcondor-ce.chtc.wisc.edu /bin/sh -c 'condor_q -all'

-- Schedd: htcondor-ce.chtc.wisc.edu : <128.104.100.65:9618?... @ 10/29/20 17:42:27
OWNER   BATCH_NAME    SUBMITTED   DONE   RUN    IDLE   HOLD  TOTAL JOB_IDS
nu_lhcb ID: 530251   7/13 22:20      _      _      _      _      1 530251.0
nu_lhcb ID: 586158  10/28 05:15      _      _      _      1      1 586158.0
nu_lhcb ID: 586213  10/28 06:23      _      1      _      _      1 586213.0
nu_lhcb ID: 586228  10/28 06:23      _      1      _      _      1 586228.0
nu_lhcb ID: 586254  10/28 06:23      _      1      _      _      1 586254.0
nu_lhcb ID: 586289  10/28 07:58      _      _      _      1      1 586289.0
```

Getting Help
------------

If you have any questions or issues about troubleshooting remote HTCondor-CEs, please [contact us](/#contact-us) for
assistance.
