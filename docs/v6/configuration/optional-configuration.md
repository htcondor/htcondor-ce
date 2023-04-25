Optional Configuration
======================

The following configuration steps are optional and will not be required for all sites.
If you do not need any of the following special configurations, skip to
the page for [verifying your HTCondor-CE](../operation.md).

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

Inserting IDTOKENs into the routed job's sandbox
------------------------------------------

If you want to insert IDTOKENS into the routed job's sandbox you can use the `SendIDTokens` route command, or
the `JOB_ROUTER_SEND_ROUTE_IDTOKENS` global configuration variable. Tokens
sent using this mechanism must be named and declared using the `JOB_ROUTER_CREATE_IDTOKEN_NAMES`
and [`JOB_ROUTER_CREATE_IDTOKEN_<name>`](https://htcondor.readthedocs.io/en/latest/admin-manual/configuration-macros.html#JOB_ROUTER_CREATE_IDTOKEN_%3CNAME%3E) configuration variables.  Tokens whose names are declared in
the `JOB_ROUTER_SEND_ROUTE_IDTOKENS` configuration variable are sent by default for each route that does
not have a `SendIDTokens` command.

- **To declare IDTOKENS for inclusion in glide-in jobs** for the purpose of advertising to a collector
  add something like the following to `/etc/condor-ce/config.d/99-local-ce-token.conf`:

        JOB_ROUTER_CREATE_IDTOKEN_NAMES = name1 name2
        JOB_ROUTER_CREATE_IDTOKEN_name1 @=end
            sub = "name1_pilot@domain"
            kid = "POOL"
            lifetime = 3900
            scope = "ADVERTISE_STARTD, ADVERTISE_MASTER, READ"
            dir = "/etc/condor-ce/gltokens/name1"
            filename = "ce_name1.idtoken"
            owner = "owner1"
        @end
        JOB_ROUTER_CREATE_IDTOKEN_Name2 @=end
            sub = "name2@users.htcondor.org"
            kid = "POOL"
            lifetime = 3900
            scope = "ADVERTISE_STARTD, ADVERTISE_MASTER, READ"
            dir = "/etc/condor-ce/gltokens/name2"
            filename = "ce_name2.idtoken"
            owner = "owner2"
        @end

- **To insert one of the above IDTOKENS in the sandbox of a routed job**, include the token name in the `SendIDTokens` route
   command like this.

        SendIDTokens = "Name2"

  **To add an IDTOKEN to a routed job in addition to the default tokens**, build a string containing the token name
   along with the value of the global configuration variable like this.

        SendIDTokens = "Name2 $(JOB_ROUTER_SEND_ROUTE_IDTOKENS)"

  **You can use an attribute of the source job** to choose the IDTOKEN by writing an expression like this.

        SendIDTokens = strcat( My.Owner, " $(JOB_ROUTER_SEND_ROUTE_IDTOKENS)")

  It is presumed that the value of `My.Owner` above is the same as the `<name>` of an IDTOKEN and as the `owner` field
  of that token.  For instance, the Fermilab CE config uses the above `SendIDTokens` expression and
  the following token declarations at the time of this guide.

        JOB_ROUTER_CREATE_IDTOKEN_NAMES = fermilab3 osg
        JOB_ROUTER_CREATE_IDTOKEN_fermilab3 @=end
            sub = "fermilabpilot@fnal.gov"
            kid = "POOL"
            lifetime = 3900
            scope = "ADVERTISE_STARTD, ADVERTISE_MASTER, READ"
            dir = "/etc/condor-ce/gltokens/fermilab"
            filename = "ce_fermilab3.idtoken"
            owner = "fermilab"
        @end
        JOB_ROUTER_CREATE_IDTOKEN_osg @=end
            sub = "osgpilot@fnal.gov"
            kid = "POOL"
            lifetime = 600
            scope = "ADVERTISE_STARTD, ADVERTISE_MASTER, READ"
            dir = "/etc/condor-ce/gltokens/fermilab"
            filename = "ce_osg.idtoken"
            owner = "osg"
        @end


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
blah APEL records for HTCondor batch systems.
Please refer to [EGI's HTCondor-CE Accounting Documentation](https://docs.egi.eu/providers/high-throughput-compute/htcondor-ce-accounting/).

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
