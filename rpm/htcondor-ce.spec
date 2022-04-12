# Have gitrev be the short hash or branch name if doing a prerelease build
#define gitrev osg

Name: htcondor-ce
Version: 5.1.4
Release: 1%{?gitrev:.%{gitrev}git}%{?dist}
Summary: A framework to run HTCondor as a CE
BuildArch: noarch

Group: Applications/System
License: Apache 2.0
URL: http://github.com/opensciencegrid/htcondor-ce

# Generated with:
# git archive --prefix=%{name}-%{version}/ v%{version} | gzip > %{name}-%{version}.tar.gz
#
# Pre-release build tarballs should be generated with:
# git archive --prefix=%{name}-%{version}/ %{gitrev} | gzip > %{name}-%{version}-%{gitrev}.tar.gz
#
Source0: %{name}-%{version}%{?gitrev:-%{gitrev}}.tar.gz

BuildRequires: openssl
BuildRequires: python-srpm-macros
BuildRequires: python-rpm-macros
BuildRequires: python3-devel
BuildRequires: python3-rpm-macros

# Mapfiles.d changes require 8.9.13 but 8.9.13 has known bugs
# affecting the Job Router and Python 3 collector plugin
# https://opensciencegrid.atlassian.net/browse/HTCONDOR-244
Requires:  condor >= 9.0.0

# Init script doesn't function without `which` (which is no longer part of RHEL7 base).
Requires: which

# Require the htcondor-ce-client subpackage.  The client provides necessary
# configuration defaults and scripts for the CE itself.
Requires: %{name}-client = %{version}-%{release}

Provides:  %{name}-master = %{version}-%{release}

%systemd_requires

# We use this utility to setup a custom hostname.
Requires: /usr/bin/unshare

%description
%{summary}

%if ! 0%{?osg}
%package bdii
Group: Applications/Internet
Summary:  GLUE 2.0 infoprovider and CE config for non-OSG sites.

Requires: python3-condor
Requires: bdii

%description bdii
%{summary}

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
Requires: ganglia-gmond

%if 0%{?rhel} >= 8
Requires: python3-flask
Requires: python3-gunicorn
Requires: python3-rpm
Requires: python3-rrdtool
%else
Requires: python36-flask
Requires: python36-gunicorn
Requires: python36-rpm
Requires: rrdtool
%endif

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
Requires: blahp

%description pbs
%{summary}

%package lsf
Group: Applications/System
Summary: Default routes for submission to LSF
Requires: %{name} = %{version}-%{release}
Requires: blahp

%description lsf
%{summary}

%package sge
Group: Applications/System
Summary: Default routes for submission to SGE
Requires: %{name} = %{version}-%{release}
Requires: blahp

%description sge
%{summary}

%package slurm
Group: Applications/System
Summary: Default routes for submission to Slurm
Requires: %{name} = %{version}-%{release}
Requires: blahp

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

# Explicitly require Python 3
Requires: python3

# voms-proxy-info used by condor_ce_trace
%if 0%{?osg}
# osg uses its own, patched version of voms-clients-cpp, so keep using that
Requires: voms-clients-cpp
%else
Requires: voms-clients
%endif

Requires: python3-condor

%description client
%{summary}

%package collector
Group: Applications/System
Summary: Central HTCondor-CE information services collector

Provides: %{name}-master = %{version}-%{release}
Requires: %{name}-client = %{version}-%{release}

# Various requirements for the CE registry application
# for registering the CE with this collector.
Requires: mod_auth_openidc
Requires: python3-mod_wsgi

%if 0%{?rhel} >= 8
Requires: python3-flask
%else
Requires: python36-flask
%endif

Conflicts: %{name}

%description collector
%{summary}


%define plugins_dir %{_datadir}/condor-ce/ceview-plugins

%define __python /usr/bin/python3

%prep
%setup -q

%install
make install DESTDIR=$RPM_BUILD_ROOT PYTHON=%{__python}

