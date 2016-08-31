# Have gitrev be the short hash or branch name if doing a prerelease build
#define gitrev osg

Name: htcondor-ce
Version: 2.0.8
Release: 2%{?gitrev:.%{gitrev}git}%{?dist}
Summary: A framework to run HTCondor as a CE
BuildArch: noarch

Group: Applications/System
License: Apache 2.0
URL: http://github.com/opensciencegrid/htcondor-ce

# _unitdir not defined on el6 build hosts
%{!?_unitdir: %global _unitdir %{_prefix}/lib/systemd/system}

# Generated with:
# git archive --prefix=%{name}-%{version}/ v%{version} | gzip > %{name}-%{version}.tar.gz
#
# Pre-release build tarballs should be generated with:
# git archive --prefix=%{name}-%{version}/ %{gitrev} | gzip > %{name}-%{version}-%{gitrev}.tar.gz
#
Source0: %{name}-%{version}%{?gitrev:-%{gitrev}}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:  condor >= 8.3.7
# This ought to pull in the HTCondor-CE specific version of the blahp
Requires: blahp

# Init script doesn't function without `which` (which is no longer part of RHEL7 base).
Requires: which

# Require the htcondor-ce-client subpackage.  The client provides necessary
# configuration defaults and scripts for the CE itself.
Requires: %{name}-client = %{version}-%{release}

Obsoletes: condor-ce < 0.5.4
Provides:  condor-ce = %{version}
Provides:  %{name}-master = %{version}-%{release}

%if 0%{?rhel} >= 7
Requires(post): systemd
Requires(preun): systemd
%else
Requires(post): chkconfig
Requires(preun): chkconfig
# This is for /sbin/service
Requires(preun): initscripts
%endif

# On RHEL6 and later, we use this utility to setup a custom hostname.
%if 0%{?rhel} >= 6
Requires: /usr/bin/unshare
%endif

%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%description
%{summary}

%if ! 0%{?osg}
%package bdii
Group: Applications/Internet
Summary:  BDII GLUE1.3/2 infoproviders and CE config for non-OSG sites.

Requires: %{name} = %{version}-%{release}, bdii

%description bdii
%{summary}
%endif

%package view
Group: Applications/Internet
Summary: A Website that will report the current status of the local HTCondor-CE

Requires: %{name}-master = %{version}-%{release}
Requires: python-cherrypy
Requires: python-genshi
Requires: ganglia-gmond
Requires: rrdtool-python

%description view
%{summary}

%package condor
Group: Applications/System
Summary: Default routes for submission to HTCondor

Requires: %{name} = %{version}-%{release}

Obsoletes: condor-ce-condor < 0.5.4
Provides:  condor-ce-condor = %{version}

%description condor
%{summary}

%package pbs
Group: Applications/System
Summary: Default routes for submission to PBS

Requires: %{name} = %{version}-%{release}
Requires: /usr/bin/grid-proxy-init
Requires: /usr/bin/voms-proxy-init

Obsoletes: condor-ce-pbs < 0.5.4
Provides:  condor-ce-pbs = %{version}

%description pbs
%{summary}

%package lsf
Group: Applications/System
Summary: Default routes for submission to LSF

Requires: %{name} = %{version}-%{release}
Requires: /usr/bin/grid-proxy-init
Requires: /usr/bin/voms-proxy-init

Obsoletes: condor-ce-lsf < 0.5.4
Provides:  condor-ce-lsf = %{version}

%description lsf
%{summary}

%package sge
Group: Applications/System
Summary: Default routes for submission to SGE

Requires: %{name} = %{version}-%{release}
Requires: /usr/bin/grid-proxy-init
Requires: /usr/bin/voms-proxy-init

Obsoletes: condor-ce-sge < 0.5.4
Provides:  condor-ce-sge = %{version}

%description sge
%{summary}

%package bosco
Group: Applications/System
Summary: Default routes for submission to BOSCO

Requires: %{name} = %{version}-%{release}
Requires: /usr/bin/grid-proxy-init
Requires: /usr/bin/voms-proxy-init

Provides:  condor-ce-bosco = %{version}

