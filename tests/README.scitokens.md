
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
SCITOKENS https://demo.scitokens.org demo@users.opensciencegrid.org
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
```

The `aud` claim, if set, must match the value of `SCITOKENS_SERVER_AUDIENCE` configuration
variable in the HTCondor-CE configuration.  If the `aud` claim is not set, then the token
will be valid at any CE.

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

