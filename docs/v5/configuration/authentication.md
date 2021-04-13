Configuring Authentication
==========================

To authenticate job submission from external users and VOs, HTCondor-CE can be configured to use a
[built-in mapfile](#built-in-mapfile) or to make [Globus callouts](#globus-callout) to an external service like Argus
or LCMAPS.
The former option is simpler but the latter option may be preferred if your grid supports it or your site already runs
such a service.

Additionally, the HTCondor-CE service uses [X.509 certificates](#configuring-certificates) for SSL and GSI authentication.

Built-in Mapfile
----------------

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
GSI "^<DISTINGUISHED NAME>$" <USERNAME>
```

Replacing `<DISTINGUISHED NAME`> (escaping any '/' with '\/') and `<USERNAME`> with the distinguished name of the
incoming certificate and the unix account under which the job should run, respectively.

VOMS attributes of incoming X.509 proxy certificates can also be used for mapping:

```
GSI "<DISTINGUISHED NAME>,<VOMS FQAN 1>,<VOMS FQAN 2>,...,<VOMSFQAN N>" <USERNAME>
```

Replacing `<DISTINGUISHED NAME`> (escaping any '/' with '\/'), `<VOMSFQAN`> fields, and `<USERNAME`> with the
distinguished name of the incoming certificate, the VOMS roles and groups, and the unix account under which the job
should run, respectively.

Additionally, you can use regular expressions for mapping certificate and VOMS attribute credentials.
For example, to map any certificate from the `GLOW` VO with the `htpc` role to the `glow` user, add the following line:

```
GSI ".*,\/GLOW\/Role=htpc.*" glow
```

!!! warning
    You should only add mappings to the mapfile. Do not remove any of the default mappings:

        GSI "(/CN=[-.A-Za-z0-9/= ]+)" \1@unmapped.htcondor.org
        CLAIMTOBE .* anonymous@claimtobe
        FS (.*) \1

Globus Callout
--------------

To use a Globus callout to a service like LCMAPS or Argus, you will need to have the relevant library installed as well
as the following HTCondor-CE configuration:

1. Add the following line to the top of `/etc/condor-ce/condor_mapfile`:

        GSI (.*) GSS_ASSIST_GRIDMAP

1. Create `/etc/grid-security/gsi-authz.conf` with the following content:

    - For LCMAPS:

            globus_mapping liblcas_lcmaps_gt4_mapping.so lcmaps_callout

    - For Argus:

            globus_mapping /usr/lib64/libgsi_pep_callout.so argus_pep_callout

Configuring Certificates
------------------------

HTCondor-CE uses X.509 host certificates and certificate authorities (CAs) when authenticating SciToken, SSL, and GSI
connections.
By default, HTCondor-CE uses the default system locations to locate CAs and host certificate when authenticating
SciToken and SSL connections.
But traditionally, CEs and their clients have authenticated with each other using specialized grid certificates (e.g.
certificates issued by [IGTF CAs](https://dl.igtf.net/distribution/igtf/current/accredited/accredited.in)) located
in `/etc/grid-security/`.

Choose one of the following options to configure your HTCondor-CE to use grid or system certificates for authentication:

- If your SSL or SciTokens clients will be interacting with your CE using grid certificates or you are using a grid
  certificate as your host certificate:

    1. Set the following configuration in `/etc/condor-ce/config.d/01-ce-auth.conf`:

            AUTH_SSL_SERVER_CERTFILE = /etc/grid-security/hostcert.pem
            AUTH_SSL_SERVER_KEYFILE = /etc/grid-security/hostkey.pem
            AUTH_SSL_SERVER_CADIR = /etc/grid-security/certificates
            AUTH_SSL_SERVER_CAFILE =
            AUTH_SSL_CLIENT_CERTFILE = /etc/grid-security/hostcert.pem
            AUTH_SSL_CLIENT_KEYFILE = /etc/grid-security/hostkey.pem
            AUTH_SSL_CLIENT_CADIR = /etc/grid-security/certificates
            AUTH_SSL_CLIENT_CAFILE =

    1. Install your host certificate and key into `/etc/grid-security/hostcert.pem` and `/etc/grid-security/hostkey.pem`,
       respectively

    1. Set the ownership and Unix permissions of the host certificate and key

            :::console
            root@host # chown root:root /etc/grid-security/hostcert.pem /etc/grid-security/hostkey.pem
            root@host # chmod 644 /etc/grid-security/hostcert.pem
            root@host # chmod 600 /etc/grid-security/hostkey.pem

- Otherwise, use the default system locations:

    1. Install your host certificate and key into `/etc/pki/tls/certs/localhost.crt` and
       `/etc/pki/tls/private/localhost.key`, respectively

    1. Set the ownership and Unix permissions of the host certificate and key

            :::console
            root@host # chown root:root /etc/pki/tls/certs/localhost.crt /etc/pki/tls/private/localhost.key
            root@host # chmod 644 /etc/pki/tls/certs/localhost.crt
            root@host # chmod 600 /etc/pki/tls/private/localhost.key

Next Steps
----------

At this point, you should have an HTCondor-CE that will take credentials from incoming jobs and map them to local Unix
accounts.
The next step is to [configure the CE for your local batch system](../configuration/local-batch-system.md) so that
HTCondor-CE knows where to route your jobs.

