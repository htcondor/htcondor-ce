Reference
=========

Configuration
-------------

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

Users
-----

The following users are needed by HTCondor-CE at all sites:

| User     | Comment                                                                                       |
|:---------|:----------------------------------------------------------------------------------------------|
| `condor` | The HTCondor-CE will be run as root, but perform most of its operations as the `condor` user. |

Certificates
------------

| File             | User that owns certificate | Path to certificate               |
|:-----------------|:---------------------------|:----------------------------------|
| Host certificate | `root`                     | `/etc/grid-security/hostcert.pem` |
| Host key         | `root`                     | `/etc/grid-security/hostkey.pem`  |

Networking
----------

| Service Name | Protocol | Port Number | Inbound | Outbound | Comment                 |
| :----------- | :------: | :---------: | :-----: | :------: | :---------------------- |
| Htcondor-CE  | tcp      | 9619        | X       |          | HTCondor-CE shared port |

Allow inbound and outbound network connection to all internal site servers, such as the batch system head-node. Only
ephemeral outgoing ports are necessary.