%description bosco
%{summary}

%package client
Group: Applications/System
Summary: Client-side tools for submission to HTCondor-CE

BuildRequires: boost-devel
BuildRequires: cmake

# Note the strange requirements (base package is not required!
# Point is to be able to submit jobs without installing the server.
Requires: condor
Requires: /usr/bin/grid-proxy-init
Requires: /usr/bin/voms-proxy-init
Requires: grid-certificates >= 7

Requires: condor-python

Obsoletes: condor-ce-client < 0.5.4
Provides:  condor-ce-client = %{version}

%description client
%{summary}

%package collector
Group: Applications/System
Summary: Central HTCondor-CE information services collector

Provides: %{name}-master = %{version}-%{release}
Requires: %{name}-client = %{version}-%{release}
Requires: libxml2-python
Conflicts: %{name}

%description collector
%{summary}

%prep
%setup -q

%build
%cmake -DHTCONDORCE_VERSION=%{version} -DCMAKE_INSTALL_LIBDIR=%{_libdir} -DPYTHON_SITELIB=%{python_sitelib}
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT

%if 0%{?rhel} >= 7
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}
install -m 0644 config/condor-ce.service $RPM_BUILD_ROOT/%{_unitdir}/condor-ce.service
install -m 0644 config/condor-ce-collector.service $RPM_BUILD_ROOT/%{_unitdir}/condor-ce-collector.service
rm $RPM_BUILD_ROOT%{_initrddir}/condor-ce{,-collector}
%else
rm $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d/condor-ce{,-collector}.conf
%endif

# Directories necessary for HTCondor-CE files
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/run/condor-ce
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/log/condor-ce
install -m 1777 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/log/condor-ce/user
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/condor-ce
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/condor-ce/spool
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/condor-ce/spool/ceview
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/condor-ce/execute
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lock/condor-ce
install -m 1777 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lock/condor-ce/user
install -m 1777 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/gratia/condorce_data

%if 0%{?osg}
rm -rf $RPM_BUILD_ROOT%{_datadir}/condor-ce/condor_ce_bdii_generate_glue*
rm -f $RPM_BUILD_ROOT%{_datadir}/condor-ce/config.d/06-ce-bdii-defaults.conf
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/condor-ce/config.d/06-ce-bdii.conf
%else
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/bdii/gip/provider
mv $RPM_BUILD_ROOT%{_datadir}/condor-ce/condor_ce_bdii_generate_glue* \
   $RPM_BUILD_ROOT%{_localstatedir}/lib/bdii/gip/provider
%endif

install -m 0755 -d -p $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d

%clean
rm -rf $RPM_BUILD_ROOT

%post
%if 0%{?rhel} >= 7
systemctl enable condor-ce
%else
/sbin/chkconfig --add condor-ce
%endif

%preun
%if 0%{?rhel} >= 7
if [ $1 = 0 ]; then
    systemctl stop condor-ce > /dev/null 2>&1 || :
    systemctl disable condor-ce > /dev/null 2>&1 || :
fi
%else
if [ $1 = 0 ]; then
  /sbin/service condor-ce stop >/dev/null 2>&1 || :
  /sbin/chkconfig --del condor-ce
fi
%endif

%postun
%if 0%{?rhel} >= 7
if [ "$1" -ge "1" ]; then
  systemctl restart condor-ce >/dev/null 2>&1 || :
fi
%else
if [ "$1" -ge "1" ]; then
  /sbin/service condor-ce condrestart >/dev/null 2>&1 || :
fi
%endif

%files
%defattr(-,root,root,-)

%{_bindir}/condor_ce_history
%{_bindir}/condor_ce_router_q

%{_datadir}/condor-ce/condor_ce_router_defaults

%if 0%{?rhel} >= 7
%{_unitdir}/condor-ce.service
%{_sysconfdir}/tmpfiles.d/condor-ce.conf
%else
%{_initrddir}/condor-ce
%endif

%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-auth.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-router.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/03-ce-shared-port.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/03-managed-fork.conf
%config(noreplace) %{_sysconfdir}/sysconfig/condor-ce

