Verifying an HTCondor-CE
========================

To verify that you have a working installation of HTCondor-CE, ensure that all the relevant services are started and
enabled then perform the validation steps below.

Managing HTCondor-CE services
-----------------------------

In addition to the HTCondor-CE job gateway service itself, there are a number of supporting services in your installation.
The specific services are:

| Software                     | Service name                                |
|:-----------------------------|:--------------------------------------------|
| Fetch CRL                    | `fetch-crl-boot` and `fetch-crl-cron`       |
| Your batch system            | `condor` or `pbs_server` or …               |
| HTCondor-CE                  | `condor-ce`                                 |
| **(Optional)** APEL uploader | `condor-ce-apel` and `condor-ce-apel.timer` |

Start and enable the services in the order listed and stop them in reverse order.
As a reminder, here are common service commands (all run as `root`):

| To...                                   | On EL7, run the command...                    |
| :-------------------------------------- | :-------------------------------------------- |
| Start a service                         | `systemctl start <SERVICE-NAME>`              |
| Stop a  service                         | `systemctl stop <SERVICE-NAME>`               |
| Enable a service to start on boot       | `systemctl enable <SERVICE-NAME>`             |
| Disable a service from starting on boot | `systemctl disable <SERVICE-NAME>`            |

Validating HTCondor-CE
----------------------

To validate an HTCondor-CE, perform the following steps:

1. Verify that local job submissions complete successfully from the CE host.
   For example, if you have a Slurm cluster, run `sbatch` from the CE and verify that it runs and completes with
   `scontrol` and `sacct`.

1. Verify that all the necessary daemons are running with
   [condor\_ce\_status -any](troubleshooting/troubleshooting.md#condor_ce_status).

1. Verify the CE's network configuration using
   [condor\_ce\_host\_network\_check](troubleshooting/troubleshooting.md#condor_ce_host_network_check).

1. Verify that jobs can complete successfully using
   [condor\_ce\_trace](troubleshooting/troubleshooting.md#condor_ce_trace).

Getting Help
------------

If any of the above validation steps fail, consult the [troubleshooting guide](troubleshooting/troubleshooting.md).
If that still doesn't resolve your issue, please [contact us](../index.md#contact-us) for assistance.
