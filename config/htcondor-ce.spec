Name: htcondor-ce
Version: 1.1
Release: 1%{?dist}
Summary: A framework to run HTCondor as a CE

Group: Applications/System
License: Apache 2.0
URL: http://github.com/bbockelm/condor-ce

# Generated with:
# git archive --prefix=%{name}-%{version}/ v%{version} | gzip > %{name}-%{version}.tar.gz
#
Source0: %{name}-%{version}.tar.gz

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

%prep
%setup -q

%build
%cmake
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

%{_initrddir}/condor-ce

%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-auth.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-router.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/03-ce-shared-port.conf
%config(noreplace) %{_sysconfdir}/condor-ce/condor_mapfile
%config(noreplace) %{_sysconfdir}/sysconfig/condor-ce

%{_datadir}/condor-ce/config.d/01-ce-auth-defaults.conf
%{_datadir}/condor-ce/config.d/01-ce-router-defaults.conf
%{_datadir}/condor-ce/config.d/03-ce-shared-port-defaults.conf

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

%{_datadir}/condor-ce/condor_ce_env_bootstrap

%{_bindir}/condor_ce_config_val
%{_bindir}/condor_ce_hold
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

%changelog
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