%{_datadir}/condor-ce/config.d/01-ce-auth-defaults.conf
%{_datadir}/condor-ce/config.d/01-ce-info-services-defaults.conf
%{_datadir}/condor-ce/config.d/01-ce-router-defaults.conf
%{_datadir}/condor-ce/config.d/03-ce-shared-port-defaults.conf
%{_datadir}/condor-ce/config.d/05-ce-health-defaults.conf
%{_datadir}/condor-ce/config.d/03-managed-fork-defaults.conf

%{_datadir}/condor-ce/osg-wrapper

%{_bindir}/condor_ce_host_network_check

%attr(-,condor,condor) %dir %{_localstatedir}/run/condor-ce
%attr(-,condor,condor) %dir %{_localstatedir}/log/condor-ce
%attr(1777,condor,condor) %dir %{_localstatedir}/log/condor-ce/user
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/spool
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/execute
%attr(-,condor,condor) %dir %{_localstatedir}/lock/condor-ce
%attr(1777,condor,condor) %dir %{_localstatedir}/lock/condor-ce/user
%attr(1777,root,root) %dir %{_localstatedir}/lib/gratia/condorce_data

%if ! 0%{?osg}
%files bdii
%attr(0755, ldap, ldap) %{_localstatedir}/lib/bdii/gip/provider/condor_ce_bdii_generate_glue1.py*
%attr(0755, ldap, ldap) %{_localstatedir}/lib/bdii/gip/provider/condor_ce_bdii_generate_glue2.py*

%{_datadir}/condor-ce/config.d/06-ce-bdii-defaults.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/06-ce-bdii.conf
%endif

%files view
%defattr(-,root,root,-)

# Web package
%{python_sitelib}/htcondorce/web.py*
%{python_sitelib}/htcondorce/rrd.py*

%{_datadir}/condor-ce/templates/index.html
%{_datadir}/condor-ce/templates/vos.html
%{_datadir}/condor-ce/templates/metrics.html
%{_datadir}/condor-ce/templates/health.html
%{_datadir}/condor-ce/templates/header.html
%{_datadir}/condor-ce/templates/pilots.html

%{_datadir}/condor-ce/config.d/05-ce-view-defaults.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/05-ce-view.conf
%config(noreplace) %{_sysconfdir}/condor-ce/metrics.d/00-example-metrics.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/05-ce-health.conf
%dir %{_sysconfdir}/condor-ce/metrics.d
%{_sysconfdir}/condor-ce/metrics.d/00-metrics-defaults.conf

%{_datadir}/condor-ce/condor_ce_view
%{_datadir}/condor-ce/condor_ce_metric
%{_datadir}/condor-ce/condor_ce_jobmetrics

%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/spool/ceview

%files condor
%defattr(-,root,root,-)

%config(noreplace) %{_sysconfdir}/condor-ce/config.d/02-ce-condor.conf
%{_datadir}/condor-ce/config.d/02-ce-condor-defaults.conf
%config(noreplace) %{_sysconfdir}/condor/config.d/99-condor-ce.conf
%{_sysconfdir}/condor/config.d/50-condor-ce-defaults.conf

%files pbs
%defattr(-,root,root,-)

%config(noreplace) %{_sysconfdir}/condor-ce/config.d/02-ce-pbs.conf
%{_datadir}/condor-ce/config.d/02-ce-pbs-defaults.conf

%files lsf
%defattr(-,root,root,-)

%config(noreplace) %{_sysconfdir}/condor-ce/config.d/02-ce-lsf.conf
%{_datadir}/condor-ce/config.d/02-ce-lsf-defaults.conf

%files sge
%defattr(-,root,root,-)

%config(noreplace) %{_sysconfdir}/condor-ce/config.d/02-ce-sge.conf
%{_datadir}/condor-ce/config.d/02-ce-sge-defaults.conf

%files bosco
%defattr(-,root,root,-)

%config(noreplace) %{_sysconfdir}/condor-ce/config.d/02-ce-bosco.conf
%{_datadir}/condor-ce/config.d/02-ce-bosco-defaults.conf

%files client

