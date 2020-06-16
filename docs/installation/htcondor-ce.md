Installing an HTCondor-CE
=========================

!!! note
    If you are installing an HTCondor-CE for the Open Science Grid (OSG), consult the
    [OSG-specific documentation](https://opensciencegrid.org/docs/compute-element/install-htcondor-ce/).

The [HTCondor-CE](overview) software is a *job gateway* based on [HTCondor](http://htcondor.org) for Compute Elements
(CE) belonging to a computing grid
(e.g. [European Grid Infrastructure](https://www.egi.eu/), [Open Science Grid](https://opensciencegrid.org/)).
As such, HTCondor-CE serves as an entry point for incoming grid jobs — it handles authorization and delegation of jobs
to a grid site's local batch system.
See the [overview page](/overview) for more details on the features and architecture of HTCondor-CE.

Use this page to learn how to install, configure, run, test, and troubleshoot HTCondor-CE from the
[HTCondor Yum repositories](http://research.cs.wisc.edu/htcondor/instructions/).

Before Starting
---------------

Before starting the installation process, consider the following points
(consulting [the reference page](/reference) as necessary):

-   **User IDs:** If they do not exist already, the installation will create the `condor` Linux user (UID 4716)
-   **SSL certificate:** The HTCondor-CE service uses a host certificate at `/etc/grid-security/hostcert.pem` and an
    accompanying key at `/etc/grid-security/hostkey.pem`
-   **DNS entries:** Forward and reverse DNS must resolve for the HTCondor-CE host
-   **Network ports:** The pilot factories must be able to contact your HTCondor-CE service on port 9619 (TCP)
-   **Submit host:** HTCondor-CE should be installed on a host that already has the ability to submit jobs into your
    local cluster running supported batch system software (Grid Engine, HTCondor, LSF, PBS/Torque, Slurm) 
-   **File Systems**: Non-HTCondor batch systems require a [shared file system](#batch-systems-other-than-htcondor)
    between the HTCondor-CE host and the batch system worker nodes.

There are some one-time (per host) steps to prepare in advance:

- Ensure the host has a supported operating system (Red Hat Enterprise Linux variant 7)
- Obtain root access to the host
- Prepare the [EPEL](https://fedoraproject.org/wiki/EPEL) and [HTCondor](https://research.cs.wisc.edu/htcondor/yum/) Yum
  repositories
- Install CA certificates and VO data into `/etc/grid-security/certificates` and `/etc/grid-security/vomsdir`,
  respectively

Installing HTCondor-CE
----------------------

!!! important
    HTCondor-CE must be installed on a host that is configured to submit jobs to your batch system.
    The details of this setup is site-specific by nature and therefore beyond the scope of this document.

1. Clean yum cache:

        ::console
        root@host # yum clean all --enablerepo=*

1. Update software:

        :::console
        root@host # yum update

    This command will update **all** packages

1. Install the `fetch-crl` package, available from the EPEL repositories.

        :::console
        root@host # yum install fetch-crl

1. Select the appropriate convenience RPM:

    | If your batch system is... | Then use the following package... |
    |:---------------------------|:----------------------------------|
    | Grid Engine                | `htcondor-ce-sge`                      |
    | HTCondor                   | `htcondor-ce-condor`                   |
    | LSF                        | `htcondor-ce-lsf`                      |
    | PBS/Torque                 | `htcondor-ce-pbs`                      |
    | SLURM                      | `htcondor-ce-slurm`                    |

1. Install the CE software:

        :::console
        root@host # yum install <PACKAGE>

    Where `<PACKAGE>` is the package you selected in the above step.

Configuring HTCondor-CE
-----------------------

There are a few required configuration steps to connect HTCondor-CE with your batch system and authentication method.
For more advanced configuration, see the section on [optional configurations](#optional-configuration).

### Configuring authentication ###

To authenticate job submission from external users and VOs, HTCondor-CE can be configured to use a
[built-in mapfile](#built-in-mapping) or to make [Globus callouts](#globus-callouts) to an external service like Argus
or LCMAPS. THe former option is simpler but the latter option may be preferred if your grid supports it or your site
already runs such a service.

#### Built-in mapfile ####

The built-in mapfile is a
[unified HTCondor mapfile](https://htcondor.readthedocs.io/en/stable/admin-manual/security.html#the-unified-map-file-for-authentication)
located at `/etc/condor-ce/condor_mapfile`.
This file is parsed in line-by-line order and HTCondor-CE will use the first line that matches.
Therefore, mappings should be added to the top of the file.

!!! warning
    `condor_mapfile.rpmnew` files may be generated upon HTCondor-CE version updates and they should be merged into
    `condor_mapfile`.

To configure authorization for users submitting jobs with an X.509 proxy certificate to your HTCondor-CE, add lines
of the following format:

```
GSI "^<DISTINGUISHED NAME>$" <USERNAME>@users.htcondor.org
```

Replacing `<DISTINGUISHED NAME`> (escaping any '/' with '\/') and `<USERNAME`> with the distinguished name of the
incoming certificate and the unix account under which the job should run, respectively.

VOMS attributes of incoming X.509 proxy certificates can also be used for mapping:

```
GSI "<DISTINGUISHED NAME>,<VOMS FQAN 1>,<VOMS FQAN 2>,...,<VOMSFQAN N>" <USERNAME>@users.htcondor.org
```

Replacing `<DISTINGUISHED NAME`> (escaping any '/' with '\/'), `<VOMSFQAN`> fields, and `<USERNAME`> with the
distinguished name of the incoming certificate, the VOMS roles and groups, and the unix account under which the job
should run, respectively.

Additionally, you can use regular expressions for mapping certificate and VOMS attribute credentials.
For example, to map any certificate from the `GLOW` VO with the `htpc` role to the `glow` user, add the following line:

```
GSI ".*,\/GLOW\/Role=htpc.*" glow@users.htcondor.org
```

!!! warning
    You should only add mappings to the mapfile. Do not remove any of the default mappings:

        GSI "(/CN=[-.A-Za-z0-9/= ]+)" \1@unmapped.htcondor.org
        CLAIMTOBE .* anonymous@claimtobe
        FS (.*) \1

#### Globus Callout ####

To use a Globus callout to a service like LCMAPS or Argus, you will need to have the relevant library installed as well
as the following HTCondor-CE configuration:

1. Add the following line to the top of `/etc/condor-ce/condor_mapfile`:

        GSI (.*) GSS_ASSIST_GRIDMAP

1. Create `/etc/grid-security/gsi-authz.conf` with the following content:

    - For LCMAPS:

            globus_mapping liblcas_lcmaps_gt4_mapping.so lcmaps_callout

    - For Argus:

            globus_mapping /usr/lib64/libgsi_pep_callout.so argus_pep_callout

### Configuring the batch system ###

Before HTCondor-CE can submit jobs to your local batch system, it has to be configured to do so.
The configuration will differ depending on if your local batch system is HTCondor or one of the other supported batch
systems.
Choose the section corresponding to your batch system below.

#### HTCondor batch systems ####

To configure HTCondor-CE for an HTCondor batch system, set `JOB_ROUTER_SCHEDD2_POOL` to your site's central manager host
and port:

```
JOB_ROUTER_SCHEDD2_POOL = cm.chtc.wisc.edu:9618
```

Additionally, set `JOB_ROUTER_SCHEDD2_SPOOL` to the location of the local batch `SPOOL` directory on the CE host if it
is different than the default location (`/var/lib/condor/spool`).

#### Non-HTCondor batch systems ####

##### Configuring the BLAHP #####

HTCondor-CE uses the Batch Language ASCII Helper Protocol (BLAHP) to submit and track jobs to non-HTCondor batch systems.
To work with the HTCondor-CE, modify `/usr/libexec/condor/glite/etc/batch_gahp.config` using the following steps:

1. Disable BLAHP handling of certificate proxies:

        blah_disable_wn_proxy_renewal=yes
        blah_delegate_renewed_proxies=no
        blah_disable_limited_proxy=yes

1. **(Optional)** If your batch system tools are installed in a non-standard location (i.e., outside of `/usr/bin/`),
   set the corresponding `*_binpath` variable to the directory containing your batch system tools:

    | **If your batch system is...** | **Then change the following configuration variable...** |
    |--------------------------------|---------------------------------------------------------|
    | LSF                            | `lsf_binpath`                                           |
    | PBS/Torque                     | `pbs_binpath`                                           |
    | SGE                            | `sge_binpath`                                           |
    | Slurm                          | `slurm_binpath`                                         |

    For example, if your Slurm binaries (e.g. `sbatch`) exist in `/opt/slurm/bin`, you would set the following:

        slurm_binpath=/opt/slurm/bin/

##### Sharing the SPOOL directory #####

Non-HTCondor batch systems require a shared file system configuration to support file transfer from the HTCondor-CE to
your site's worker nodes.
The current recommendation is to run a dedicated NFS server on the **CE host**.
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

### Optional Configuration ###

The following configuration steps are optional and will not be required for all sites.
If you do not need any of the following special configurations, skip to
[the section on next steps](#next-steps).

#### Configuring for multiple network interfaces

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

#### Enabling the monitoring web interface

The HTCondor-CE View is an optional web interface to the status of your CE.
To run the HTCondor-CE View, install the appropriate package and set the relevant configuration.

1.  Begin by installing the `htcondor-ce-view` package:

        :::console
        root@host # yum install htcondor-ce-view

2.  Next, uncomment the `DAEMON_LIST` configuration located at `/etc/condor-ce/config.d/05-ce-view.conf`:

        DAEMON_LIST = $(DAEMON_LIST), CEVIEW, GANGLIAD, SCHEDD

3.  Restart the `condor-ce` service

4.  Verify the service by entering your CE's hostname into your web browser

The website is served on port 80 by default.
To change this default, edit the value of `HTCONDORCE_VIEW_PORT` in `/etc/condor-ce/config.d/05-ce-view.conf`.

#### Uploading accounting records to APEL ####

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

1. Start and enable the `condor-ce-apel` [services](/verification#managing-htcondor-ce-services) appropriate for your
   operating system.

#### Enabling BDII integration ####

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


Next Steps
----------

At this point, you should have an installation of HTCondor-CE that will forward grid jobs into your site's batch system
unchanged.
If you need to transform incoming grid jobs (e.g. by setting a partition, queue, or accounting group), configure the
[HTCondor-CE Job Router](/batch-system-integration).
Otherwise, continue to the [this document](/verification) to start the relevant services and verify your installation.

Getting Help
------------

If you have any questions or issues with the installation process, please [contact us](/#contact-us) for assistance,