%if 0%{?osg}
rm -rf $RPM_BUILD_ROOT%{_datadir}/condor-ce/htcondor-ce-provider
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/condor/config.d/50-ce-bdii-defaults.conf
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/condor/config.d/99-ce-bdii.conf
rm -f $RPM_BUILD_ROOT%{_datadir}/condor-ce/apel/README.md
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/condor/config.d/50-condor-apel.conf
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/condor-ce/config.d/50-ce-apel.conf
rm -f $RPM_BUILD_ROOT%{_datadir}/condor-ce/config.d/50-ce-apel-defaults.conf
rm -f $RPM_BUILD_ROOT%{_datadir}/condor-ce/condor_batch_blah.sh
rm -f $RPM_BUILD_ROOT%{_datadir}/condor-ce/condor_ce_apel.sh
rm -f $RPM_BUILD_ROOT%{_unitdir}/condor-ce-apel.service
rm -f $RPM_BUILD_ROOT%{_unitdir}/condor-ce-apel.timer
mv -f $RPM_BUILD_ROOT%{_sysconfdir}/condor-ce/config.d/05-ce-view-table.osg.conf \
      $RPM_BUILD_ROOT%{_sysconfdir}/condor-ce/config.d/05-ce-view-table.conf
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/condor-ce/config.d/05-ce-view-table.nonosg.conf
mv -f $RPM_BUILD_ROOT%{_datadir}/condor-ce/config.d/05-ce-view-table-defaults.osg.conf \
      $RPM_BUILD_ROOT%{_datadir}/condor-ce/config.d/05-ce-view-table-defaults.conf
rm -f $RPM_BUILD_ROOT%{_datadir}/condor-ce/config.d/05-ce-view-table-defaults.nonosg.conf
%else
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/bdii/gip/provider
mv $RPM_BUILD_ROOT%{_datadir}/condor-ce/htcondor-ce-provider \
   $RPM_BUILD_ROOT%{_localstatedir}/lib/bdii/gip/provider
mkdir -p $RPM_BUILD_ROOT%{_datadir}/condor-ce/apel/
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/condor-ce/apel/
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/condor/history/
rm -f $RPM_BUILD_ROOT%{plugins_dir}/agis_json.py
mv -f $RPM_BUILD_ROOT%{_sysconfdir}/condor-ce/config.d/05-ce-view-table.nonosg.conf \
      $RPM_BUILD_ROOT%{_sysconfdir}/condor-ce/config.d/05-ce-view-table.conf
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/condor-ce/config.d/05-ce-view-table.osg.conf
mv -f $RPM_BUILD_ROOT%{_datadir}/condor-ce/config.d/05-ce-view-table-defaults.nonosg.conf \
      $RPM_BUILD_ROOT%{_datadir}/condor-ce/config.d/05-ce-view-table-defaults.conf
rm -f $RPM_BUILD_ROOT%{_datadir}/condor-ce/config.d/05-ce-view-table-defaults.osg.conf
%endif

# Gratia accounting cleanup
%if ! 0%{?osg}
rm -rf ${RPM_BUILD_ROOT%}%{_datadir}/condor-ce/gratia_cleanup.py*
%endif

install -m 0755 -d -p $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d
install -m 0755 -d -p $RPM_BUILD_ROOT/%{_sysconfdir}/condor-ce/bosco_override

%pre collector

getent group condorce_webapp >/dev/null || groupadd -r condorce_webapp
getent passwd condorce_webapp >/dev/null || \
  useradd -r -g condorce_webapp -d %_var/lib/condor-ce/webapp -s /sbin/nologin \
    -c "Webapp user for HTCondor-CE collector" condorce_webapp

%post
/bin/systemctl daemon-reload >/dev/null 2>&1 || :

if [ ! -e /etc/condor-ce/passwords.d/POOL ]; then
    %{_datadir}/condor-ce/condor_ce_create_password >/dev/null 2>&1 || :
fi

%systemd_post condor-ce.service

%post collector
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
%systemd_post condor-ce-collector.service condor-ce-collector-config.service

if [ ! -e /etc/condor-ce/passwords.d/POOL ]; then
    %{_datadir}/condor-ce/condor_ce_create_password >/dev/null 2>&1 || :
fi