%dir %{_sysconfdir}/condor-ce
%dir %{_sysconfdir}/condor-ce/config.d
%config %{_sysconfdir}/condor-ce/condor_config
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-common-auth.conf
%{_datadir}/condor-ce/config.d/01-common-auth-defaults.conf
%{_datadir}/condor-ce/config.d/01-common-collector-defaults.conf
%{_datadir}/condor-ce/ce-status.cpf
%{_datadir}/condor-ce/pilot-status.cpf
%config(noreplace) %{_sysconfdir}/condor-ce/condor_mapfile

%{_datadir}/condor-ce/condor_ce_env_bootstrap
%{_datadir}/condor-ce/condor_ce_client_env_bootstrap
%{_datadir}/condor-ce/condor_ce_startup
%{_datadir}/condor-ce/condor_ce_startup_internal

%{_bindir}/condor_ce_config_val
%{_bindir}/condor_ce_hold
%{_bindir}/condor_ce_info_status
%{_bindir}/condor_ce_job_router_info
%{_bindir}/condor_ce_off
%{_bindir}/condor_ce_on
%{_bindir}/condor_ce_q
%{_bindir}/condor_ce_qedit
%{_bindir}/condor_ce_restart
%{_bindir}/condor_ce_rm
%{_bindir}/condor_ce_run
%{_bindir}/condor_ce_release
%{_bindir}/condor_ce_submit
%{_bindir}/condor_ce_reconfig
%{_bindir}/condor_ce_reschedule
%{_bindir}/condor_ce_status
%{_bindir}/condor_ce_version
%{_bindir}/condor_ce_trace
%{_bindir}/condor_ce_ping

%dir %{python_sitelib}/htcondorce
%{python_sitelib}/htcondorce/__init__.py*
%{python_sitelib}/htcondorce/info_query.py*
%{python_sitelib}/htcondorce/tools.py*

%files collector

%{_bindir}/condor_ce_config_generator
%{_datadir}/condor-ce/config.d/01-ce-collector-defaults.conf
%{_datadir}/condor-ce/config.d/01-ce-auth-defaults.conf

%if 0%{?rhel} >= 7
%{_unitdir}/condor-ce-collector.service
%{_sysconfdir}/tmpfiles.d/condor-ce-collector.conf
%else
%{_initrddir}/condor-ce-collector
%endif

%config(noreplace) %{_sysconfdir}/sysconfig/condor-ce-collector
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-collector.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-collector-requirements.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-auth.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/02-ce-auth-generated.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/04-ce-collector-auth.conf
%config(noreplace) %{_sysconfdir}/cron.d/condor-ce-collector-generator.cron
%config(noreplace) %{_sysconfdir}/logrotate.d/condor-ce-collector

%attr(-,condor,condor) %dir %{_localstatedir}/run/condor-ce
%attr(-,condor,condor) %dir %{_localstatedir}/log/condor-ce
%attr(1777,condor,condor) %dir %{_localstatedir}/log/condor-ce/user
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/spool
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/execute
%attr(-,condor,condor) %dir %{_localstatedir}/lock/condor-ce
%attr(1777,condor,condor) %dir %{_localstatedir}/lock/condor-ce/user
%attr(1777,root,root) %dir %{_localstatedir}/lib/gratia/condorce_data

%changelog
* Wed Aug 29 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.8-2
- Fix EL7 cleanup on uninstall

* Mon Aug 29 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.8-1
- Remove the HTCondor-CE init script on EL7 (SOFTWARE-2419)
- Fix OnExitHold to be set to expressions rather than their evaluated forms
- Force 'condor_ce_q -allusers' until QUEUE_SUPER_USER is fixed to be able to use CERTIFICATE_MAPFILE in 8.5.6
- Allow mapping of Terana eScience hostcerts
- Ensure lockdir and rundir exist with correct permissions on startup

* Thu Jun 23 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.7-1
- Add a default route for a BOSCO CE (SOFTWARE-2370)

* Wed May 25 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.6-1
- Fix condor_ce_trace timeout exit code
- Print condor_ce_trace exceptions when -debug is specified
- Accept submit attribute format, '+AttributeName', in condor_ce_trace

