Operating an HTCondor-CE
========================

To verify that you have a working installation of HTCondor-CE, ensure that all the relevant services are started and
enabled then perform the validation steps below.

Managing HTCondor-CE services
-----------------------------

In addition to the HTCondor-CE job gateway service itself, there are a number of supporting services in your installation.
The specific services are:

| Software                     | Service name                                |
|:-----------------------------|:--------------------------------------------|
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
   [condor\_ce\_status -any](troubleshooting/debugging-tools.md#condor_ce_status).

1. Verify the CE's network configuration using
   [condor\_ce\_host\_network\_check](troubleshooting/debugging-tools.md#condor_ce_host_network_check).

1. Verify that jobs can complete successfully using
   [condor\_ce\_trace](troubleshooting/debugging-tools.md#condor_ce_trace).

Draining an HTCondor-CE
-----------------------

To drain an HTCondor-CE of jobs, perform the following steps:

1. Set `CONDORCE_MAX_JOBS = 0` in `/etc/condor-ce/config.d`

1. Run `condor_ce_reconfig` to apply the configuration change

1. Use `condor_ce_rm` as needed to stop and remove any jobs that should stop running

Once draining is completed, don't forget to restore the value of `CONDORCE_MAX_JOBS` to its previous value
before trying to operate the HTCondor-CE again.

Checking User Authentication
----------------------------

The authentication method for submitting jobs to
an HTCondor-CE is SciTokens.
To see which authentication method and identity were used to submit
a particular job (or modify existing jobs), you can look in
`/var/log/condor-ce/AuditLog`.

If SciTokens authentication was used, you'll see a set of lines like this:

```
10/15/21 17:54:08 (cid:130) (D_AUDIT) Command=QMGMT_WRITE_CMD, peer=<172.17.0.2:37869>
10/15/21 17:54:08 (cid:130) (D_AUDIT) AuthMethod=SCITOKENS, AuthId=https://demo.scitokens.org,htcondor-ce-dev, CondorId=testuser@users.htcondor.org
10/15/21 17:54:08 (cid:130) (D_AUDIT) Submitting new job 2.0
```

Lines pertaining to the same client request will have the same `cid` value.
Lines from different client requests may be interleaved.

Getting Help
------------

If any of the above validation steps fail, consult the [troubleshooting guide](troubleshooting/common-issues.md).
If that still doesn't resolve your issue, please [contact us](../index.md#contact-us) for assistance.
