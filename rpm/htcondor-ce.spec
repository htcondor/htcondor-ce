# Have gitrev be the short hash or branch name if doing a prerelease build
#define gitrev osg

Name: htcondor-ce
Version: 3.2.2
Release: 1%{?gitrev:.%{gitrev}git}%{?dist}
Summary: A framework to run HTCondor as a CE
BuildArch: noarch

Group: Applications/System
License: Apache 2.0
URL: http://github.com/opensciencegrid/htcondor-ce

# _unitdir,_tmpfilesdir not defined on el6 build hosts
%{!?_unitdir: %global _unitdir %{_prefix}/lib/systemd/system}
%{!?_tmpfilesdir: %global _tmpfilesdir %{_prefix}/lib/tmpfiles.d}

# Generated with:
# git archive --prefix=%{name}-%{version}/ v%{version} | gzip > %{name}-%{version}.tar.gz
#
# Pre-release build tarballs should be generated with:
# git archive --prefix=%{name}-%{version}/ %{gitrev} | gzip > %{name}-%{version}-%{gitrev}.tar.gz
#
Source0: %{name}-%{version}%{?gitrev:-%{gitrev}}.tar.gz

BuildRequires: boost-devel
BuildRequires: cmake

# because of https://jira.opensciencegrid.org/browse/SOFTWARE-2816
Requires:  condor >= 8.6.5

# OSG builds of HTCondor-CE use the Globus-lcmaps plugin architecture
# for authz
%if 0%{?osg}
%ifarch %{ix86}
Requires: liblcas_lcmaps_gt4_mapping.so.0
%else
Requires: liblcas_lcmaps_gt4_mapping.so.0()(64bit)
%endif
%endif

# Init script doesn't function without `which` (which is no longer part of RHEL7 base).
Requires: which

# Require the htcondor-ce-client subpackage.  The client provides necessary
# configuration defaults and scripts for the CE itself.
Requires: %{name}-client = %{version}-%{release}

Provides:  %{name}-master = %{version}-%{release}

%if 0%{?rhel} >= 7
Requires(post): systemd
Requires(preun): systemd
%define systemd 1
%else
Requires(post): chkconfig
Requires(preun): chkconfig
# This is for /sbin/service
Requires(preun): initscripts
%define systemd 0
%endif

# We use this utility to setup a custom hostname.
Requires: /usr/bin/unshare

%description
%{summary}

%if ! 0%{?osg}
%package bdii
Group: Applications/Internet
Summary:  GLUE 2.0 infoprovider and CE config for non-OSG sites.

Requires: %{name} = %{version}-%{release}, bdii

%description bdii
%{summary}
%endif

%if ! 0%{?osg}
%package apel
Group: Applications/Internet
Summary: Scripts for writing accounting log files in APEL format, blah (ce) and batch (runtimes)

Requires: %{name} = %{version}-%{release}
Requires: apel-client >= 1.8.0
Requires: apel-parsers >= 1.8.0
Requires: apel-ssm

%description apel
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

%description condor
%{summary}

%package pbs
Group: Applications/System
Summary: Default routes for submission to PBS
Requires: %{name} = %{version}-%{release}

%if 0%{?uw_build}
Requires: /usr/libexec/condor/glite/bin/batch_gahp
%else
Requires: blahp
%endif

%description pbs
%{summary}

%package lsf
Group: Applications/System
Summary: Default routes for submission to LSF
Requires: %{name} = %{version}-%{release}

%if 0%{?uw_build}
Requires: /usr/libexec/condor/glite/bin/batch_gahp
%else
Requires: blahp
%endif

%description lsf
%{summary}

%package sge
Group: Applications/System
Summary: Default routes for submission to SGE
Requires: %{name} = %{version}-%{release}

%if 0%{?uw_build}
Requires: /usr/libexec/condor/glite/bin/batch_gahp
%else
Requires: blahp
%endif

%description sge
%{summary}

%package slurm
Group: Applications/System
Summary: Default routes for submission to Slurm
Requires: %{name} = %{version}-%{release}

%if 0%{?uw_build}
Requires: /usr/libexec/condor/glite/bin/batch_gahp
%else
Requires: blahp
%endif

%description slurm
%{summary}

