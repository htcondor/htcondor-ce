Installing and Maintaining HTCondor-CE
======================================

The [HTCondor-CE](htcondor-ce-overview) software is a *job gateway* for an OSG Compute Element (CE).
As such, HTCondor-CE is the entry point for jobs coming from the OSG — it handles authorization and delegation of jobs
to your local batch system.
In OSG today, most CEs accept *pilot jobs* from a factory, which in turn are able to accept and run end-user jobs.
See the [HTCondor-CE Overview](htcondor-ce-overview) for a much more detailed introduction.

Use this page to learn how to install, configure, run, test, and troubleshoot HTCondor-CE from the OSG software
repositories.

!!! note
    If you are installing an HTCondor-CE for use outside of the OSG, consult [this documentation](https://htcondor-wiki.cs.wisc.edu/index.cgi/wiki?p=InstallHtcondorCe)

Before Starting
---------------

Before starting the installation process, consider the following points
(consulting [the Reference section below](#reference) as needed):

-   **User IDs:** If they do not exist already, the installation will create the Linux users `condor` (UID 4716) and
    `gratia` (UID 42401)
-   **SSL certificate:** The HTCondor-CE service uses a host certificate at `/etc/grid-security/hostcert.pem` and an
    accompanying key at `/etc/grid-security/hostkey.pem`
-   **DNS entries:** Forward and reverse DNS must resolve for the HTCondor-CE host
-   **Network ports:** The pilot factories must be able to contact your HTCondor-CE service on port 9619 (TCP)
-   **Submit host:** HTCondor-CE should be installed on a host that already has the ability to submit jobs into your
    local cluster
-   **File Systems**: Non-HTCondor batch systems require a [shared file system](#batch-systems-other-than-htcondor)
    between the HTCondor-CE host and the batch system worker nodes.

As with all OSG software installations, there are some one-time (per host) steps to prepare in advance:

- Ensure the host has [a supported operating system](/release/supported_platforms)
- Obtain root access to the host
- Prepare the [required Yum repositories](/common/yum)
- Install [CA certificates](/common/ca)

Installing HTCondor-CE
----------------------

An HTCondor-CE installation consists of the job gateway (i.e., the HTCondor-CE job router) and other support software
(e.g., GridFTP, a Gratia probe, authentication software).
To simplify installation, OSG provides convenience RPMs that install all required software.

1. Clean yum cache:

        ::console
        root@host # yum clean all --enablerepo=*

1. Update software:

        :::console
        root@host # yum update

    This command will update **all** packages

1. **(Optional)** If your batch system is already installed via non-RPM means and is in the following list, install the
   appropriate 'empty' RPM.
   Otherwise, skip to the next step.

    | If your batch system is… | Then run the following command…                       |
    |:-------------------------|:------------------------------------------------------|
    | HTCondor                 | `yum install empty-condor --enablerepo=osg-empty`     |
    | SLURM                    | `yum install empty-slurm --enablerepo=osg-empty`      |

1. **(Optional)** If your HTCondor batch system is already installed via non-OSG RPM means, add the line below to
`/etc/yum.repos.d/osg.repo`.
   Otherwise, skip to the next step.

        exclude=condor

1. Select the appropriate convenience RPM:

    | If your batch system is... | Then use the following package... |
    |:---------------------------|:----------------------------------|
    | HTCondor                   | `osg-ce-condor`                   |
    | LSF                        | `osg-ce-lsf`                      |
    | PBS                        | `osg-ce-pbs`                      |
    | SGE                        | `osg-ce-sge`                      |
    | SLURM                      | `osg-ce-slurm`                    |

1. Install the CE software:

        :::console
        root@host # yum install <PACKAGE>

    Where `<PACKAGE>` is the package you selected in the above step.

Configuring HTCondor-CE
-----------------------

There are a few required configuration steps to connect HTCondor-CE with your batch system and authentication method.
For more advanced configuration, see the section on [optional configurations](#optional-configuration).

### Configuring the batch system

!!! important
    HTCondor-CE must be installed on a host that is configured to submit jobs to your batch system.
    The details of this configuration is likely site-specific and therefore beyond the scope of this document.

Enable your batch system in the HTCondor-CE configuration by editing the `enabled` field in the
`/etc/osg/config.d/20-<YOUR BATCH SYSTEM>.ini`:

``` file
enabled = True
```

If you are using HTCondor as your **local batch system** (i.e., in addition to your HTCondor-CE), skip to the
[configuring authorization](#configuring-authorization) section.
For other batch systems (e.g., PBS, LSF, SGE, SLURM), keep reading.

#### Batch systems other than HTCondor

Non-HTCondor batch systems require a shared file system configuration to support file transfer from the HTCondor-CE to
your site's worker nodes.
The current recommendation is to run a dedicated NFS server (whose installation is beyond the scope of this document) on
the **CE host**.
In this setup, HTCondor-CE writes to the local spool directory, the NFS server shares the directory, and each worker
node mounts the directory in the same location as on the CE.
For example, if your spool directory is `/var/lib/condor-ce` (the default), you must mount the shared directory to
`/var/lib/condor-ce` on the worker nodes.

!!! note
    If you choose not to host the NFS server on your CE, you will need to turn off root squash so that the HTCondor-CE
    daemons can write to the spool directory.

You can control the value of the spool directory by setting `SPOOL` in `/etc/condor-ce/config.d/99-local.conf` (create
this file if it doesn't exist).
For example, the following sets the `SPOOL` directory to `/home/condor`:

``` file
SPOOL = /home/condor
```

!!! note
    The shared spool directory must be readable and writeable by the `condor` user for HTCondor-CE to function correctly.

### Configuring authorization

To configure which virtual organizations and users are authorized to submit jobs to your, follow the instructions in
[the LCMAPS VOMS plugin document](/security/lcmaps-voms-authentication#configuring-the-lcmaps-voms-plugin).

!!! note
    If your local batch system is HTCondor, it will attempt to utilize the LCMAPS callouts if enabled in the
    `condor_mapfile`.
    If this is not the desired behavior, set `GSI_AUTHZ_CONF=/dev/null` in the local HTCondor configuration.

### Configuring CE collector advertising

To split jobs between the various sites of the OSG, information about each site's capabilities are uploaded to a central
collector.
The job factories then query the central collector for idle resources and submit pilot jobs to the available sites.
To advertise your site, you will need to enter some information about the worker nodes of your clusters.

Please see the [Subcluster / Resource Entry configuration document](/other/configuration-with-osg-configure#subcluster-resource-entry)
about configuring the data that will be uploaded to the central collector.

### Applying configuration settings

Making changes to the OSG configuration files in the `/etc/osg/config.d` directory does not apply those settings to
software automatically.
Settings that are made outside of the OSG directory take effect immediately or at least when the relevant service is
restarted.
For the OSG settings, use the [osg-configure](/other/configuration-with-osg-configure) tool to validate (to a limited
extent) and apply the settings to the relevant software components.
The `osg-configure` software is included automatically in an HTCondor-CE installation.

1. Make all changes to `.ini` files in the `/etc/osg/config.d` directory

    !!! note
        This document describes the critical settings for HTCondor-CE and related software.
        You may need to configure other software that is installed on your HTCondor-CE host, too.

2. Validate the configuration settings

        :::console
        root@host # osg-configure -v

3. Fix any errors (at least) that `osg-configure` reports.
4. Once the validation command succeeds without errors, apply the configuration settings:

        :::console
        root@host # osg-configure -c

### Optional configuration

The following configuration steps are optional and will likely not be required for setting up a small site.
If you do not need any of the following special configurations, skip to
[the section on using HTCondor-CE](#using-htcondor-ce).

-   [Transforming and filtering jobs](#transforming-and-filtering-jobs)
-   [Configuring for multiple network interfaces](#configuring-for-multiple-network-interfaces)
-   [Limiting or disabling locally running jobs on the CE](#limiting-or-disabling-locally-running-jobs-on-the-ce)
-   [Accounting with multiple CEs or local user jobs](#accounting-with-multiple-ces-or-local-user-jobs)
-   [HTCondor accounting groups](#htcondor-accounting-groups)
-   [HTCondor-CE monitoring web interface](#install-and-run-the-htcondor-ce-view)

#### Transforming and filtering jobs

If you need to modify or filter jobs, more information can be found in the [Job Router Recipes](job-router-recipes)
document.

!!! note
    If you need to assign jobs to HTCondor accounting groups, refer to [this](#htcondor-accounting-groups) section.

#### Configuring for multiple network interfaces

If you have multiple network interfaces with different hostnames, the HTCondor-CE daemons need to know which hostname
and interface to use when communicating to each other.
Set `NETWORK_HOSTNAME` and `NETWORK_INTERFACE` to the hostname and IP address of your public interface, respectively, in
`/etc/condor-ce/config.d/99-local.conf` directory with the line:

``` file
NETWORK_HOSTNAME = condorce.example.com
NETWORK_INTERFACE = 127.0.0.1
```

Replacing `condorce.example.com` text with your public interface’s hostname and `127.0.0.1` with your public interface’s
IP address.

#### Limiting or disabling locally running jobs on the CE

If you want to limit or disable jobs running locally on your CE, you will need to configure HTCondor-CE's local and
scheduler universes.
Local and scheduler universes allow jobs to be run on the CE itself, mainly for remote troubleshooting.
Pilot jobs will not run as local/scheduler universe jobs so leaving them enabled does NOT turn your CE into another
worker node.

The two universes are effectively the same (scheduler universe launches a starter process for each job), so we will be
configuring them in unison.

- **To change the default limit** on the number of locally run jobs (the current default is 20), add the following to
  `/etc/condor-ce/config.d/99-local.conf`:

        START_LOCAL_UNIVERSE = TotalLocalJobsRunning + TotalSchedulerJobsRunning < <JOB-LIMIT>
        START_SCHEDULER_UNIVERSE = $(START_LOCAL_UNIVERSE)

    Where `<JOB-LIMIT>` is the maximum number of jobs allowed to run locally

- **To only allow a specific user** to start locally run jobs, add the following to
  `/etc/condor-ce/config.d/99-local.conf`:

        START_LOCAL_UNIVERSE = target.Owner =?= "<USERNAME>"
        START_SCHEDULER_UNIVERSE = $(START_LOCAL_UNIVERSE)

   Change `<USERNAME>` for the username allowed to run jobs locally

- **To disable** locally run jobs, add the following to `/etc/condor-ce/config.d/99-local.conf`:

        START_LOCAL_UNIVERSE = False
        START_SCHEDULER_UNIVERSE = $(START_LOCAL_UNIVERSE)

!!! note
    RSV requires the ability to start local universe jobs so if you are using RSV, you need to allow local universe jobs
    from the `rsv` user.

#### Accounting with multiple CEs or local user jobs

!!! note
    For non-HTCondor batch systems only

If your site has multiple CEs or you have non-grid users submitting to the same local batch system, the OSG accounting
software needs to be configured so that it doesn't over report the number of jobs.
Use the following table to determine which file requires editing:

| If your batch system is… | Then edit the following file on each of your CE(s)… |
|:-------------------------|:--------------------------------------------|
| LSF                      | `/etc/gratia/pbs-lsf/ProbeConfig`           |
| PBS                      | `/etc/gratia/pbs-lsf/ProbeConfig`           |
| SGE                      | `/etc/gratia/sge/ProbeConfig`               |
| SLURM                    | `/etc/gratia/slurm/ProbeConfig`             |

Then edit the value of `SuppressNoDNRecords` on each of your CE's so that it reads:

``` file
SuppressNoDNRecords="1"
```

#### HTCondor accounting groups

!!! note
    For HTCondor batch systems only

If you want to provide fairshare on a group basis, as opposed to a Unix user basis, you can use HTCondor accounting groups.
They are independent of the Unix groups the user may already be in and are [documented in the HTCondor manual](http://research.cs.wisc.edu/htcondor/manual/v8.6/3_6User_Priorities.html#SECTION00467000000000000000).
If you are using HTCondor accounting groups, you can map jobs from the CE into HTCondor accounting groups based on their
UID, their DN, or their VOMS attributes.

-   **To map UIDs to an accounting group,** add entries to `/etc/osg/uid_table.txt` with the following form:

        uid GroupName

    The following is an example `uid_table.txt`:

        uscms02 TestGroup
        osg     other.osgedu

-   **To map DNs or VOMS attributes to an accounting group,** add lines to `/etc/osg/extattr_table.txt` with the
    following form:

        SubjectOrAttribute GroupName

    The `SubjectOrAttribute` can be a Perl regular expression. The following is an example `extattr_table.txt`:

        cmsprio cms.other.prio
        cms\/Role=production cms.prod
        \/DC=com\/DC=DigiCert-Grid\/O=Open\ Science\ Grid\/OU=People\/CN=Brian\ Lin\ 1047 osg.test
        .* other

!!! note
    Entries in `/etc/osg/uid_table.txt` are honored over `/etc/osg/extattr_table.txt` if a job would match to lines in
    both files.

#### Install and run the HTCondor-CE View

The HTCondor-CE View is an optional web interface to the status of your CE. To run the View,

1.  Begin by installing the package htcondor-ce-view:

        :::console
        root@host # yum install htcondor-ce-view

2.  Next, uncomment the `DAEMON_LIST` configuration located at `/etc/condor-ce/config.d/05-ce-view.conf`:

        DAEMON_LIST = $(DAEMON_LIST), CEVIEW, GANGLIAD, SCHEDD

3.  Restart the CE service:

        :::console
        root@host # service condor-ce restart

4.  Verify the service by entering your CE's hostname into your web browser

The website is served on port 80 by default. To change this default, edit the value of `HTCONDORCE_VIEW_PORT` in
`/etc/condor-ce/config.d/05-ce-view.conf`.

Using HTCondor-CE
-----------------

As a site administrator, there are a few ways to use the HTCondor-CE:

-   Managing the HTCondor-CE and associated services
-   Using HTCondor-CE administrative tools to monitor and maintain the job gateway
-   Using HTCondor-CE user tools to test gateway operations

### Managing HTCondor-CE and associated services

In addition to the HTCondor-CE job gateway service itself, there are a number of supporting services in your installation.
The specific services are:

| Software          | Service name                          | Notes                                                                                  |
|:------------------|:--------------------------------------|:---------------------------------------------------------------------------------------|
| Fetch CRL         | `fetch-crl-boot` and `fetch-crl-cron` | See [CA documentation](/common/ca#managing-fetch-crl-services) for more info |
| Gratia            | `gratia-probes-cron`                  | Accounting software                                                                    |
| Your batch system | `condor` or `pbs_server` or …         |                                                                                        |
| HTCondor-CE       | `condor-ce`                           |                                                                                        |

Start the services in the order listed and stop them in reverse order. As a reminder, here are common service commands (all run as `root`):

| To...                                   | On EL6, run the command...                  | On EL7, run the command...                      |
| :-------------------------------------- | :----------------------------------------   | :--------------------------------------------   |
| Start a service                         | `service <SERVICE-NAME> start` | `systemctl start <SERVICE-NAME>`   |
| Stop a  service                         | `service <SERVICE-NAME> stop`  | `systemctl stop <SERVICE-NAME>`    |
| Enable a service to start on boot       | `chkconfig <SERVICE-NAME> on`  | `systemctl enable <SERVICE-NAME>`  |
| Disable a service from starting on boot | `chkconfig <SERVICE-NAME> off` | `systemctl disable <SERVICE-NAME>` |

### Using HTCondor-CE tools

Some of the HTCondor-CE administrative and user tools are documented in [the HTCondor-CE troubleshooting guide](troubleshoot-htcondor-ce).

Validating HTCondor-CE
----------------------

To validate an HTCondor-CE, perform the following verification steps:

1. Verify that local job submissions complete successfully from the CE host.
   For example, if you have a Slurm cluster, run `sbatch` from the CE and verify that it runs and completes with
   `scontrol` and `sacct`.

1. Verify that all the necessary daemons are running with
   [condor\_ce\_status -any](/compute-element/troubleshoot-htcondor-ce#condor_ce_status).

1. Verify the CE's network configuration using
   [condor\_ce\_host\_network\_check](/compute-element/troubleshoot-htcondor-ce#condor_ce_host_network_check).

1. Verify that jobs can complete successfully using
   [condor\_ce\_trace](/compute-element/troubleshoot-htcondor-ce#condor_ce_trace).

Troubleshooting HTCondor-CE
---------------------------

For information on how to troubleshoot your HTCondor-CE, please refer to
[the HTCondor-CE troubleshooting guide](troubleshoot-htcondor-ce).

Registering the CE
------------------

To be part of the OSG Production Grid, your CE must be
[registered with the OSG](https://github.com/opensciencegrid/topology#topology).
To register your resource:

1.  Identify the facility, site, and resource group where your HTCondor-CE is hosted.
    For example, the Center for High Throughput Computing at the University of Wisconsin-Madison uses the following
    information:

        Facility: University of Wisconsin
        Site: CHTC
        Resource Group: CHTC

1. Using the above information, [create or update](https://github.com/opensciencegrid/topology#how-to-register) the
   appropriate YAML file, using [this template](https://github.com/opensciencegrid/topology/blob/master/template-resourcegroup.yaml)
   as a guide.


Getting Help
------------

To get assistance, please use the [this page](/common/help).

Reference
---------

Here are some other HTCondor-CE documents that might be helpful:

-   [HTCondor-CE overview and architecture](htcondor-ce-overview)
-   [Configuring HTCondor-CE job routes](job-router-recipes)
-   [The HTCondor-CE troubleshooting guide](troubleshoot-htcondor-ce)
-   [Submitting jobs to HTCondor-CE](submit-htcondor-ce)

### Configuration

The following directories contain the configuration for HTCondor-CE.
The directories are parsed in the order presented and thus configuration within the final directory will override
configuration specified in the previous directories.

| Location                         | Comment                                                                                                                    |
|:---------------------------------|:---------------------------------------------------------------------------------------------------------------------------|
| `/usr/share/condor-ce/config.d/` | Configuration defaults (overwritten on package updates)                                                                    |
| `/etc/condor-ce/config.d/`       | Files in this directory are parsed in alphanumeric order (i.e., `99-local.conf` will override values in `01-ce-auth.conf`) |

For a detailed order of the way configuration files are parsed, run the following command:

``` console
user@host $ condor_ce_config_val -config
```

### Users

The following users are needed by HTCondor-CE at all sites:

| User     | Comment                                                                                       |
|:---------|:----------------------------------------------------------------------------------------------|
| `condor` | The HTCondor-CE will be run as root, but perform most of its operations as the `condor` user. |
| `gratia` | Runs the Gratia probes to collect accounting data                                             |

### Certificates

| File             | User that owns certificate | Path to certificate               |
|:-----------------|:---------------------------|:----------------------------------|
| Host certificate | `root`                     | `/etc/grid-security/hostcert.pem` |
| Host key         | `root`                     | `/grid-security/hostkey.pem`  |

Find instructions to request a host certificate [here](/security/host-certs).

### Networking

| Service Name | Protocol | Port Number | Inbound | Outbound | Comment                 |
| :----------- | :------: | :---------: | :-----: | :------: | :---------------------- |
| Htcondor-CE  | tcp      | 9619        | X       |          | HTCondor-CE shared port |

Allow inbound and outbound network connection to all internal site servers, such as the batch system head-node only
ephemeral outgoing ports are necessary.
