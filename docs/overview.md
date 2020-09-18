Overview
========

This document serves as an introduction to HTCondor-CE and how it works.
Before continuing with the overview, make sure that you are familiar with the following concepts:

-   What is a batch system and which one will you use
    ([HTCondor](http://htcondor.org),
    [Grid Engine](http://www.univa.com/products/),
    [LSF](https://www.ibm.com/us-en/marketplace/hpc-workload-management),
    [PBS Pro](https://www.pbsworks.com/PBSProduct.aspx?n=Altair-PBS-Professional&c=Overview-and-Capabilities)/[Torque](https://adaptivecomputing.com/cherry-services/torque-resource-manager/),
    and [Slurm](https://slurm.schedmd.com/))?
-   Pilot jobs and factories (e.g., [GlideinWMS](http://glideinwms.fnal.gov/doc.prd/index.html),
    [PanDA](http://news.pandawms.org/), [DIRAC](https://dirac.readthedocs.io/en/latest/index.html))

What is a Compute Entrypoint?
--------------------------

A Compute Entrypoint (CE) is the entry point for grid jobs into your local resources.
CEs are made up of a layer of software that you install on a machine that can submit jobs into your local batch system.
At the heart of the CE is the *job gateway* software, which is responsible for handling incoming jobs, authenticating
and authorizing them, and delegating them to your batch system for execution.

In many grids today, jobs that arrive at a CE (called *grid jobs*) are **not** end-user jobs, but rather pilot jobs
submitted from job factories.
Successful pilot jobs create and make available an environment for end-user jobs to match and ultimately run within
the pilot job.

!!! note
    The Compute Entrypoint was previously known as the "Compute Element".

What is HTCondor-CE?
--------------------

HTCondor-CE is a special configuration of the HTCondor software designed to be a job gateway solution for computing
grids (e.g. [European Grid Infrastructure](https://www.egi.eu/), [Open Science Grid](https://opensciencegrid.org/)).
It is configured to use the [Job Router daemon](https://htcondor.readthedocs.io/en/stable/grid-computing/job-router.html)
to delegate jobs by transforming and submitting them to the site’s batch system.

Benefits of running the HTCondor-CE:

-   **Scalability:** HTCondor-CE is capable of supporting job workloads of large sites
-   **Debugging tools:** HTCondor-CE offers [many tools to help troubleshoot](/troubleshooting#htcondor-ce-troubleshooting-tools)
    issues with jobs
-   **Routing as configuration:** HTCondor-CE’s mechanism to transform and submit jobs is customized via configuration
    variables, which means that customizations will persist across upgrades and will not involve modification of
    software internals to route jobs

How Jobs Run
------------

Once an incoming grid job is authorized, it is placed into HTCondor-CE’s scheduler where the Job Router creates a
transformed copy (called the *routed job*) and submits the copy to the batch system (called the *batch system job*).
After submission, HTCondor-CE monitors the batch system job and communicates its status to the original grid job, which
in turn notifies the original submitter (e.g., job factory) of any updates.
When the job completes, files are transferred along the same chain: from the batch system to the CE, then from the CE to
the original submitter.

### On HTCondor batch systems

For a site with an HTCondor **batch system**, the Job Router uses HTCondor protocols to place a transformed copy of the
grid job directly into the batch system’s scheduler, meaning that the routed and batch system jobs are one and the same.
Thus, there are three representations of your job, each with its own ID (see diagram below):

-   Submitter: the HTCondor job ID in the original queue
-   HTCondor-CE: the incoming grid job’s ID
-   HTCondor batch system: the routed job’s ID

![HTCondor-CE with an HTCondor batch system](/img/condor_batch.png)

In an HTCondor-CE/HTCondor setup, file transfer is handled natively between the two sets of daemons by the underlying
HTCondor software.

If you are running HTCondor as your batch system, you will have two HTCondor configurations side-by-side (one residing
in `/etc/condor/` and the other in `/etc/condor-ce`) and will need to make sure to differentiate the two when modifying
any configuration.

### On other batch systems

For non-HTCondor batch systems, the Job Router transforms the grid job into a routed job on the CE and the routed job
submits a job into the batch system via a process called the BLAHP.
Thus, there are four representations of your job, each with its own ID (see diagram below):

-   Submitter: the HTCondor job ID in the original queue
-   HTCondor-CE: the incoming grid job’s ID and the routed job’s ID
-   HTCondor batch system: the batch system’s job ID

Although the following figure specifies the PBS case, it applies to all non-HTCondor batch systems:

![HTCondor-CE with other batch systems](/img/other_batch.png)

With non-HTCondor batch systems, HTCondor-CE cannot use internal HTCondor protocols to transfer files so its "spool"
directory must be exported to a shared file system that is mounted on the batch system’s worker nodes.

### Hosted CE over SSH

The Hosted CE is designed to be an [HTCondor-CE as a Service](https://en.wikipedia.org/wiki/Software_as_a_service)
offered by central grid operations.
Hosted CEs submit jobs to remote clusters over SSH, providing a simple starting point for opportunistic resource
owners that want to start contributing to a computing grid with minimal effort.

![HTCondor-CE-Bosco](/img/bosco.png)

If your site intends to run over 10,000 concurrent grid jobs, you will need to host your own
[HTCondor-CE](/installation/htcondor-ce) because the Hosted CE has not yet been optimized for such loads.

How the CE is Customized
------------------------

Aside from the [basic configuration](/installation/htcondor-ce#configuring-htcondor-ce) required in the CE
installation, there are two main ways to customize your CE (if you decide any customization is required at all):

-   **Deciding which Virtual Organizations (VOs) are allowed to run at your site:** HTCondor-CE leverages HTCondor's
    built-in ability to authenticate incoming jobs based on their GSI credentials, including VOMS attributes.
    Additionally, HTCondor may be configured to callout to external authentication services like Argus or LCMAPS. 
-   **How to filter and transform the grid jobs to be run on your batch system:** Filtering and transforming grid jobs
    (i.e., setting site-specific attributes or resource limits), requires configuration of your site’s job routes.
    For examples of common job routes, consult the [batch system integration](/configuration/batch-system-integration)
    page.

How Security Works
------------------

In the OSG, security depends on a PKI infrastructure involving Certificate Authorities (CAs) where CAs sign and issue
certificates.
When these clients and hosts wish to communicate with each other, the identities of each party is confirmed by
cross-checking their certificates with the signing CA and establishing trust.

In its default configuration, HTCondor-CE uses GSI-based authentication and authorization to verify the certificate
chain, which will work with technologies such as LCMAPS or Argus.
Additionally, it can be reconfigured to provide alternate authentication mechanisms such as token, Kerberos, SSL, shared
secret, or even IP-based authentication.
More information about authorization methods can be found
[here](https://htcondor.readthedocs.io/en/stable/admin-manual/security.html#authentication).

Getting Help
------------

If you have any questions about the architecture of HTCondor-CE, please [contact us](/#contact-us) for assistance.
