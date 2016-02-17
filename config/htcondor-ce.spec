# Have gitrev be the short hash or branch name if doing a prerelease build
#define gitrev osg

Name: htcondor-ce
Version: 1.21
Release: 1%{?gitrev:.%{gitrev}git}%{?dist}
Summary: A framework to run HTCondor as a CE

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

%if ! 0%{?osg}
%package bdii
Group: Application/Internet
Summary:  BDII GLUE1.3/2 infoproviders and CE config for non-OSG sites.

Requires: %{name} = %{version}-%{release}, bdii

%description bdii
%{summary}
%endif

%package view
Group: Applications/Internet
Summary: A Website that will report the current status of the local HTCondor-CE

Requires: %{name} = %{version}-%{release}
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
Requires: grid-certificates >= 7

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

%if %{?rhel} >= 7
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}
install -m 0644 config/condor-ce.service $RPM_BUILD_ROOT/%{_unitdir}/condor-ce.service
install -m 0644 config/condor-ce-collector.service $RPM_BUILD_ROOT/%{_unitdir}/condor-ce-collector.service
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

%if %{?rhel} >= 7
%{_unitdir}/condor-ce.service
%endif

%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-auth.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-router.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/03-ce-shared-port.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/03-managed-fork.conf
%config(noreplace) %{_sysconfdir}/condor-ce/metrics.d/00-example-metrics.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/05-ce-health.conf
%{_sysconfdir}/condor-ce/metrics.d/00-metrics-defaults.conf
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
%{_initrddir}/condor-ce-collector
%{_datadir}/condor-ce/config.d/01-ce-collector-defaults.conf
%{_datadir}/condor-ce/config.d/01-ce-auth-defaults.conf

%if %{?rhel} >= 7
%{_unitdir}/condor-ce-collector.service
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


