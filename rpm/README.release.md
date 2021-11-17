Releasing HTCondor-CE
=====================

HTCondor-CE release and release candidate RPMs can be automatically built upon GitHub release/pre-release:

1.  Update the version number in the [Makefile](../Makefile).
1.  Update the version, release number, and changelog in the [RPM packaging](htcondor-ce.spec).
    Release candidate numbers should be of the form `0.rcA` or `A` where `A` increments for each release candidate or
    packaging change, respectively.
1.  [Draft a new GitHub release](https://github.com/htcondor/htcondor-ce/releases/new) against your target major version
    branch, i.e. `V5-branch`:
    - For production releases, use the tag `vX.Y.Z`, title `HTCondor-CE X.Y.Z`, and copy the RPM changelog entry into
      the description.
      Add links to tickets where appropriate.
    - For release candidates, **make sure to check the pre-release box**, use the tag `vX.Y.Z-0.rcAX` and use the title
      `HTCondor-CE X.Y.Z Release Candidate A`.
1.  The [build and upload RPM CI](https://github.com/htcondor/htcondor-ce/actions/workflows/upload_rpms.yaml) should
    trigger, uploading RPMs to `/var/tmp/ci_deploy/htcondor/` on the CI transfer host.
1.  Speak to the HTCondor release manager and request that the builds are placed in the rc or production Yum
    repositories as appropriate.