%package bosco
Group: Applications/System
Summary: Default routes for submission to BOSCO
Requires: %{name} = %{version}-%{release}

%description bosco
%{summary}

%package client
Group: Applications/System
Summary: Client-side tools for submission to HTCondor-CE

# Note the strange requirements (base package is not required!
# Point is to be able to submit jobs without installing the server.
Requires: condor
# voms-proxy-info used by condor_ce_trace
Requires: voms-clients-cpp
%if ! 0%{?uw_build}
Requires: grid-certificates >= 7
%endif

Requires: condor-python

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
%cmake -DHTCONDORCE_VERSION=%{version} -DSTATE_INSTALL_DIR=%{_localstatedir} -DPYTHON_SITELIB=%{python_sitelib}
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT

%if %systemd
rm $RPM_BUILD_ROOT%{_initrddir}/condor-ce{,-collector}
%else
rm $RPM_BUILD_ROOT%{_unitdir}/condor-ce{,-collector}.service
rm $RPM_BUILD_ROOT%{_tmpfilesdir}/condor-ce{,-collector}.conf
%endif

%if 0%{?osg}
rm -rf $RPM_BUILD_ROOT%{_datadir}/condor-ce/htcondor-ce-provider
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/condor/config.d/50-ce-bdii-defaults.conf
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/condor/config.d/99-ce-bdii.conf
rm -f $RPM_BUILD_ROOT%{_datadir}/condor-ce/apel/README.md
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/condor-ce/config.d/50-ce-apel.conf
rm -f $RPM_BUILD_ROOT%{_datadir}/condor-ce/config.d/50-ce-apel-defaults.conf
rm -f $RPM_BUILD_ROOT%{_datadir}/condor-ce/condor_blah.sh
rm -f $RPM_BUILD_ROOT%{_datadir}/condor-ce/condor_batch.sh
%else
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/bdii/gip/provider
mv $RPM_BUILD_ROOT%{_datadir}/condor-ce/htcondor-ce-provider \
   $RPM_BUILD_ROOT%{_localstatedir}/lib/bdii/gip/provider
mkdir -p $RPM_BUILD_ROOT%{_datadir}/condor-ce/apel/
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/condor-ce/apel/
%endif

# Gratia accounting cleanup
%if ! 0%{?osg}
rm -rf ${RPM_BUILD_ROOT%}%{_datadir}/condor-ce/config.d/03-gratia-cleanup.conf
rm -rf ${RPM_BUILD_ROOT%}%{_datadir}/condor-ce/gratia_cleanup.py*
%endif

%if 0%{?uw_build}
# Remove BATCH_GAHP location override
rm -rf ${RPM_BUILD_ROOT%}%{_datadir}/condor-ce/config.d/01-blahp-location.conf

# Remove central collector tools
rm -rf ${RPM_BUILD_ROOT%}%{_bindir}/condor_ce_info_status
rm -rf ${RPM_BUILD_ROOT%}%{python_sitelib}/htcondorce/info_query.py*
rm -rf ${RPM_BUILD_ROOT%}%{_datadir}/condor-ce/config.d/01-ce-info-services-defaults.conf

# Use simplified CERTIFICATE_MAPFILE for UW builds with *htcondor.org domain
# OSG and CERN have entries in the original mapfile/authz for *cern.ch and
# *opensciencegrid.org so we use original config non-UW builds
rm -rf ${RPM_BUILD_ROOT}%{_sysconfdir}/condor-ce/condor_mapfile.osg
rm -rf ${RPM_BUILD_ROOT}%{_sysconfdir}/condor-ce/config.d/01-ce-auth.conf.osg
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/condor-ce/config.d/01-ce-auth-defaults.conf.osg
%else
mv ${RPM_BUILD_ROOT}%{_sysconfdir}/condor-ce/condor_mapfile{.osg,}
mv ${RPM_BUILD_ROOT}%{_sysconfdir}/condor-ce/config.d/01-ce-auth.conf{.osg,}
mv ${RPM_BUILD_ROOT}%{_datadir}/condor-ce/config.d/01-ce-auth-defaults.conf{.osg,}
%endif

install -m 0755 -d -p $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d

