
AUTOMAKE_OPTIONS = foreign

EXTRA_DIST = config/condor-ce.spec bootstrap src/condor-ce src/condor_ce_env_bootstrap src/condor_ce_config_val src/condor_ce_history src/condor_ce_hold src/condor_ce_q src/condor_ce_qedit src/condor_ce_release src/condor_ce_rm src/condor_ce_submit src/condor_ce_version src/condor_ce_reconfig src/condor_ce_router_defaults config/condor-ce src/condor_ce_router_q src/pbs_status.py src/condor_ce_status src/condor_ce_reschedule src/condor_ce_run

cceconfigdir = $(sysconfdir)/condor-ce/
dist_cceconfig_DATA = config/condor_config config/condor_mapfile

cceconfigddir = $(sysconfdir)/condor-ce/config.d
dist_cceconfigd_DATA = config/01-ce-auth.conf config/01-ce-router.conf config/02-ce-condor.conf config/02-ce-pbs.conf

sysconfigdir = $(sysconfdir)/sysconfig
dist_sysconfig_DATA = config/condor-ce

ccedatadir = $(datadir)/condor-ce/
ccedata_DATA = src/condor_ce_env_bootstrap
ccedata_SCRIPTS = src/condor_ce_router_defaults

initddir = $(sysconfdir)/rc.d/init.d
initd_SCRIPTS = src/condor-ce

bin_SCRIPTS = src/condor_ce_config_val src/condor_ce_history src/condor_ce_hold src/condor_ce_q src/condor_ce_qedit src/condor_ce_release src/condor_ce_rm src/condor_ce_submit src/condor_ce_version src/condor_ce_reconfig src/condor_ce_router_q src/condor_ce_status src/condor_ce_reschedule src/condor_ce_run