autogenerated_token=/etc/condor-ce/webapp.tokens.d/50-webapp
if [ ! -e $autogenerated_token ]; then
    CONDOR_CONFIG=/etc/condor-ce/condor_config condor_token_create \
                 -authz ADMINISTRATOR -identity condorce_webapp@htcondor.org > $autogenerated_token 2>&1 || :
fi

%preun
%systemd_preun condor-ce.service

%preun collector
%systemd_preun condor-ce-collector.service condor-ce-collector-config.service

%postun
%systemd_postun_with_restart condor-ce.service

%postun collector
%systemd_postun_with_restart condor-ce-collector.service condor-ce-collector-config.service

%files
%defattr(-,root,root,-)

%if 0%{?osg}
%{_datadir}/condor-ce/gratia_cleanup.py*
%if 0%{?rhel} < 8
%{_datadir}/condor-ce/__pycache__/gratia_cleanup.*.pyc
%endif
%attr(1777,root,root) %dir %{_localstatedir}/lib/gratia/condorce_data
%endif

%{_bindir}/condor_ce_history
%{_bindir}/condor_ce_router_q

%{_datadir}/condor-ce/condor_ce_router_defaults

%{_unitdir}/condor-ce.service
%{_tmpfilesdir}/condor-ce.conf

%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-auth.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-router.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-pilot-env.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/03-managed-fork.conf
%config(noreplace) %{_sysconfdir}/sysconfig/condor-ce

%config(noreplace) %{_sysconfdir}/condor-ce/mapfiles.d/10-gsi.conf
%config(noreplace) %{_sysconfdir}/condor-ce/mapfiles.d/10-scitokens.conf
%config(noreplace) %{_sysconfdir}/condor-ce/mapfiles.d/50-gsi-callout.conf

%{_datadir}/condor-ce/config.d/01-ce-auth-defaults.conf
%{_datadir}/condor-ce/config.d/01-ce-audit-payloads-defaults.conf
%{_datadir}/condor-ce/config.d/01-ce-router-defaults.conf
%{_datadir}/condor-ce/config.d/01-pilot-env-defaults.conf
%{_datadir}/condor-ce/config.d/03-managed-fork-defaults.conf
%{_datadir}/condor-ce/config.d/05-ce-health-defaults.conf

%{_datadir}/condor-ce/local-wrapper

%{python3_sitelib}/htcondorce/audit_payloads.py
%{python3_sitelib}/htcondorce/__pycache__/audit_payloads.*.pyc

%{_bindir}/condor_ce_host_network_check
%{_bindir}/condor_ce_register

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

%files apel
%{_datadir}/condor-ce/apel/README.md
%{_datadir}/condor-ce/condor_batch_blah.sh
%{_datadir}/condor-ce/condor_ce_apel.sh
%{_datadir}/condor-ce/config.d/50-ce-apel-defaults.conf
%{_sysconfdir}/condor/config.d/50-condor-apel.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/50-ce-apel.conf
%attr(-,root,root) %dir %{_localstatedir}/lib/condor-ce/apel/
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor/history/

%{_unitdir}/condor-ce-apel.service
%{_unitdir}/condor-ce-apel.timer
%endif

%files view
%defattr(-,root,root,-)

# Web package
%{python3_sitelib}/htcondorce/web.py
%{python3_sitelib}/htcondorce/web_utils.py
%{python3_sitelib}/htcondorce/rrd.py
%{python3_sitelib}/htcondorce/registry.py
%{python3_sitelib}/htcondorce/__pycache__/web.*.pyc
%{python3_sitelib}/htcondorce/__pycache__/web_utils.*.pyc
%{python3_sitelib}/htcondorce/__pycache__/rrd.*.pyc
%{python3_sitelib}/htcondorce/__pycache__/registry.*.pyc
%{python3_sitelib}/htcondorce/static/bootstrap-pincode-input.js
%{python3_sitelib}/htcondorce/static/bootstrap-pincode-input.css

