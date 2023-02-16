HTCondor-CE
===========

The [HTCondor-CE](#what-is-htcondor-ce) software is a *Compute Entrypoint* (CE) based on [HTCondor](http://htcondor.org) for sites
that are part of a larger computing grid
(e.g. [European Grid Infrastructure](https://www.egi.eu/), [Open Science Grid](https://opensciencegrid.org/)).
As such, HTCondor-CE serves as a "door" for incoming resource allocation requests (RARs) — it handles authorization and
delegation of these requests to a grid site's local batch system.
Supported batch systems include
[Grid Engine](http://www.univa.com/products/),
[HTCondor](http://htcondor.org),
[LSF](https://www.ibm.com/us-en/marketplace/hpc-workload-management),
[PBS Pro](https://www.altair.com/pbs-professional/)/[Torque](https://adaptivecomputing.com/cherry-services/torque-resource-manager/),
and [Slurm](https://slurm.schedmd.com/).

For an introduction to HTCondor-CE, watch our [recorded webinar](https://www.youtube.com/embed/6IWaMbofG7M) from the EGI
Community Webinar Programme:

<iframe width="560" height="315" src="https://www.youtube.com/embed/6IWaMbofG7M" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
</iframe>

What is a Compute Entrypoint?
-----------------------------

A Compute Entrypoint (CE) is the door for remote organizations to submit requests to temporarily allocate local compute
resources.
These resource allocation requests are submitted as **pilot jobs** that create an environment for end-user jobs to match
and ultimately run within the pilot job.
CEs are made up of a thin layer of software that you install on a machine that already has the ability to submit and
manage jobs in your local batch system.

What is HTCondor-CE?
--------------------

HTCondor-CE is a special configuration of the HTCondor software designed as a Compute Entrypoint.
It is configured to use the HTCondor [Job Router daemon](https://htcondor.readthedocs.io/en/v9_0/grid-computing/job-router.html)
to delegate resource allocation requests by transforming and submitting them to the site’s batch system.

Benefits of running the HTCondor-CE:

-   **Scalability:** HTCondor-CE is capable of supporting ~16k concurrent RARs
-   **Debugging tools:** HTCondor-CE offers
    [many tools to help troubleshoot](v6/troubleshooting/troubleshooting.md#htcondor-ce-troubleshooting-tools) issues with RARs
-   **Routing as configuration:** HTCondor-CE’s mechanism to transform and submit RARs is customized via configuration
    variables, which means that customizations will persist across upgrades and will not involve modification of
    software internals to route jobs

Getting HTCondor-CE
-------------------

Learn how to get and install HTCondor-CE through our [documentation](v6/installation/htcondor-ce.md).

Contact Us
----------

HTCondor-CE is developed and maintained by the [Center for High Throughput Computing](http://chtc.cs.wisc.edu/).
If you have questions or issues regarding HTCondor-CE, please see the
[HTCondor support page](https://research.cs.wisc.edu/htcondor/htcondor-support/) for how to contact us.
