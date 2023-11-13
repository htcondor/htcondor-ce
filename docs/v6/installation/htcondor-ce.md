Installing HTCondor-CE 6
========================

!!! tip "Joining the OSG Consortium (OSG)?"
    If you are installing an HTCondor-CE for the OSG, consult the
    [OSG-specific documentation](https://osg-htc.org/docs/compute-element/htcondor-ce-overview/).

HTCondor-CE is a special configuration of the HTCondor software designed as a Compute Entrypoint solution for computing
grids (e.g. [European Grid Infrastructure](https://www.egi.eu/), [The OSG Consortium](https://osg-htc.org/)).
It is configured to use the [Job Router daemon](https://htcondor.readthedocs.io/en/lts/grid-computing/job-router.html)
to delegate resource allocation requests by transforming and submitting them to the site’s batch system.
See the [home page](../../index.md) for more details on the features and architecture of HTCondor-CE.

Use this page to learn how to install, configure, run, test, and troubleshoot HTCondor-CE 6 from the
[CHTC yum repositories](https://htcondor.org/downloads/htcondor-ce.html).

Before Starting
---------------

Before starting the installation process, consider the following points
(consulting [the reference page](../reference.md) as necessary):

-   **User IDs:** If they do not exist already, the installation will create the `condor` Linux user (UID 4716)
-   **SSL certificate:** The HTCondor-CE service uses a host certificate and key for SSL authentication
-   **DNS entries:** Forward and reverse DNS must resolve for the HTCondor-CE host
-   **Network ports:** The pilot factories must be able to contact your HTCondor-CE service on port 9619 (TCP)
-   **Submit host:** HTCondor-CE should be installed on a host that already has the ability to submit jobs into your
    local cluster running supported batch system software (Grid Engine, HTCondor, LSF, PBS/Torque, Slurm) 
-   **File Systems**: Non-HTCondor batch systems require a
    [shared file system](../configuration/local-batch-system.md#sharing-the-spool-directory) between the HTCondor-CE
    host and the batch system worker nodes.

There are some one-time (per host) steps to prepare in advance:

- Ensure the host has a supported operating system (Red Hat Enterprise Linux variant 7)
- Obtain root access to the host
- Prepare the [EPEL](https://fedoraproject.org/wiki/EPEL) and [HTCondor Development](https://research.cs.wisc.edu/htcondor/yum/) Yum
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

Next Steps
----------

At this point, you should have all the necessary binaries, scripts, and default configurations.
The next step is to [configure authentication](../configuration/authentication.md) to allow for remote submission to
your HTCondor-CE.

Getting Help
------------

If you have any questions or issues with the installation process, please [contact us](../../index.md#contact-us) for assistance.
