Optional Configuration
======================

The following configuration steps are optional and will not be required for all sites.
If you do not need any of the following special configurations, skip to
the page for [verifying your HTCondor-CE](../verification.md).

Configuring for Multiple Network Interfaces
-------------------------------------------

If you have multiple network interfaces with different hostnames, the HTCondor-CE daemons need to know which hostname
and interface to use when communicating with each other.
Set `NETWORK_HOSTNAME` and `NETWORK_INTERFACE` to the hostname and IP address of your public interface, respectively, in
`/etc/condor-ce/config.d/99-local.conf` directory with the line:

``` file
NETWORK_HOSTNAME = condorce.example.com
NETWORK_INTERFACE = 127.0.0.1
```

Replacing `condorce.example.com` text with your public interface’s hostname and `127.0.0.1` with your public interface’s
IP address.

Limiting or Disabling Locally Running Jobs
------------------------------------------

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

Enabling the Monitoring Web Interface
-------------------------------------

The HTCondor-CE View is an optional web interface to the status of your CE.
To run the HTCondor-CE View, install the appropriate package and set the relevant configuration.

1.  Begin by installing the `htcondor-ce-view` package:

        :::console
        root@host # yum install htcondor-ce-view

1.  Restart the `condor-ce` service

1.  Verify the service by entering your CE's hostname into your web browser

The website is served on port 80 by default.
To change this default, edit the value of `HTCONDORCE_VIEW_PORT` in `/etc/condor-ce/config.d/05-ce-view.conf`.

Uploading Accounting Records to APEL
------------------------------------

!!! note "Batch System Support"
    HTCondor-CE only supports generation of APEL accounting records for HTCondor batch systems.

For sites outside of the OSG that need to upload the APEL accounting records, HTCondor-CE supports uploading batch and
blah APEL records for HTCondor batch systems:

1. Install the HTCondor-CE APEL package on your CE host:

        :::console
        root@host # yum install htcondor-ce-apel

1. On each worker node, set the appropriate scaling factor in the HTCondor configuration (i.e. `/etc/condor/config.d/`)
   and advertise it in the startd ad:

        ApelScaling = <SCALING FACTOR>  # For example, 1.062
        STARTD_ATTRS = $(STARTD_ATTRS) ApelScaling

1. Configure the APEL parser, client, and SSM

    - Records are written to `APEL_OUTPUT_DIR` in the HTCondor-CE configuration (default: `/var/lib/condor-ce/apel/`)
    - Batch and blah record filenames are prefixed `batch-` and `blah-`, respectively

1. Start and enable the `condor-ce-apel` and `condor-ce-apel.timer`
   [services](../verification.md#managing-htcondor-ce-services)

Enabling BDII Integration
-------------------------

!!! note "Batch System Support"
    HTCondor-CE only supports reporting BDII information for HTCondor batch systems.

HTCondor-CE supports reporting BDII information for all HTCondor-CE endpoints and batch information for an HTCondor
batch system.
To make this information available, perform the following instructions on your site BDII host.

1. Install the HTCondor-CE BDII package:

        :::console
        root@host # yum install htcondor-ce-bdii

1. Configure HTCondor (`/etc/condor/config.d/`) on your site BDII host to point to your central manager:

        CONDOR_HOST = <CENTRAL MANAGER>

    Replacing `<CENTRAL MANAGER>` with the hostname of your HTCondor central manager

1. Configure BDII static information by modifying `/etc/condor/config.d/99-ce-bdii.conf`

Additionally, install the HTCondor-CE BDII package on each of your HTCondor-CE hosts:

```
root@host # yum install htcondor-ce-bdii
```