%dir %{_datadir}/condor-ce/templates
%{_datadir}/condor-ce/templates/index.html
%{_datadir}/condor-ce/templates/vos.html
%{_datadir}/condor-ce/templates/metrics.html
%{_datadir}/condor-ce/templates/health.html
%{_datadir}/condor-ce/templates/view_base.html
%{_datadir}/condor-ce/templates/pilots.html
%{_datadir}/condor-ce/templates/code.html
%{_datadir}/condor-ce/templates/code_submit.html
%{_datadir}/condor-ce/templates/code_submit_failure.html

%{_datadir}/condor-ce/config.d/05-ce-view-defaults.conf
%{_datadir}/condor-ce/config.d/05-ce-view-table-defaults.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/05-ce-view.conf
%config(noreplace) %{_sysconfdir}/condor-ce/metrics.d/00-example-metrics.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/05-ce-health.conf
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/05-ce-view-table.conf
%dir %{_sysconfdir}/condor-ce/metrics.d
%{_sysconfdir}/condor-ce/metrics.d/00-metrics-defaults.conf

%{_datadir}/condor-ce/condor_ce_view
%{_datadir}/condor-ce/condor_ce_metric
%{_datadir}/condor-ce/condor_ce_jobmetrics

%dir %{plugins_dir}

%if 0%{?osg}
%{plugins_dir}/agis_json.py*
%if 0%{?rhel} < 8
%dir %{plugins_dir}/__pycache__
%{plugins_dir}/__pycache__/agis_json.*.pyc
%endif
%endif

%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/spool/ceview
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/spool/ceview/vos
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/spool/ceview/metrics

%files condor
%defattr(-,root,root,-)

%config(noreplace) %{_sysconfdir}/condor-ce/uid_acct_group.map
%config(noreplace) %{_sysconfdir}/condor-ce/x509_acct_group.map
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/02-ce-condor.conf
%{_datadir}/condor-ce/config.d/02-ce-condor-defaults.conf
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
%{_datadir}/condor-ce/bosco-cluster-remote-hosts.*
%if 0%{?rhel} < 8
%{_datadir}/condor-ce/__pycache__/bosco-cluster-remote-hosts.*.pyc
%endif
%dir %{_sysconfdir}/condor-ce/bosco_override

%files client

%{_bindir}/condor_ce_info_status
%{python3_sitelib}/htcondorce/info_query.py
%{python3_sitelib}/htcondorce/__pycache__/info_query.*.pyc

%dir %{_sysconfdir}/condor-ce
%dir %{_sysconfdir}/condor-ce/config.d
%config %{_sysconfdir}/condor-ce/condor_config
%attr(0700,root,root) %dir %{_sysconfdir}/condor-ce/passwords.d
%attr(0700,condor,condor) %dir %{_sysconfdir}/condor-ce/tokens.d

%dir %{_datadir}/condor-ce/
%dir %{_datadir}/condor-ce/config.d
%{_datadir}/condor-ce/config.d/01-common-auth-defaults.conf
%{_datadir}/condor-ce/config.d/01-common-collector-defaults.conf
%{_datadir}/condor-ce/ce-status.cpf
%{_datadir}/condor-ce/pilot-status.cpf

%dir %{_datadir}/condor-ce/mapfiles.d
%config %{_datadir}/condor-ce/mapfiles.d/50-common-default.conf

%config %{_sysconfdir}/condor-ce/condor_mapfile

%dir %{_datadir}/condor-ce
%if 0%{?rhel} < 8
%dir %{_datadir}/condor-ce/__pycache__
%{_datadir}/condor-ce/__pycache__/verify_ce_config.*.pyc
%endif
%{_datadir}/condor-ce/condor_ce_env_bootstrap
%{_datadir}/condor-ce/condor_ce_startup
%{_datadir}/condor-ce/condor_ce_startup_internal
%{_datadir}/condor-ce/verify_ce_config.py*
%{_datadir}/condor-ce/condor_ce_create_password

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
%{_bindir}/condor_ce_scitoken_exchange
%{_bindir}/condor_ce_reconfig
%{_bindir}/condor_ce_reschedule
%{_bindir}/condor_ce_status
%{_bindir}/condor_ce_version
%{_bindir}/condor_ce_trace
%{_bindir}/condor_ce_ping