* Tue Apr 26 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.5-1
- HTCondor-CE-CEView update to add Schedd (SOFTWARE-2268)
- Remove extraneous copies of pbs_status.py (SOFTWARE-2279)
- Add BR ANESP hostcert (https://ticket.opensciencegrid.org/29196)
- Unit tests for condor_ce_router_defaults accounting groups
- Add yum clean commands before Travis-CI tests
- Fix incorrect paths and empty job attr in the CE View

* Thu Mar 31 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.4-1
- Bug fix for extraneous parens when using uid_table.txt (SOFTWARE-2243)

* Mon Mar 28 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.3-1
- Drop arch requirements
- Accept subject DNs in extattr_table.txt (SOFTWARE-2243)

* Fri Feb 22 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.2-1
- Drop CE ClassAd functions from JOB_ROUTER_DEFAULTS

* Wed Feb 07 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.1-1
- Fix htcondor-ce-view requirements to allow installation with an htcondor-ce-collector
- Drop CE ClassAd functions

* Fri Jan 22 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.0-2
- Require condor >= 8.3.7, which provides the userHome ClassAd function

* Tue Dec 15 2015 Brian Lin <blin@cs.wisc.edu> - 2.0.0-1
- Added a web monitor: htcondor-ce-view
- Added BDII providers for non-OSG sites
- Improved formatting for condor_ce_status

* Thu Nov 12 2015 Brian Lin <blin@cs.wisc.edu> - 1.20-2
- Rebuild against condor-8.4.0 in case we are not satisfied with 8.4.2

* Wed Nov 11 2015 Carl Edquist <edquist@cs.wisc.edu> - 1.20-1
- Enable GSI map caching to decrease the number of GSI callouts (SOFTWARE-2105)
- Allow authenticated, mapped users to advertise glideins
- Build against condor 8.4.2 (SOFTWARE-2084)

* Fri Nov 06 2015 Brian Lin <blin@cs.wisc.edu> - 1.19-1
- Fix a bug in setting HTCondor accounting groups for routed jobs (SOFTWARE-2076)

* Mon Nov 2 2015 Edgar Fajardo <emfajard@ucsd.edu> - 1.18-2
- Build against condor 8.4.0 (SOFTWARE-2084)

* Tue Oct 27 2015 Jeff Dost <jdost@ucsd.edu> - 1.18-1
- Fix a bug that prevented HTCondor-CE from starting when UID or extattr mappings were not used
- Allow users to append lines to JOB_ROUTER_DEFAULTS (SOFTWARE-2065)
- Allow users to add onto accounting group defaults set by the job router (SOFTWARE-2067)
- build against condor 8.4.1 (SOFTWARE-2084)

* Mon Sep 25 2015 Brian Lin <blin@cs.wisc.edu> - 1.16-1
- Add network troubleshooting tool (condor_ce_host_network_check)
- Add ability to disable glideins advertising to the CE
- Add non-DigiCert hostcerts for CERN
- Improvements to 'condor_ce_run' error messages

* Mon Aug 31 2015 Carl Edquist <edquist@cs.wisc.edu> - 1.15-2
- bump release to rebuild against condor 8.3.8 (SOFTWARE-1995)

* Fri Aug 21 2015 Brian Lin <blin@cs.wisc.edu> 1.15-1
- Add 'default_remote_cerequirements' attribute to the JOB_ROUTER_DEFAULTS
- Verify the first route in JOB_ROUTER_ENTRIES in the init script
- htcondor-ce-collecotr now uses /etc/sysconfig/condor-ce-collector for additional configuration

* Mon Jul 20 2015 Mátyás Selmeci <matyas@cs.wisc.edu> 1.14-4
- bump to rebuild

* Wed Jul 01 2015 Mátyás Selmeci <matyas@cs.wisc.edu> 1.14-3
- Require grid-certificates >= 7 (SOFTWARE-1883)

* Tue Jun 30 2015 Brian Lin <blin@cs.wisc.edu> - 1.14-2
- Authorization fix when running condor_ce_run without '-r' (SOFTWARE-1910)

* Wed Jun 24 2015 Brian Lin <blin@cs.wisc.edu> - 1.14-1
- CE Collector should accept all CEs (SOFTWARE-1790)
- Do not utilize the CE config when submitting a job with condor_ce_run without the -r option (SOFTWARE-1910)
- Verify value of QUEUE_SUPER_USER_MAY_IMPERSONATE for HTCondor batch systems (SOFTWARE-1943)
- Ensure that the HTCondor Python bindings are in the PYTHONPATH (SOFTWARE-1927)
- HTCondor CE should warn if osg-configure has not been run (SOFTWARE-1914)
- Improvements to condor_ce_run error messages
- Drop userHome function since it's included in upstream HTCondor 8.3.6

* Fri Jun 19 2015 Mátyás Selmeci <matyas@cs.wisc.edu> 1.13-3
- Add basic systemd service files for condor-ce and condor-ce-collector (SOFTWARE-1541)
- Fix name and description in the LSB lines in the init scripts

* Mon Apr 27 2015 Brian Lin <blin@cs.wisc.edu> - 1.13-1
- Fix bug that prevented HTCondor CE service from starting with multiple job routes

* Mon Apr 27 2015 Brian Lin <blin@cs.wisc.edu> - 1.12-1
- Add ability to constrain via arbitrary ClassAd expression in condor_ce_info_status (SOFTWARE-1842)
- condor_ce_run now accepts extra attributes via file (SOFTWARE-1641)
- Support for dynamic assignment of OSG env variables (SOFTWARE-1862)
- Catch socket exceptions in condor_ce_trace (SOFTWARE-1821)
- Add support for CILogon certificates
- Fix gridmanager job limit configuration

* Mon Mar 30 2015 Brian Lin <blin@cs.wisc.edu> - 1.11-1
- Add code for generating submit file additions (SOFTWARE-1760)
- Bug fix for matching pilot DN's

* Mon Feb 23 2015 Brian Lin <blin@cs.wisc.edu> - 1.10-1
- Add dry-run option to condor_ce_run (SOFTWARE-1787)
- Add minWalltime attribute
- Allow the collector to accept startd ads from worker nodes
- Advertise the collector's address in the job environment
- Fix --vo broken if missing in condor_ce_info_status (SOFTWARE-1782)
- Fix cleanup bug in condor_ce_run

* Mon Jan 26 2015 Brian Lin <blin@cs.wisc.edu> - 1.9-3
- Improvements to error handling and environment verification of condor_ce_trace
- Change the name of the job router diagnostic tool to condor_ce_job_router_info

* Tue Jan 06 2015 Brian Lin <blin@cs.wisc.edu> - 1.9-2
- Fix HTCondor jobs routing incorrectly in 8.3.x

* Thu Dec 18 2014 Brian Lin <blin@cs.wisc.edu> - 1.9-1
- Add auth file to the collector RPM.
- Updates and fixes to condor_ce_info_status and condor_ce_trace
- Fixes to default security settings

* Thu Dec 04 2014 Mátyás Selmeci <matyas@cs.wisc.edu> 1.8-5
- Add a user-friendly error message when condor_ce_reconfig fails in condor_ce_config_generator (SOFTWARE-1705)

* Mon Dec 01 2014 Mátyás Selmeci <matyas@cs.wisc.edu> 1.8-4
- Fix help message code so it is Python 2.4 compatible

* Mon Nov 24 2014 Brian Lin <blin@cs.wisc.edu> - 1.8-3
- Nest try/except/finally for python 2.4 compatability

* Mon Nov 24 2014 Brian Lin <blin@cs.wisc.edu> - 1.8-2
- Fix configuration issue preventing htcondor-ce startup

* Sun Nov 23 2014 Brian Bockelman <bbockelm@cse.unl.edu> - 1.8-1
- Initial v1.8 release.
- On newer HTCondor versions, have the collector and shared_port
  use the same TCP port (SOFTWARE-1696).
- Add tools for querying the central collector and parsing the
  results (akin to condor_status for OSG). (SOFTWARE-1669, 1692, 1688)
- Improve usability and usefulness of condor_ce_trace (SOFTWARE-1678, 1679)
- Update the central collector with TCP instead of UDP (SOFTWARE-1676)
- Set GRIDMANAGER_MAX_SUBMITTED_JOBS_PER_RESOURCE by default.

* Tue Oct 28 2014 Mátyás Selmeci <matyas@cs.wisc.edu> 1.7-1
- Rename logrotate file for GeneratorLog (SOFTWARE-1642)
- Set cronjob frequency back to original (SOFTWARE-1643)
- Decrease logging verbosity at default level (SOFTWARE-1650)

* Mon Oct 27 2014 Matyas Selmeci <matyas@cs.wisc.edu> 1.6.1-1
- Rebuild with condor-8.2

* Thu Oct 23 2014 Mátyás Selmeci <matyas@cs.wisc.edu> 1.6-4
- Add logrotate file for GeneratorLog (made by condor_ce_config_generator) (SOFTWARE-1642)
- Fix failure with condor_ce_config_generator calling condor_ce_reconfig in cron (SOFTWARE-1643)
- Decrease condor_ce_config_generator cronjob frequency (SOFTWARE-1643)

* Fri Oct 03 2014 Mátyás Selmeci <matyas@cs.wisc.edu> 1.6-3
- Fix condor_ce_generator rename issue in collector cron job and init script (SOFTWARE-1621)

* Tue Sep 30 2014 Mátyás Selmeci <matyas@cs.wisc.edu> 1.6-2
- Add grid-certificates virtual dependency
- Add CONDOR_VIEW_CLASSAD_TYPES setting (SOFTWARE-1616)
- Add LastCEConfigGenerateTime to COLLECTOR_ATTRS to include it in the collector classad
- Add implementation of htcondor.param.git (if missing)
- Add config last gen time as an attribute (LastCEConfigGenerateTime)
- collector subpackage also owns dirs under /var/log
- Rename condor_ce_generator to condor_ce_config_generator and improve config file text

* Mon Sep 29 2014 Brian Lin <blin@cs.wisc.edu> - 1.6-1
- Allow sysadmins to set a custom hostname.
- Advertise the HTCondor-CE version in the ClassAd.
- Add condor_ce_job_router_tool

* Thu Sep 04 2014 Brian Lin <blin@cs.wisc.edu> - 1.5.1-1
- Fix idle jobs getting held even if they have a matching route

* Wed Sep 03 2014 Brian Bockelman <bbockelm@cse.unl.edu> - 1.6-1
- Allow sysadmins to set a custom hostname.
- Advertise the HTCondor-CE version in the ClassAd.

* Mon Aug 25 2014 Brian Lin <blin@cs.wisc.edu> - 1.5-1
- Add workaround to fix client tool segfault with mismatched ClassAd versions
  between HTCondor CE and Condor (SOFTWARE-1583)
- Fix condor_ce_trace so it can accept requirements attributes

* Tue Jul 29 2014 Brian Lin <blin@cs.wisc.edu> - 1.4-1
- Add default for $HOME in job environment
- Fix condor_ce_run bug that lost any predefinied environmental variables
- Limit the number of local and scheduler universe jobs
- Add option to condor_ce_run to more easily run local jobs

* Fri Jul 18 2014 Brian Lin <blin@cs.wisc.edu> - 1.3-1
- Fix bug that prevented HTCondor-CE from starting if running HTCondor > 8.0.x
- Hold then remove jobs that don't match any job router entries
- Enable special ClassAd attributes set by GlideinWMS Factories

* Mon Jun 30 2014 Brian Lin <blin@cs.wisc.edu> - 1.2-1
- Fix bug where condor-ce wouldn't start

* Tue Jun 17 2014 Brian Lin <blin@cs.wisc.edu> - 1.1-1
- Allow users to add ClassAd attr in condor_ce_trace
- Add LSF and SGE job routes
- Remove jobs that have been held longer than 24 hr
- Don't set AccountingGroup when missing UID/extattr table

* Sun Apr 27 2014 Brian Lin <blin@cs.wisc.edu> - 1.0-1
- Add condor specific config files

* Tue Mar 04 2014 Brian Bockelman <bbockelm@cse.unl.edu> - 0.6.3-1
- Do not use InputRSL unless we have an appropriate version of HTCondor.
- Further tighten security defaults
- Make a copy of all config files in /usr/share
- Strip leading and trailing whitespaces from classad values

* Wed Feb 12 2014 Brian Bockelman <bbockelm@cse.unl.edu> - 0.6.2-1
- Fix attribute names to be more compatible with glideinWMS's preferred usage.
- Wall time, memory, and CPU count are now passed through to PBS correctly.
- Remove PeriodicRemove inserted by HTCondor-G.

* Fri Jan 31 2014 Brian Bockelman <bbockelm@cse.unl.edu> - 0.6.1-2
- Rebuild for HCC.

* Fri Jan 31 2014 Brian Bockelman <bbockelm@cse.unl.edu> - 0.6.1-1
- Fix issue with older classads library.

* Sat Jan 11 2014 Brian Bockelman <bbockelm@cse.unl.edu> - 0.6.0-1
- Add compatibility layer with GlobusRSL.  This allows GlobusRSL set
  for HTCondor-G for GRAM to be reused by HTCondor-CE.

* Mon Jan 06 2014 Brian Bockelman <bbockelm@cse.unl.edu> - 0.5.9-1
- Add support for OSG extended attribute and UID tables.
- Small config fixes for RHEL6's OpenSSL and the PBS backend.

* Thu Aug 22 2013 Brian Bockelman <bbockelm@cse.unl.edu> - 0.5.8-1
- Fix runtime environment for local universe jobs.

* Wed Aug 21 2013 Brian Bockelman <bbockelm@cse.unl.edu> - 0.5.7-1
- Addition of condor_ce_ping
- Fix condor_ce_trace script; it was using condor_ping from the base condor config.
- Re-organize auth configs so the client RPM could include the bootstrap.
- A modest amount of Condor->HTCondor renaming in the configs.

* Mon Aug 19 2013 Brian Lin <blin@cs.wisc.edu> - 0.5.6-3
- Fixed incompatibility with the UW Condor RPM and empty-condor
- Make separate builds for different architectures

* Wed Aug 14 2013 Brian Lin <blin@cs.wisc.edu> - 0.5.6-2
- Add condor-python requirement to htcondor-ce-client

* Sat May 04 2013 Brian Bockelman <bbockelm@cse.unl.edu> - 0.5.6-1
- Improve hold reason error message.
- Enable HTCondor audit log by default. 

* Mon Apr 29 2013 Brian Bockelman <bbockelm@cse.unl.edu> - 0.5.5-1
- Add condor_ce_trace for debugging a CE.
- Update environment bootstrap to match OSG's globus-gatekeeper.

* Thu Dec 13 2012 Brian Bockelman <bbockelm@cse.unl.edu> - 0.5.4-1
- Add DigiCert-CA-issued mapping in the default condor_mapfile
- Add requirement for HTCondor > 7.9.2
- Make shared-port default.

* Wed Dec 12 2012 Brian Bockelman <bbockelm@cse.unl.edu> - 0.5.3-1
- Implement the condor_ce_run helper utility.
- Split out client tools subpackage.

* Sat Jul 07 2012 Brian Bockelman <bbockelm@cse.unl.edu> - 0.5.2-1
- A second try at fixing the periodic hold expression.

* Fri Jul 06 2012 Brian Bockelman <bbockelm@cse.unl.edu> - 0.5.1-1
- Fix incorrect attribute name in the periodic hold expression.

* Tue Jun 19 2012 Brian Bockelman <bbockelm@cse.unl.edu> - 0.5-1
- Fix RPM deps and some small pbs_status tweaks.

* Thu Jun 14 2012 Brian Bockelman <bbockelm@cse.unl.edu> - 0.4-1
- Tweak default route settings from limits hit in the scalability tests.
- Add support for RSV.

* Mon Jun 04 2012 Brian Bockelman <bbockelm@cse.unl.edu> - 0.3-1
- Add support for Gratia.

* Thu May 31 2012 Brian Bockelman <bbockelm@cse.unl.edu> - 0.2-1
- Release after a day of testing with PBS and HTCondor.


