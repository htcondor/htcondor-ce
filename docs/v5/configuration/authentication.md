Configuring Authentication
==========================

To authenticate job submission from external users and VOs, HTCondor-CE can be configured to use
[built-in mapfiles](#built-in-mapfiles) or to make [Globus callouts](#globus-callout) to an external service like Argus
or LCMAPS.
The former option is simpler but the latter option may be preferred if your grid supports it or your site already runs
such a service.

Additionally, the HTCondor-CE service uses [X.509 certificates](#configuring-certificates) for SciTokens, SSL, and GSI
authentication.

Built-in Mapfiles
----------------

HTCondor-CE uses
[unified HTCondor mapfiles](https://htcondor.readthedocs.io/en/v9_0/admin-manual/security.html#the-unified-map-file-for-authentication)
stored in `/etc/condor-ce/mapfiles.d/*.conf` to map incoming jobs with credentials to local Unix accounts.
These files are parsed in lexicographic order and HTCondor-CE will use the first line that matches for the
authentication method that the client and your HTCondor-CE negotiates.
Each mapfile line consists of three fields:

1.  HTCondor authentication method
1.  Incoming credential principal formatted as a Perl Compatible Regular Expression (PCRE)
1.  Local account


### SciTokens ###

To allow clients with SciToken or WLCG tokens to submit jobs to your HTCondor-CE, add lines of the following format:

```
SCITOKENS /<TOKEN ISSUER>,<TOKEN SUBJECT>/ <USERNAME>
```

Replacing `<TOKEN ISSUER>` (escaping any `/` with `\/`, `<TOKEN SUBJECT>`, and `<USERNAME>` with the token issuer
(`iss`), token subject (`sub`), and the unix account under which the job should run, respectively.
For example, to map any token from the `OSG` VO regardless of the token `sub`, add the following line to a `*.conf` file
in `/etc/condor-ce/mapfiles.d/`:

```
SCITOKENS /^https:\/\/scitokens.org\/osg-connect,.*/ osg
```

### GSI ###

To allow clients with GSI proxies with to submit jobs to your HTCondor-CE, add lines of the following format:

```
GSI /^<DISTINGUISHED NAME>$/ <USERNAME>
```

Replacing `<DISTINGUISHED NAME>` (escaping any `/` with `\/`) and `<USERNAME>` with the distinguished name of the
incoming certificate and the unix account under which the job should run, respectively.
VOMS attributes of incoming X.509 proxy certificates can also be used for mapping:

```
GSI /<DISTINGUISHED NAME>,<VOMS FQAN 1>,<VOMS FQAN 2>,...,<VOMSFQAN N>/ <USERNAME>
```

Replacing `<DISTINGUISHED NAME>` (escaping any `/` with `\/`), `<VOMSFQAN>` fields, and `<USERNAME>` with the
distinguished name of the incoming certificate, the VOMS roles and groups, and the unix account under which the job
should run, respectively.
For example, to map any certificate from the `GLOW` VO with the `htpc` role to the `glow` user, add the following line
to a `*.conf` file in `/etc/condor-ce/mapfiles.d/`:

```
GSI /.*,\/GLOW\/Role=htpc.*/ glow
```

Globus Callout
--------------

To use a Globus callout to a service like LCMAPS or Argus, you will need to have the relevant library installed as well
as the following HTCondor-CE configuration:

1. Add the following line to the top of `/etc/condor-ce/condor_mapfile`:

        GSI /(.*)/ GSS_ASSIST_GRIDMAP

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

