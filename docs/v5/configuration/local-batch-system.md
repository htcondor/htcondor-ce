Configuring for the Local Batch System
======================================

Before HTCondor-CE can submit jobs to your local batch system, it has to be configured to do so.
The configuration will differ depending on if your local batch system is HTCondor or one of the other supported batch
systems.
Choose the section corresponding to your batch system below.

HTCondor Batch Systems
----------------------

To configure HTCondor-CE for an HTCondor batch system, set `JOB_ROUTER_SCHEDD2_POOL` to your site's central manager host
and port:

```
JOB_ROUTER_SCHEDD2_POOL = cm.chtc.wisc.edu:9618
```

Additionally, set `JOB_ROUTER_SCHEDD2_SPOOL` to the location of the local batch `SPOOL` directory on the CE host if it
is different than the default location (`/var/lib/condor/spool`).

Non-HTCondor Batch Systems
--------------------------

### Configuring the BLAHP ###

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

### Sharing the SPOOL directory ###

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