%if %systemd
%define add_service() (/bin/systemctl daemon-reload >/dev/null 2>&1 || :)
%define remove_service() (/bin/systemctl stop %1 > /dev/null 2>&1 || :; \
                          /bin/systemctl disable %1 > /dev/null 2>&1 || :)
%define restart_service() (/bin/systemctl condrestart %1 >/dev/null 2>&1 || :)
%else
%define add_service() (/sbin/chkconfig --add %1 || :)
%define remove_service() (/sbin/service %1 stop >/dev/null 2>&1 || :; \
                                       /sbin/chkconfig --del %1 || :)
%define restart_service() (/sbin/service %1 condrestart >/dev/null 2>&1 || :)
%endif

%post
%add_service condor-ce

%post collector
%add_service condor-ce-collector

%preun
if [ $1 -eq 0 ]; then
    %remove_service condor-ce
fi

%preun collector
if [ $1 -eq 0 ]; then
    %remove_service condor-ce-collector
fi

%postun
if [ $1 -ge 1 ]; then
    %restart_service condor-ce
fi

%postun collector
if [ $1 -ge 1 ]; then
    %restart_service condor-ce-collector
fi

%files
%defattr(-,root,root,-)

%if ! 0%{?uw_build}
# TODO: Drop the OSG-blahp config when the OSG and HTCondor blahps are merged
# https://htcondor-wiki.cs.wisc.edu/index.cgi/tktview?tn=5102,86
%{_datadir}/condor-ce/config.d/01-blahp-location.conf
%{_datadir}/condor-ce/config.d/01-ce-info-services-defaults.conf
%endif

%if 0%{?osg}
%{_datadir}/condor-ce/gratia_cleanup.py*
%{_datadir}/condor-ce/config.d/03-gratia-cleanup.conf
%attr(1777,root,root) %dir %{_localstatedir}/lib/gratia/condorce_data
%endif

%{_bindir}/condor_ce_history
%{_bindir}/condor_ce_router_q

%{_datadir}/condor-ce/condor_ce_router_defaults

%if %systemd
%{_unitdir}/condor-ce.service
%{_tmpfilesdir}/condor-ce.conf
%else
%{_initrddir}/condor-ce
%endif

%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-auth.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-router.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/03-managed-fork.conf
%config(noreplace) %{_sysconfdir}/sysconfig/condor-ce

%{_datadir}/condor-ce/config.d/01-ce-auth-defaults.conf
%{_datadir}/condor-ce/config.d/01-ce-audit-payloads-defaults.conf
%{_datadir}/condor-ce/config.d/01-ce-router-defaults.conf
%{_datadir}/condor-ce/config.d/03-managed-fork-defaults.conf
%{_datadir}/condor-ce/config.d/05-ce-health-defaults.conf

%{_datadir}/condor-ce/local-wrapper

%{python_sitelib}/htcondorce/audit_payloads.py*

%{_bindir}/condor_ce_host_network_check

%attr(-,condor,condor) %dir %{_localstatedir}/run/condor-ce
%attr(-,condor,condor) %dir %{_localstatedir}/log/condor-ce
%attr(1777,condor,condor) %dir %{_localstatedir}/log/condor-ce/user
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/spool
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/execute
%attr(-,condor,condor) %dir %{_localstatedir}/lock/condor-ce
%attr(1777,condor,condor) %dir %{_localstatedir}/lock/condor-ce/user

%if ! 0%{?osg}
%files bdii
%attr(0755, ldap, ldap) %{_localstatedir}/lib/bdii/gip/provider/htcondor-ce-provider

%{_sysconfdir}/condor/config.d/50-ce-bdii-defaults.conf
%config(noreplace) %{_sysconfdir}/condor/config.d/99-ce-bdii.conf
%endif


%if ! 0%{?osg}
%files apel
%{_datadir}/condor-ce/apel/README.md
%{_datadir}/condor-ce/condor_blah.sh
%{_datadir}/condor-ce/condor_batch.sh
%{_datadir}/condor-ce/config.d/50-ce-apel-defaults.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/50-ce-apel.conf
%attr(-,root,root) %dir %{_localstatedir}/lib/condor-ce/apel/
%endif

%files view
%defattr(-,root,root,-)

