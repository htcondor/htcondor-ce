HTCondor-CE BDII Provider
=========================

This folder contains the HTCondor-CE [GLUE2](https://www.ogf.org/documents/GFD.147.pdf) provider for HTCondor-CE and
associated configuration intended for use with an HTCondor batch system.
This provider works by contacting the site's local HTCondor's central manager to discover each HTCondor-CE at a site.
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
