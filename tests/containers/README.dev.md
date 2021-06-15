HTCondor-CE Development Containers
==================================

Compute Entrypoint
------------------

To spin up an HTCondor-CE for development, you'll want to build and run a test container.
The Compute Entrypoint container image contains an HTCondor-CE that is configured to submit to an HTCondor pool within
the container.

The container starts these services using [Supervisor](http://supervisord.org/), which also sets up a CA, generates a
host certificate/key pair, and VOMS information.
Additionally, a user proxy and demo SciToken are created for the test user.

### Building the container ###

From the root of the git repo, run the following:

```
docker build -t entrypoint -f tests/containers/entrypoint/Dockerfile .
```

You may also specify `--build-arg` for:

- `EL`: CentOS major version (default: `7`)
- `CONDOR_SERIES`: HTCondor release series (default `9.0`)

### Starting the CE ###

```
docker run -d --name dev-ce entrypoint:latest
```

### Using the CE ###

Shell into the container:

```
docker exec -it dev-ce /bin/bash
```

Within the container, submit a GSI test job as the test user:

```
su - testuser
_condor_SEC_CLIENT_AUTHENTICATION_METHODS=GSI condor_ce_trace -d `hostname`
```

Within the container, submit a SciTokens test job as the test user:

```
su - testuser
renew-demo-token.py
_condor_SEC_CLIENT_AUTHENTICATION_METHODS=SCITOKENS _condor_SCITOKENS_FILE=/tmp/bt_u$(id -u testuser) condor_ce_trace -d `hostname`
```

### Cleaning up the CE ###

```
docker stop dev-ce && docker rm dev-ce
```