# Web package
%{python_sitelib}/htcondorce/web.py*
%{python_sitelib}/htcondorce/web_utils.py*
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
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/spool/ceview/vos
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/spool/ceview/metrics

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

%files slurm
%defattr(-,root,root,-)

%config(noreplace) %{_sysconfdir}/condor-ce/config.d/02-ce-slurm.conf
%{_datadir}/condor-ce/config.d/02-ce-slurm-defaults.conf

%files bosco
%defattr(-,root,root,-)

%config(noreplace) %{_sysconfdir}/condor-ce/config.d/02-ce-bosco.conf
%{_datadir}/condor-ce/config.d/02-ce-bosco-defaults.conf

%files client

%if ! 0%{?uw_build}
%{_bindir}/condor_ce_info_status
%{python_sitelib}/htcondorce/info_query.py*
%endif

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
%{_datadir}/condor-ce/verify_ce_config.py*

%{_bindir}/condor_ce_config_val
%{_bindir}/condor_ce_hold
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
%{python_sitelib}/htcondorce/tools.py*

%files collector

%{_bindir}/condor_ce_config_generator
%{_datadir}/condor-ce/config.d/01-ce-collector-defaults.conf
%{_datadir}/condor-ce/config.d/01-ce-auth-defaults.conf

%if %systemd
%{_unitdir}/condor-ce-collector.service
%{_tmpfilesdir}/condor-ce-collector.conf
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
* Tue Mar 26 2019 Brian Lin <blin@cs.wisc.edu> - 3.2.2-1
- Make blahp requirement binary package specific (SOFTWARE-3623)
- Added condor_ce_store_cred for PASSWORD authentication
- Use new multi-line syntax configuration syntax (SOFTWARE-3637)
- Update MyOSG URL and queries

* Mon Feb 11 2019 Brian Lin <blin@cs.wisc.edu> - 3.2.1-1
- Explicitly set ALLOW_READ to support HTCondor 8.9 (SOFTWARE-3538)
- Add timeouts to the BDII provider

* Tue Dec 11 2018 Brian Lin <blin@cs.wisc.edu> - 3.2.0-1
- Map certs with VOMS attr before local daemons (SOFTWARE-3489)
- Send CEView keepalives as the condor user (SOFTWARE-3486)

* Tue Sep 11 2018 Mátyás Selmeci <matyas@cs.wisc.edu> - 3.1.4-1
- Fix condor_ce_trace failures caused by transferring /usr/bin/env (SOFTWARE-3387)
- Fix regex for RDIG certs (SOFTWARE-3399)
- Don't require authz check for condor_ce_q (SOFTWARE-3414)

* Mon Aug 13 2018 Brian Lin <blin@cs.wisc.edu> - 3.1.3-1
- Fix condor_ce_info_status using the wrong port for the central collector (SOFTWARE-3381)

* Thu Jun 07 2018 Brian Lin <blin@cs.wisc.edu> - 3.1.2-3
- Ensure that all BDII files exist for the condor repository

* Thu Jun 07 2018 Brian Lin <blin@cs.wisc.edu> - 3.1.2-2
- Build the BDII sub-package for the condor repository

* Wed May 02 2018 Carl Edquist <edquist@cs.wisc.edu> - 3.1.2-1
- Require voms-clients-cpp explicitly (SOFTWARE-3201)
- Add CN -> daemon.opensciencegrid.org mapping (SOFTWARE-3236)

* Fri Apr 06 2018 Brian Lin <blin@cs.wisc.edu> - 3.1.1-1
- Allow InCommon host certs
- Drop vestigal HTCondor-related configuration
- Add documentation for mapping multiple VOMS attributes

* Thu Mar 15 2018 Brian Lin <blin@cs.wisc.edu> - 3.1.0-1
- Removed OSG-specific code and configuration from builds intended for the
  HTCondor repo
- Updated the CERN BDII provider
- Removed packaging necessary for EL5 builds

* Fri Dec 08 2017 Brian Lin <blin@cs.wisc.edu> - 3.0.4-1
- Handle missing 'MyType' attribute in condor 8.7.5

* Wed Dec 06 2017 Brian Lin <blin@cs.wisc.edu> - 3.0.3-1
- Fix condor_ce_ping with IPv6 addresses (SOFTWARE-3030)
- Fix for CEView being killed after 24h (SOFTWARE-2820)
- Import the web_utils library for condor_ce_metric

