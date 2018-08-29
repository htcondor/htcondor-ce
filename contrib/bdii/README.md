HTCondor-CE BDII Provider
=========================

This folder contains the HTCondor-CE [GLUE2] provider for and associated configuration intended for use with an HTCondor
batch system.
Since BDII is not used in the OSG, the `htcondor-ce-bdii` package is excluded from OSG builds.

Usage
-----

To report BDII data, use the following instructions

1. Install `htcondor-ce-bdii` on each of your site's HTCondor-CE's:

        yum install htcondor-ce-bdii

1. Start and enable BDII on only one of your HTCondor-CE's.
   Alternatively, you may install `htcondor-ce-bdii` on a non-CE host running BDII and HTCondor as long as you set the
   following HTCondor configuration:

        HAS_HTCONDOR_CE = False

References
----------

- [BDII releases]((http://gridinfo.web.cern.ch/sys-admins/bdii-releases))
- [Official GLUE2 documentation](https://www.ogf.org/documents/GFD.147.pdf)
- [CERN GLUE2 reference](http://glue20.web.cern.ch/glue20/)
