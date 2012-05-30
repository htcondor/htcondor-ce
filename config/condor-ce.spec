
Name: condor-ce
Version: 0.1
Release: 1%{?dist}
Summary: A framework to run Condor as a CE

Group: Applications/System
License: Apache 2.0
URL: http://github.com/bbockelm/condor-ce

Source0: %{name}-%{version}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

Requires:  condor

Requires(post): chkconfig
Requires(preun): chkconfig
# This is for /sbin/service
Requires(preun): initscripts

%description
%{summary}

%package condor
Group: Applications/System
Summary: Default routes for submission to Condor

Requires: %{name} = %{version}-%{release}

%description condor
%{summary}

%package pbs
Group: Applications/System
Summary: Default routes for submission to PBS

Requires: %{name} = %{version}-%{release}

%description pbs
%{summary}

%prep
%setup -q

%build
%configure
make

%install
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT

# Directories necessary for Condor-CE files
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/run/condor-ce
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/log/condor-ce
install -m 1777 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/log/condor-ce/user
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/condor-ce
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/condor-ce/spool
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/condor-ce/execute
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lock/condor-ce
install -m 1777 -d -p $RPM_BUILD_ROOT/%{_localstatedir}/lock/condor-ce/user

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
%{_bindir}/condor_ce_hold
%{_bindir}/condor_ce_q
%{_bindir}/condor_ce_qedit
%{_bindir}/condor_ce_release
%{_bindir}/condor_ce_rm
%{_bindir}/condor_ce_submit
%{_bindir}/condor_ce_version
%{_bindir}/condor_ce_config_val
%{_bindir}/condor_ce_reconfig
%{_bindir}/condor_ce_router_q

%{_datadir}/condor-ce/condor_ce_env_bootstrap
%{_datadir}/condor-ce/condor_ce_router_defaults

%{_initrddir}/condor-ce

%dir %{_sysconfdir}/condor-ce
%dir %{_sysconfdir}/condor-ce/config.d
%config %{_sysconfdir}/condor-ce/condor_config
%config %{_sysconfdir}/condor-ce/config.d/01-ce-auth.conf
%config %{_sysconfdir}/condor-ce/config.d/01-ce-router.conf
%config(noreplace) %{_sysconfdir}/condor-ce/condor_mapfile
%config(noreplace) %{_sysconfdir}/sysconfig/condor-ce

%attr(-,condor,condor) %dir %{_localstatedir}/run/condor-ce
%attr(-,condor,condor) %dir %{_localstatedir}/log/condor-ce
%attr(1777,condor,condor) %dir %{_localstatedir}/log/condor-ce/user
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/spool
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/execute
%attr(-,condor,condor) %dir %{_localstatedir}/lock/condor-ce
%attr(1777,condor,condor) %dir %{_localstatedir}/lock/condor-ce/user

%files condor
%defattr(-,root,root,-)

%config %{_sysconfdir}/condor-ce/config.d/02-ce-condor.conf

%files pbs
%defattr(-,root,root,-)

%config %{_sysconfdir}/condor-ce/config.d/02-ce-pbs.conf