* Mon Aug 28 2017 Brian Lin <blin@cs.wisc.edu> - 3.0.2-1
- Fix traceback if JOB_ROUTER_ENTRIES not present (SOFTWARE-2814)
- Improve POSIX compatability

* Tue Aug 01 2017 Dave Dykstra <dwd@fnal.gov> - 3.0.1-1
- Fix loss of job audit info when a new job implicitly stopped a previous
  job that was the last one in a master slot (SOFTWARE-2788).

* Thu Jul 27 2017 Dave Dykstra <dwd@fnal.gov> - 3.0.0-1
- Add the audit_payloads function.  This logs the starting and stopping of
  all payloads that were started from pilot systems based on condor.
- Do not hold jobs with expired proxy (SOFTWARE-2803)
- Only warn about configuration if osg-configure is present (SOFTWARE-2805)
- CEView VO tab throws 500 error on inital installation (SOFTWARE-2826)

* Tue Jun 27 2017 Brian Lin <blin@cs.wisc.edu> - 2.2.1-1
- CPU accounting and non-Condor batch system memory request fixes (SOFTWARE-2786, SOFTWARE-2787)
- Disable mail on service restart

* Thu May 25 2017 Brian Lin <blin@cs.wisc.edu> - 2.2.0-1
- Add ability to request whole node jobs (SOFTWARE-2715)
- Fix bugs to pass GLUE2 Validator

* Wed Mar 22 2017 Brian Lin <blin@cs.wisc.edu> - 2.1.5-1
- Do not disable LCMAPS VOMS attribute checking (SOFTWARE-2633)
- Package htcondor-ce-slurm (SOFTWARE-2631)

* Fri Feb 24 2017 Brian Lin <blin@cs.wisc.edu> - 2.1.4-1
- Fix RequestCpus expression (SOFTWARE-2598)

* Wed Feb 22 2017 Derek Weitzel <dweitzel@cse.unl.edu> - 2.1.3-1
- Add JSON attributes for AGIS (SOFTWARE-2591)
- Respect RequestCpus of incoming jobs (SOFTWARE-2598)
- Fix set_attr check in condor_ce_startup (SOFTWARE-2581)

* Tue Dec 24 2016 Brian Lin <blin@cs.wisc.edu> - 2.1.2-1
- condor_ce_info_status: safely handle bad data (SOFTWARE-2185)
- Added Russian Data Intensive Grid certs to condor_mapfile (GOC#31952)

* Wed Nov 23 2016 Brian Lin <blin@cs.wisc.edu> - 2.1.1-1
- Fix hold message for jobs that are not picked up by the job router
  (SOFTWARE-2539)
- Remove TotalSubmitProcs attribute in routed jobs for correct
  condor_q job counts for HTCondor 8.5.x+

* Wed Nov 02 2016 Brian Lin <blin@cs.wisc.edu> - 2.1.0-1
- Overhaul of queue generation in the CE View to support AGIS JSON
  (SOFTWARE-2525)

* Mon Oct 24 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.11-1
- Accept all DaemonCore options in htcondor-ce-view (SOFTWARE-2481)
- Fix incorrect comment in htcondor-ce-pbs template config (SOFTWARE-2476)

* Tue Oct 11 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.10-1
- Fix CE View so that it handles new DaemonCore options in Condor 8.5.7

* Tue Sep 27 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.9-4
- Add conflicts statements so we pseudo-require an condor 8.5.x >= 8.5.7

* Tue Sep 27 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.9-3
- Always reload daemons after package installation
- Drop daemon-reload in postun that is handled in post

* Tue Sep 27 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.9-2
- Fix upgrades so that services are condrestarted instead of a regular restart

* Mon Sep 26 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.9-1
- Install tmpfile config to /usr/lib (SOFTWARE-2444)
- Change 'null' to 'undefined' in the JOB_ROUTER_DEFAULTS (SOFTWARE-2440)
- HTCondor-CE should detect and refuse to start with invalid configs (SOFTWARE-1856)
- Handle unbounded HTCondor-CE accounting dir (SOFTWARE-2090)

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


