
Testing Use of SciTokens with HTCondor-CE
=========================================

(SciTokens)[https://scitokens.org] provide an alternate authorization mechanism to access
the HTCondor-CE beyond the legacy GSI authentication.  This document aims to provide
developers with the background knowledge necessary to generate a SciToken and use it to
access a test CE.

First, to test SciTokens, you need the prerequisite software:
- HTCondor 8.9.2 or later _with_ SciTokens enabled.  SciTokens support is not enabled
  by default when compiling HTCondor 8.9.2 and not enabled in the shipped build from
  the HTCondor team; it is available from OSG.
- A pre-release build of the HTCondor-CE 4.0.0 (or later).  This is also available from
  the OSG team.

Authorizing an Issuer
=====================

Each SciToken is signed by a specific "issuer" (in the SciTokens model, there is an
issuer per VO).  Unlike a VO in the VOMS model, the issuer is identified by a URL.

Each SciToken issuer must be mapped to a local account on the CE that corresponds
to the Unix identity for that issuer.  At the top of the `/etc/condor-ce/condor_mapfile`,
add a line along the following:

```
SCITOKENS https://demo.scitokens.org demo@users.htcondor.org
```

This maps the demo issuer (`https://demo.scitokens.org`) to the Unix account `demo`.

Creating an appropriate "demo" SciToken
=======================================

The example application at https://demo.scitokens.org can be used to auto-generate and
sign a token on request.  This is useful for testing, but the token is otherwise worthless
(as anyone can generate any token).

Edit the payload box (the UI is awkward; copy/paste works better than typing) to include
the following claims in the token:

```
  "scope": "condor:/READ condor:/WRITE condor:/ALLOW",
  "aud": "my-ce.example.com:9619",
  "sub": "condor",
```

The `aud` claim, if set, must match the value of `SCITOKENS_SERVER_AUDIENCE` configuration
variable in the HTCondor-CE configuration.  If the `aud` claim is not set, then the token
will be valid at any CE.

As the authorizations depend only on the scopes set on the token, any value for the subject (`sub`)
is acceptable.

Testing the CE Endpoint
=======================

Download the signed token from the browser and save it to a file such as `/tmp/token`.
Then, one can test the token using the following

```
_condor_SCITOKENS_FILE=/tmp/token condor_ce_trace my-ce.example.com:9619
```

New setups often require some amount of debugging.  A few helpful hints:

- For the schedd itself, set `SCHEDD_DEBUG=D_FULLDEBUG,D_SECURITY` in `/etc/condor-ce/config.d/99-local.conf`
  in order to increase the logging level for security issues.  A `condor_ce_reconfig` is needed
  to make the updated config take hold.  The schedd log is in `/var/log/condor-ce/ScheddLog`.
- For debugging on the client side, set the environment variable `_condor_TOOL_DEBUG=D_FULLDEBUG,D_SECURITY`
  and add the `-debug` flag to the command line tool.
- Switch to using `condor_ce_ping` to debug authentication issues if `condor_ce_trace` fails.

Setup your own SciTokens issuer
===============================

To make a URL a valid SciTokens issuer, three things are needed:

- A webserver capable of serving static files at the URL.
- A list of valid public keys for the issuer
- A "auto-discovery" file describing where to find the public key URL.

We will not cover the webserver step here.


If your issuer is named `https://scitokens.example.com`, then create a file at

```
https://scitokens.example.com/.well-known/openid-configuration
```

with the following contents:

```
{
 "issuer":"https://scitokens.example.com",
 "jwks_uri":"https://scitokens.example.com/oauth2/certs"}
```

The `jwks_uri` key can point to any URL, but will need to be used below.

To create a keypair, first install the `python2-scitokens` RPM from the OSG via yum:

```
yum install python2-scitokens
```

Next, use `scitokens-admin-create-key` to create a new keyfile:

```
scitokens-admin-create-key --create-keys --pem-private > /tmp/test.scitoken.private.pem
scitokens-admin-create-key --private-keyfile /tmp/test.scitoken.private.pem --jwks-private > /tmp/test.scitoken.private.jwks
scitokens-admin-create-key --private-keyfile /tmp/test.scitoken.private.pem --jwks-public > /tmp/test.scitoken.public.jwks
```

Now, copy the public key (`/tmp/test.scitoken.public.jwks`) to the URL specified by `jwks_uri` above
(such as `https://scitokens.example.com/oauth2/certs`).  Note the `kid` claim in the generate public key.  For example, in
the following public key, the `kid` is `b270`:

```
{
    "keys": [
        {
            "alg": "RS256",
            "e": "AQAB",
            "kid": "b270",
            "kty": "RSA",
            "n": "rnX434cLF7I70ckfpi1lbcNSBXhP0fToMw_RaOlE2zER5aFddHnRkBUBQIAgrM29MDYVjJdXJ_9xLwls0Gm6SSz9IWuobT81HOAeoqepLdcJ5EIaSLDBoRmDsfW0h7g_6m6yJ8aIL5vtJPyiTWjrYiv-VyE8AEPEY_-0KRpuwqr9MXIRYj4pPC7ZhXEyjph1ZETdOF215aWr-Zf-KNw6iF3KRrL4t0cdrdX1AvVduBCQ6JIytW6EwNbKlfTTEGGkzes9fbDdjAcO94qoVZD3E5W3CbZrEN23jXW4cdhAEOJbAufcL3Mi7KF294iwzAXfw0LSQwlpUpV4hB4ZLdQ0gw==",
            "use": "sig"
        }
    ]
}
```

With these two files in place, we have a valid SciTokens issuer at `https://scitokens.example.com` and can
use the generated private key to start issuing tokens!

To generate a token, simply use `scitokens-admin-create-token`:

```
scitokens-admin-create-token --kid b270 --keyfile /tmp/test.scitoken.private.pem --issuer https://scitokens.example.com sub=htcondor aud=https://my-ce.example.com 'scope=condor:/READ condor:/WRITE condor:/ALLOW'
```

For the `kid` argument, utilize the `kid` generated above.

This will output an encoded token that should be usable to submit jobs to the HTCondor-CE.