%dir %{python3_sitelib}/htcondorce
%{python3_sitelib}/htcondorce/__init__.py
%{python3_sitelib}/htcondorce/tools.py
%{python3_sitelib}/htcondorce/__pycache__/__init__.*.pyc
%{python3_sitelib}/htcondorce/__pycache__/tools.*.pyc

%files collector

%{_datadir}/condor-ce/config.d/01-ce-collector-defaults.conf
%{_datadir}/condor-ce/config.d/01-ce-auth-defaults.conf
%{_datadir}/condor-ce/mapfiles.d/50-central-collector.conf
%{_datadir}/condor-ce/condor_ce_create_password

%{_unitdir}/condor-ce-collector.service
%{_tmpfilesdir}/condor-ce-collector.conf

%config %{_datadir}/condor-ce/config.d/01-ce-collector-requirements.conf
%config %{_datadir}/condor-ce/config.d/05-ce-collector-auth.conf
%config(noreplace) %{_sysconfdir}/sysconfig/condor-ce-collector
%config(noreplace) %{_sysconfdir}/condor-ce/config.d/01-ce-collector.conf
%attr(0700,condorce_webapp,condorce_webapp) %dir %{_sysconfdir}/condor-ce/webapp.tokens.d
%attr(0700,root,root) %dir %{_sysconfdir}/condor-ce/passwords.d

%config(noreplace) %attr(0600,root,root) %{_sysconfdir}/httpd/conf.d/htcondorce_registry.conf

%attr(-,condor,condor) %dir %{_localstatedir}/run/condor-ce
%attr(-,condor,condor) %dir %{_localstatedir}/log/condor-ce
%attr(1777,condor,condor) %dir %{_localstatedir}/log/condor-ce/user
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/spool
%attr(-,condor,condor) %dir %{_localstatedir}/lib/condor-ce/execute
%attr(-,condor,condor) %dir %{_localstatedir}/lock/condor-ce
%attr(1777,condor,condor) %dir %{_localstatedir}/lock/condor-ce/user
%attr(1777,root,root) %dir %{_localstatedir}/lib/gratia/condorce_data
%{_localstatedir}/www/wsgi-scripts/htcondor-ce/htcondor-ce-registry.wsgi

%changelog
* Thu Mar 24 2022 Tim Theisen <tim@cs.wisc.edu> - 5.1.4-1
- Fix whole node job glidein CPUs and GPUs expressions that caused held jobs
- Fix bug where default CERequirements were being ignored
- Pass whole node request from GlideinWMS to the batch system
- Since CentOS 8 has reached end of life, we build and test on Rocky Linux 8

* Tue Dec 21 2021 Tim Theisen <tim@cs.wisc.edu> - 5.1.3-1
- The HTCondor-CE central collector requires SSL credentials from client CEs
- Fix BDII crash if an HTCondor Access Point is not available
- Fix formatting of APEL records that contain huge values
- HTCondor-CE client mapfiles are not installed on the central collector

* Wed Sep 22 2021 Tim Theisen <tim@cs.wisc.edu> - 5.1.2-1
- Fixed the default memory and CPU requests when using job router transforms
- Apply default MaxJobs and MaxJobsIdle when using job router transforms
- Improved SciTokens support in submission tools
- Fixed --debug flag in condor_ce_run
- Update configuration verification script to handle job router transforms
- Corrected ownership of the HTCondor PER_JOBS_HISTORY_DIR
- Fix bug passing maximum wall time requests to the local batch system

