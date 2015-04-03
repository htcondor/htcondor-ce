# Have gitrev be the short hash or branch name if doing a prerelease build
#define gitrev osg

Name: htcondor-ce
Version: 1.11
Release: 1%{?gitrev:.%{gitrev}git}%{?dist}
Summary: A framework to run HTCondor as a CE

Group: Applications/System
License: Apache 2.0
URL: http://github.com/bbockelm/condor-ce

# Generated with:
# git archive --prefix=%{name}-%{version}/ v%{version} | gzip > %{name}-%{version}.tar.gz
#
# Pre-release build tarballs should be generated with:
# git archive --prefix=%{name}-%{version}/ %{gitrev} | gzip > %{name}-%{version}-%{gitrev}.tar.gz
#
Source0: %{name}-%{version}%{?gitrev:-%{gitrev}}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:  condor >= 8.0.0
# This ought to pull in the HTCondor-CE specific version of the blahp
Requires: blahp

# Require the htcondor-ce-client subpackage.  The client provides necessary
# configuration defaults and scripts for the CE itself.
Requires: %{name}-client = %{version}-%{release}

Obsoletes: condor-ce < 0.5.4
Provides:  condor-ce = %{version}

Requires(post): chkconfig
Requires(preun): chkconfig
# This is for /sbin/service
Requires(preun): initscripts

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

%package client
Group: Applications/System
Summary: Client-side tools for submission to HTCondor-CE

BuildRequires: boost-devel
BuildRequires: globus-rsl-devel
BuildRequires: condor-classads-devel
BuildRequires: cmake

# Note the strange requirements (base package is not required!
# Point is to be able to submit jobs without installing the server.
Requires: condor
Requires: /usr/bin/grid-proxy-init
Requires: /usr/bin/voms-proxy-init
Requires: grid-certificates

# Require the appropriate version of the python library.  This
# is rather awkward, but better syntax isn't available until RHEL6
%ifarch x86_64
Requires: htcondor.so()(64bit)
%else
Requires: htcondor.so()
%endif

Obsoletes: condor-ce-client < 0.5.4
Provides:  condor-ce-client = %{version}

%description client
%{summary}

%package collector
Group: Applications/System
Summary: Central HTCondor-CE information services collector

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

# Directories necessary for HTCondor-CE files
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/run/condor-ce
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/log/condor-ce
install -m 1777 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/log/condor-ce/user
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/condor-ce
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/condor-ce/spool
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/condor-ce/execute
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lock/condor-ce
install -m 1777 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lock/condor-ce/user
install -m 1777 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/gratia/condorce_data

install -m 0755 -d -p $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add condor-ce

%preun
if [ $1 = 0 ]; then
  /sbin/service condor-ce stop >/dev/null 2>&1 || :
  /sbin/chkconfig --del condor-ce
fi

%postun
if [ "$1" -ge "1" ]; then
  /sbin/service condor-ce condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root,-)

%{_bindir}/condor_ce_history
%{_bindir}/condor_ce_router_q

%{_datadir}/condor-ce/condor_ce_router_defaults

%{_libdir}/condor/libeval_rsl.so
%{_libdir}/condor/libclassad_ce.so

%{_initrddir}/condor-ce

%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-auth.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-router.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/03-ce-shared-port.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/03-managed-fork.conf
%config(noreplace) %{_sysconfdir}/sysconfig/condor-ce

%{_datadir}/condor-ce/config.d/01-ce-auth-defaults.conf
%{_datadir}/condor-ce/config.d/01-ce-info-services-defaults.conf
%{_datadir}/condor-ce/config.d/01-ce-router-defaults.conf
%{_datadir}/condor-ce/config.d/03-ce-shared-port-defaults.conf
%{_datadir}/condor-ce/config.d/03-managed-fork-defaults.conf

%{_datadir}/condor-ce/osg-wrapper

%attr(-,condor,condor) %dir %{_localstatedir}/run/condor-ce
%attr(-,condor,condor) %dir %{_localstatedir}/log/condor-ce
%attr(1777,condor,condor) %dir %{_localstatedir}/log/condor-ce/user
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/spool
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/execute
%attr(-,condor,condor) %dir %{_localstatedir}/lock/condor-ce
%attr(1777,condor,condor) %dir %{_localstatedir}/lock/condor-ce/user
%attr(1777,root,root) %dir %{_localstatedir}/lib/gratia/condorce_data

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

%files client

%dir %{_sysconfdir}/condor-ce
%dir %{_sysconfdir}/condor-ce/config.d
%config %{_sysconfdir}/condor-ce/condor_config
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-common-auth.conf
%{_datadir}/condor-ce/config.d/01-common-auth-defaults.conf
%{_datadir}/condor-ce/config.d/01-common-collector-defaults.conf
%{_datadir}/condor-ce/ce-status.cpf
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

%{python_sitelib}/condor_ce_info_query.py*
%{python_sitelib}/condor_ce_tools.py*

%files collector

%{_bindir}/condor_ce_config_generator
%{_initrddir}/condor-ce-collector
%{_datadir}/condor-ce/config.d/01-ce-collector-defaults.conf
%{_datadir}/condor-ce/config.d/01-ce-auth-defaults.conf

%config(noreplace) %{_sysconfdir}/sysconfig/condor-ce-collector
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-collector.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-auth.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/02-ce-auth-generated.conf
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

* Fri Dec 18 2014 Brian Lin <blin@cs.wisc.edu> - 1.9-1
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


