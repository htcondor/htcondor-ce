Installing an HTCondor-CE Central Collector
===========================================

The HTCondor-CE Central Collector is an information service designed to provide a an overview and descriptions of grid
services.
Based on the
[HTCondorView Server](https://htcondor.readthedocs.io/en/v9_0/admin-manual/setting-up-special-environments.html#configuring-the-htcondorview-server),
the Central Collector accepts [ClassAds](https://htcondor.readthedocs.io/en/v9_0/misc-concepts/classad-mechanism.html)
from site HTCondor-CEs by default but may accept from other services using the
[HTCondor Python Bindings](https://htcondor.readthedocs.io/en/v9_0/apis/python-bindings/index.html).
By distributing configuration to each member site, a central grid team can coordinate the information that site 
HTCondor-CEs should advertise.

Additionally, the the HTCondor-CE View web server may be installed alongside a Central Collector to display pilot job
statistics across its grid, as well as information for each site HTCondor-CE.
For example, the OSG Central Collector can be viewed at <https://collector.opensciencegrid.org>.

Use this page to learn how to install, configure, and run an HTCondor-CE Central Collector as part of your central
operations.

Before Starting
---------------

Before starting the installation process, consider the following points
(consulting [the reference page](../reference.md) as necessary):

-   **User IDs:** If they do not exist already, the installation will create the `condor` Linux user (UID 4716)
-   **SSL certificate:** The HTCondor-CE Central Collector service uses a host certificate and key for SSL
    authentication
-   **DNS entries:** Forward and reverse DNS must resolve for the HTCondor-CE Central Collector host
-   **Network ports:** Site HTCondor-CEs must be able to contact the Central Collector on port 9619 (TCP).
    Additionally, the optional HTCondor-CE View web server should be accessible on port 80 (TCP).

There are some one-time (per host) steps to prepare in advance:

- Ensure the host has a supported operating system (Red Hat Enterprise Linux variant 7)
- Obtain root access to the host
- Prepare the [EPEL](https://fedoraproject.org/wiki/EPEL) and [HTCondor](https://research.cs.wisc.edu/htcondor/yum/) Yum
  repositories
- Install CA certificates and VO data into `/etc/grid-security/certificates` and `/etc/grid-security/vomsdir`,
  respectively

Installing a Central Collector
------------------------------

1.  Clean yum cache:

        ::console
        root@host # yum clean all --enablerepo=*

1.  Update software:

        :::console
        root@host # yum update

    This command will update **all** packages

1.  Install the `fetch-crl` package, available from the EPEL repositories.

        :::console
        root@host # yum install fetch-crl

1.  Install the Central Collector software:

        :::console
        root@host # yum install htcondor-ce-collector

Configuring a Central Collector
-------------------------------

Like a site HTCondor-CE, the Central Collector uses X.509 host certificates and certificate authorities (CAs) when
authenticating SSL connections.
By default, the Central Collector uses the default system locations to locate CAs and host certificate when
authenticating SSL connections, i.e. for SSL authentication methods.
But traditionally, the Central Collector and HTCondor-CEs have authenticated with each other using specialized grid
certificates (e.g. certificates issued by [IGTF CAs](https://dl.igtf.net/distribution/igtf/current/accredited/accredited.in))
located in `/etc/grid-security/`.

Choose one of the following options to configure your Central Collector to use grid or system certificates for
authentication:

-   If your site HTCondor-CEs will be advertising to your Central Collector using grid certificates or you are using a
    grid certificate for your Central Collector's host certificate:

    1.  Set the following configuration in `/etc/condor-ce/config.d/01-ce-auth.conf`:

            AUTH_SSL_SERVER_CERTFILE = /etc/grid-security/hostcert.pem
            AUTH_SSL_SERVER_KEYFILE = /etc/grid-security/hostkey.pem
            AUTH_SSL_SERVER_CADIR = /etc/grid-security/certificates
            AUTH_SSL_SERVER_CAFILE =
            AUTH_SSL_CLIENT_CERTFILE = /etc/grid-security/hostcert.pem
            AUTH_SSL_CLIENT_KEYFILE = /etc/grid-security/hostkey.pem
            AUTH_SSL_CLIENT_CADIR = /etc/grid-security/certificates
            AUTH_SSL_CLIENT_CAFILE =

    1.  Install your host certificate and key into `/etc/grid-security/hostcert.pem` and `/etc/grid-security/hostkey.pem`,
        respectively

    1.  Set the ownership and Unix permissions of the host certificate and key

            :::console
            root@host # chown root:root /etc/grid-security/hostcert.pem /etc/grid-security/hostkey.pem
            root@host # chmod 644 /etc/grid-security/hostcert.pem
            root@host # chmod 600 /etc/grid-security/hostkey.pem

-  Otherwise, use the default system locations:

    1.  Install your host certificate and key into `/etc/pki/tls/certs/localhost.crt` and
        `/etc/pki/tls/private/localhost.key`, respectively

    1.  Set the ownership and Unix permissions of the host certificate and key

            :::console
            root@host # chown root:root /etc/pki/tls/certs/localhost.crt /etc/pki/tls/private/localhost.key
            root@host # chmod 644 /etc/pki/tls/certs/localhost.crt
            root@host # chmod 600 /etc/pki/tls/private/localhost.key

### Optional configuration ###

The following configuration steps are optional and will not be required for all Central Collectors.
If you do not need any of the following special configurations, skip to
[the section on next steps](#distributing-configuration-to-site-htcondor-ces).

#### Banning HTCondor-CEs ####

By default, Central Collectors accept ClassAds from all HTCondor-CEs with a valid and accepted certificate.
If you want to stop accepting ClassAds from a particular HTCondor-CE, add its hostname to `DENY_ADVERTISE_SCHEDD` in
`/etc/condor-ce/config.d/01-ce-collector.conf`.
For example:

```
DENY_ADVERTISE_SCHEDD = $(DENY_ADVERTISE_SCHEDD), misbehaving-ce-1.bad-domain.com, misbehaving-ce-2.bad-domain.com
```

#### Configuring HTCondor-CE View ####

The HTCondor-CE View is an optional web interface to the status of all HTCondor-CEs advertising to your Central
Collector.
To run the HTCondor-CE View, install the appropriate package and set the relevant configuration.

1.  Begin by installing the `htcondor-ce-view` package:

        :::console
        root@host # yum install htcondor-ce-view

1.  Restart the `condor-ce-collector` service

1.  Verify the service by entering your Central Collector's hostname into your web browser

The website is served on port 80 by default.
To change this default, edit the value of `HTCONDORCE_VIEW_PORT` in `/etc/condor-ce/config.d/05-ce-view.conf`.

Distributing Configuration to Site HTCondor-CEs
-----------------------------------------------

To make the Central Collector truly useful, each site HTCondor-CE in your organization will need to configure their
HTCondor-CEs to advertise to your Central Collector(s) along with any custom information that may be of interest.
For example, the OSG provides default configuration to OSG sites through an `osg-ce`
[metapackage](https://docs.fedoraproject.org/en-US/Fedora_Contributor_Documentation/1/html/Software_Collections_Guide/sect-Creating_a_Meta_Package.html)
and configuration tools.
Following the [Filesystem Hierarchy Standard](https://en.wikipedia.org/wiki/Filesystem_Hierarchy_Standard), the
following configuration should be set by HTCondor-CE administrators in `/etc/condor-ce/config.d/` or by packagers in
`/usr/share/condor-ce/config.d/`:

1.  Set `CONDOR_VIEW_HOST` to a comma-separated list of Central Collectors:

        CONDOR_VIEW_HOST = collector.htcondor.org:9619, collector1.htcondor.org:9619, collector2.htcondor.org:9619

1.  Append arbitrary attributes to `SCHEDD_ATTRS` containing custom information in any number of arbitrarily
    configuration attributes:

        ATTR_NAME_1 = value1
        ATTR_NAME_2 = value2
        SCHEDD_ATTRS = $(SCHEDD_ATTRS) ATTR_NAME_1 ATTR_NAME_2

    For example, OSG sites advertise information describing their [OSG Topology](https://topology.opensciencegrid.org)
    registrations, local batch system, and local resourcess:

        OSG_Resource = "local"
        OSG_ResourceGroup = ""
        OSG_BatchSystems = "condor"
        OSG_ResourceCatalog = { \
          [ \
            AllowedVOs = { "osg" }; \
            CPUs = 2; \
            MaxWallTime = 1440; \
            Memory = 10000; \
            Name = "test"; \
            Requirements = TARGET.RequestCPUs <= CPUs && TARGET.RequestMemory <= Memory && member(TARGET.VO, AllowedVOs); \
            Transform = [ set_MaxMemory = RequestMemory; set_xcount = RequestCPUs; ]; \
          ] \
        }
        SCHEDD_ATTRS = $(SCHEDD_ATTRS) OSG_Resource OSG_ResourceGroup OSG_BatchSystems OSG_ResourceCatalog

Verifying a Central Collector
-----------------------------

To verify that you have a working installation of a Central Collector, ensure that all the relevant services are started
and enabled then perform the validation steps below.

### Managing Central Collector services ###

In addition to the Central Collector service itself, there are a number of supporting services in your installation.
The specific services are:

| Software    | Service name                          |
|:------------|:--------------------------------------|
| Fetch CRL   | `fetch-crl-boot` and `fetch-crl-cron` |
| HTCondor-CE | `condor-ce-collector`                 |

Start and enable the services in the order listed and stop them in reverse order.
As a reminder, here are common service commands (all run as `root`):

| To...                                   | On EL7, run the command...                    |
| :-------------------------------------- | :-------------------------------------------- |
| Start a service                         | `systemctl start <SERVICE-NAME>`              |
| Stop a  service                         | `systemctl stop <SERVICE-NAME>`               |
| Enable a service to start on boot       | `systemctl enable <SERVICE-NAME>`             |
| Disable a service from starting on boot | `systemctl disable <SERVICE-NAME>`            |


### Validating a Central Collector ###


Getting Help
------------

If you have any questions or issues with the installation process, please [contact us](../../index.md#contact-us) for assistance.