* Tue May 18 2021 Brian Lin <blin@cs.wisc.edu> - 5.1.1-1
- Improve restart time of HTCondor-CE View (HTCONDOR-420)
- Fix bug that caused HTCondor-CE to ignore incoming BatchRuntime requests (#480)
- Fix blahp packaging requirement (HTCONDOR-504)

* Tue Mar 30 2021 Mark Coatsworth <coatsworth@cs.wisc.edu> - 5.1.0-1
- Fix an issue where the CE removed running jobs prematurely (HTCONDOR-350)
- Add optional job router transform syntax (HTCONDOR-243)
- Add username and X.509 accounting group mapfiles for use by job router transforms (HTCONDOR-187)
- Replace custom mappings in condor_mapfile with /etc/condor-ce/mapfiles.d/ (HTCONDOR-244)
- Require regular expressions in the second field of the unified mapfile be enclosed by '/'(HTCONDOR-244)
- Update maxWallTime logic to accept BatchRuntime (HTCONDOR-80)
- Append SSL to the default authentication methods list (HTCONDOR-366)
- APEL reporting scripts now use the local HTCondor's PER_JOB_HISTORY_DIR to collect job data. (HTCONDOR-293)
- Use the `GlobalJobID` attribute as the APEL record `lrmsID` (#426)
- Update HTCondor-CE registry app to Python 3 (HTCONDOR-307)
- Enable SSL authentication by default for `READ`/`WRITE` authorization levels (HTCONDOR-366)
- Downgrade errors in the configuration verification startup script to support routes written in the transform syntax (#465)
- Allow required directories to be owned by non-`condor` groups (#451)
- Fix an issue with an overly aggressive default `SYSTEM_PERIODIC_REMOVE` (HTCONDOR-350)
- Fix incorrect path to Python 3 Collector plugin (HTCONDOR-400)
- Fix faulty validation of `JOB_ROUTER_ROUTE_NAMES` and `JOB_ROUTER_ENTRIES` in the startup script (HTCONDOR-406)
- Fix various Python 3 incompatibilities (#460)

* Thu Feb 11 2021 Brian Lin <blin@cs.wisc.edu> - 5.0.0-1
- Add Python 3 and EL8 support (HTCondor-13)
- Whole node jobs (HTCondor batch systems only) now make use of GPUs (HTCONDOR-103)
- Added `USE_CE_HOME_DIR` configuration variable (default: `False`) to allow users to enable setting `$HOME` in the
  routed job's environment based on the HTCondor-CE user's home directory
- HTCondor-CE Central Collectors now prefer GSI over SSL authentication (HTCONDOR-237)
- HTCondor-CE registry now validates the value of submitted client codes (HTCONDOR-241)
- Automatically remove CE jobs that exceed their `maxWalltime` (if defined) or the configuration value of
  `ROUTED_JOB_MAX_TIME` (default: 4320 sec/72 hrs)
- Remove circular HTCondor-CE View configuration definition (HTCONDOR-161)
- Replace htcondor-ce package requirement with python2-condor for htcondor-ce-bdii

* Wed Jan 27 2021 Brian Lin <blin@cs.wisc.edu> - 5.0.0-0.rc1
- Remove unused deps from the central collector packaging

* Wed Jan 27 2021 Brian Lin <blin@cs.wisc.edu> - 5.0.0-0.rc1
- Convert HTCondor-CE to Python 3 (#391, #397, #400, #402, #403, #404, #405,
  #406)
- Add USE_CE_HOME_DIR configuration to allow users to disable passing the CE
  users's HOME dir to the job on the worker node (#377)
- RPM packaging fixes for default CE registry httpd configuration (#372)
- Add CE View advertising of GPU job counts to the central collector (#381)
- BDII: Reduce package dependencies of htcondor-ce-bdii (#384)
- BDII: Add support for whitespace/comma separated local collectors (#375)

* Wed Jul 15 2020 Mátyás Selmeci <matyas@cs.wisc.edu> - 4.4.1-2
- Change voms-clients-cpp requirement to voms-clients for non-OSG builds,
  because voms-clients-java works equally well

* Tue Jul 14 2020 Brian Lin <blin@cs.wisc.edu> - 4.4.1-1
- Fix a stacktrace with the BDII provider when `HTCONDORCE_SPEC` isn't
  defined in the local HTCondor configuration
- Fixed a race condition that could result in removed jobs being put
  on hold
- Improve performance of the HTCondor-CE View
  
* Mon Jun 15 2020 Brian Lin <blin@cs.wisc.edu> - 4.4.0-1
- Add plug-in interface to HTCondor-CE View and separate out
  OSG-specific code and configuration (SOFTWARE-3963)
- Add configuration option (COMPLETED_JOB_EXPIRATION) for how many
  days completed jobs may stay in the queue (SOFTWARE-4108)

- Replace APEL uploader SchedD cron with init and systemd services
  (#323)
- Fix HTCondor-CE View SchedD query that caused "Info" tables to be blank

* Wed May 27 2020 Brian Lin <blin@cs.wisc.edu> - 4.3.0-2
- Update the packaging for 4.3.0

* Wed May 27 2020 Brian Lin <blin@cs.wisc.edu> - 4.3.0-1
- Add the CE registry web application to the central collector. The
  registry provides an interface to OSG site administrators of
  HTCondor-CEs to retrieve an HTCondor IDTOKEN for authenticating
  pilot job submissions (#298, #299)
- Identify broken job routes upon startup (#319)
- Add benchmarking parameters to the BDII provider via HTCONDORCE_SPEC
  in the configuration. See /etc/condor-ce/config.d/99-ce-bdii.conf
  for examples (#311)
- Fix handling of unmapped GSI users in the central collector (#317)
- Fix reference to old BDII configuration values (#322)

* Wed Mar 18 2020 Brian Lin <blin@cs.wisc.edu> - 4.2.1-1
- Drop vestigial central collector config generator
- Fix unmapped GSI/SSL regexps and allow unmapped enttities to advertise to the central ceollector (SOFTWARE-3939)

* Thu Mar 12 2020 Brian Lin <blin@cs.wisc.edu> - 4.2.0-1
- Add SSL support for reporting to central collectors (SOFTWARE-3939)
- GLUE2 validation improvements for the BDII provider (#308)

* Mon Nov 04 2019 Brian Lin <blin@cs.wisc.edu> - 4.1.0-1
- Add non-OSG method for modifying the job environment (SOFTWARE-3871)
- Simplify configuration of APEL scripts
- Do not require authentication for queue reads (SOFTWARE-3860)
- Allow local CE users to submit jobs without a proxy or token (SOFTWARE-3856)
- Fix the ability to specify grid certificate locations for SSL authentication
- Refine the APEL record filter to ignore jobs that have not yet started
- Fix an issue where `condor_ce_q` required authentication
- Re-enable the ability for local users to submit jobs to the CE queue
- Fix an issue where some jobs were capped at 72 minutes instead of 72 hours
- Add `systemctl daemon-reload` to packaging for initial installations
- Improve robustness of BDII provider

* Mon Sep 16 2019 Brian Lin <blin@cs.wisc.edu> - 4.0.1-1
- Fix call to error() (#245)

* Fri Sep 13 2019 Brian Lin <blin@cs.wisc.edu> - 4.0.0-1
- Disable job retries (SOFTWARE-3407)

* Tue Sep 10 2019 Brian Lin <blin@cs.wisc.edu> - 4.0.0-0.2
- Use simplified CERequirements format:
https://htcondor-wiki.cs.wisc.edu/index.cgi/tktview?tn=6133,86
- Reorganize HTCondor-CE configuration: configuration that admins are
expected to change is in /etc, other configuration is in /usr
- Remove most OSG-specific configuration into the OSG CE metapackage
(SOFTWARE-3813)
- Increase the default maximum walltime to 72 hours

* Fri Aug 09 2019 Brian Bockelman <brian.bockelman@cern.ch> - 4.0.0-0.2
- Add support for SciTokens.

* Thu Aug 01 2019 Brian Lin <blin@cs.wisc.edu> - 3.3.0-1
- Add APEL support for HTCondor-CE and HTCondor backends
- Store malformed ads reporting to htcondor-ce-collector

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

* Tue Jan 24 2017 Brian Lin <blin@cs.wisc.edu> - 2.1.2-1
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

* Wed Aug 31 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.8-2
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

* Mon Feb 22 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.2-1
- Drop CE ClassAd functions from JOB_ROUTER_DEFAULTS

* Wed Feb 17 2016 Brian Lin <blin@cs.wisc.edu> - 2.0.1-1
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

* Fri Sep 25 2015 Brian Lin <blin@cs.wisc.edu> - 1.16-1
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

