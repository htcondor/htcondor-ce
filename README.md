HTCondor-CE
===========

[![Build and test HTCondor-CE RPMs](https://github.com/htcondor/htcondor-ce/actions/workflows/build_and_test_rpms.yml/badge.svg?branch=V5-branch)](https://github.com/htcondor/htcondor-ce/actions/workflows/build_and_test_rpms.yml)

---

A site grid gatekeeper technology based solely on HTCondor components.

This package is simply a thin set of wrappers around HTCondor, allowing you to
run a HTCondor-CE without disrupting a site HTCondor install.

For example, `condor_ce_q` is the HTCondor-CE equivalent to `condor_q` for the
HTCondor-CE processes.  This package took much of its inspiration - and base 
code - from OSGs condor-cron package.

Sites are encouraged to install the sub-package `htcondor-ce-condor` or
`htcondor-ce-pbs`, depending on which batch manager they run.

Download
--------

HTCondor-CE RPMs are available from the following locations:

- HTCondor Yum repositories: https://research.cs.wisc.edu/htcondor/yum/
- OSG Yum repositories: https://opensciencegrid.org/docs/common/yum/

Versioning
----------

At any given time, two versions of HTCondor-CE are maintained, a stable and a development version.
In this repository, the `master` branch contains the latest version of HTCondor-CE (i.e. development) while the `stable`
branch contains the previous version.

- [Development](https://htcondor-ce.readthedocs.io/en/latest/): HTCondor-CE 4
- [Stable](https://htcondor-ce.readthedocs.io/en/stable/): HTCondor-CE 3

Development
-----------

1.  Build the development container:

        $ docker build -t htcondor-ce-dev -f tests/Dockerfile.dev .

    Optionally, specify the following build arguments:

        -  `EL`: CentOS base image to use for the build.
           Accepted values: `8` or `7` (default)
        -  `BUILD_ENV`: specifies the repositories to use for HTCondor/BLAH dependencies.
           Accepted values: `osg` or `uw_build` (default)

2.  Run the container with the following:

        $ docker run -d \
                     --name my-htcondor-ce \
                     -v ${PWD}:/src/htcondor-ce \
                     -p 9619:9619 \
                     -p 8080:80 \
                     htcondor-ce-dev

3.  Make changes to the source, apply them, and reconfigure the CE:

        $ docker exec my-htcondor-ce \
                 /bin/sh -c \
                   "cmake -DCMAKE_INSTALL_PREFIX=/usr -DPYTHON_EXECUTABLE=/usr/bin/python3 && \
                    make install && \
                    condor_ce_restart -fast"
