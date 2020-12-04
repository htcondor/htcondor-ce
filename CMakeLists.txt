
project(condor-ce NONE)

cmake_minimum_required(VERSION 2.6)

set( HTCONDORCE_VERSION "4.4.1" CACHE INTERNAL "Version of the HTCondor-CE" )

find_package(PkgConfig)

set(SHARE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}/share" CACHE PATH "Base directory for files which go to share/")
set(SYSCONF_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}/etc" CACHE PATH "Base directory for files which go to etc/")
set(STATE_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}/var" CACHE PATH "Base directory for files which go to var/")

include(FindPythonInterp)
execute_process ( COMMAND ${PYTHON_EXECUTABLE} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib().replace('/usr', '${CMAKE_INSTALL_PREFIX}', 1))" OUTPUT_VARIABLE DETECTED_PYTHON_SITELIB OUTPUT_STRIP_TRAILING_WHITESPACE )
set(PYTHON_SITELIB "${DETECTED_PYTHON_SITELIB}" CACHE PATH "Base directory for python libraries")

configure_file (
  "${PROJECT_SOURCE_DIR}/config/01-ce-router.conf.in"
  "${CMAKE_CURRENT_BINARY_DIR}/config/01-ce-router.conf"
)

configure_file (
  "${PROJECT_SOURCE_DIR}/config/01-ce-router-defaults.conf.in"
  "${CMAKE_CURRENT_BINARY_DIR}/config/01-ce-router-defaults.conf"
)

install(PROGRAMS
  src/condor_ce_startup
  src/verify_ce_config.py
  src/condor_ce_startup_internal
  src/condor_ce_env_bootstrap
  src/condor_ce_router_defaults
  src/local-wrapper
  src/condor_ce_jobmetrics
  src/condor_ce_metric
  src/condor_ce_view
  src/gratia_cleanup.py
  src/condor_ce_create_password
  contrib/apelscripts/condor_ce_apel.sh
  contrib/apelscripts/condor_blah.sh
  contrib/apelscripts/condor_batch.sh
  contrib/bdii/htcondor-ce-provider
  contrib/bosco/bosco-cluster-remote-hosts.py
  contrib/bosco/bosco-cluster-remote-hosts.sh
  DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce)

install(FILES
  src/htcondorce/plugins/agis_json.py
  DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce/ceview-plugins)

install(PROGRAMS
  src/condor_ce_config_val
  src/condor_ce_history
  src/condor_ce_hold
  src/condor_ce_info_status
  src/condor_ce_q
  src/condor_ce_qedit
  src/condor_ce_release
  src/condor_ce_rm
  src/condor_ce_submit
  src/condor_ce_version
  src/condor_ce_reconfig
  src/condor_ce_router_q
  src/condor_ce_status
  src/condor_ce_register
  src/condor_ce_reschedule
  src/condor_ce_run
  src/condor_ce_trace
  src/condor_ce_ping
  src/condor_ce_off
  src/condor_ce_on
  src/condor_ce_restart
  src/condor_ce_job_router_info
  src/condor_ce_host_network_check
  src/condor_ce_scitoken_exchange
  DESTINATION ${CMAKE_INSTALL_PREFIX}/bin)
install(FILES
  src/htcondorce/__init__.py
  src/htcondorce/web_utils.py
  src/htcondorce/web.py
  src/htcondorce/rrd.py
  src/htcondorce/tools.py
  src/htcondorce/info_query.py
  src/htcondorce/registry.py
  src/audit_payloads.py
  DESTINATION ${PYTHON_SITELIB}/htcondorce)
install(FILES
  src/htcondorce/static/bootstrap-pincode-input.css
  src/htcondorce/static/bootstrap-pincode-input.js
  DESTINATION ${PYTHON_SITELIB}/htcondorce/static)

install(FILES
  config/condor_config
  config/condor_mapfile
  config/condor_mapfile.central_collector
  config/condor_mapfile.osg
  DESTINATION ${SYSCONF_INSTALL_DIR}/condor-ce)

install(FILES config/htcondorce_registry.conf DESTINATION ${SYSCONF_INSTALL_DIR}/httpd/conf.d)
# This file should contain various OIDC secrets; should not be world-readable.
install(CODE "execute_process(COMMAND chmod 0700 ${SYSCONF_INSTALL_DIR}/httpd/conf.d/htcondorce_registry.conf)")
install(CODE "execute_process(COMMAND chown root:root ${SYSCONF_INSTALL_DIR}/httpd/conf.d/htcondorce_registry.conf)")

install(FILES src/htcondor-ce-registry.wsgi DESTINATION ${STATE_INSTALL_DIR}/www/wsgi-scripts/htcondor-ce)

install(FILES
  contrib/apelscripts/README.md
  DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce/apel)

install(FILES
  config/metrics.d/00-metrics-defaults.conf
  config/metrics.d/00-example-metrics.conf
  DESTINATION ${SYSCONF_INSTALL_DIR}/condor-ce/metrics.d)
install(FILES
  config/01-ce-auth.conf
  config/01-ce-collector.conf
  ${CMAKE_CURRENT_BINARY_DIR}/config/01-ce-router.conf
  config/01-pilot-env.conf
  config/02-ce-condor.conf
  config/02-ce-pbs.conf
  config/02-ce-lsf.conf
  config/02-ce-sge.conf
  config/02-ce-slurm.conf
  config/02-ce-bosco.conf
  config/03-managed-fork.conf
  config/05-ce-view.conf
  config/05-ce-health.conf
  config/05-ce-view-table.osg.conf
  config/05-ce-view-table.nonosg.conf
  contrib/apelscripts/50-ce-apel.conf
  DESTINATION ${SYSCONF_INSTALL_DIR}/condor-ce/config.d)
install(FILES
  config/01-ce-collector-defaults.conf
  config/01-ce-collector-requirements.conf
  config/01-ce-audit-payloads-defaults.conf
  config/01-ce-auth-defaults.conf
  config/01-common-auth-defaults.conf
  config/01-common-collector-defaults.conf
  ${CMAKE_CURRENT_BINARY_DIR}/config/01-ce-router-defaults.conf
  config/01-pilot-env-defaults.conf
  config/02-ce-condor-defaults.conf
  config/02-ce-pbs-defaults.conf
  config/02-ce-lsf-defaults.conf
  config/02-ce-sge-defaults.conf
  config/02-ce-slurm-defaults.conf
  config/02-ce-bosco-defaults.conf
  config/03-managed-fork-defaults.conf
  config/05-ce-collector-auth.conf
  config/05-ce-view-defaults.conf
  config/05-ce-health-defaults.conf
  config/05-ce-view-defaults.conf
  config/05-ce-view-table-defaults.osg.conf
  config/05-ce-view-table-defaults.nonosg.conf
  contrib/apelscripts/50-ce-apel-defaults.conf
  DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce/config.d)
install(FILES
  config/50-condor-ce-defaults.conf
  contrib/apelscripts/50-condor-apel.conf
  contrib/bdii/99-ce-bdii.conf
  contrib/bdii/50-ce-bdii-defaults.conf
  DESTINATION
  ${SYSCONF_INSTALL_DIR}/condor/config.d)

set(HTCONDORCE_DIRS ${STATE_INSTALL_DIR}/run/condor-ce ${STATE_INSTALL_DIR}/log/condor-ce
  ${STATE_INSTALL_DIR}/log/condor-ce/user ${STATE_INSTALL_DIR}/lib/condor-ce ${STATE_INSTALL_DIR}/lib/condor-ce/spool
  ${STATE_INSTALL_DIR}/lib/condor-ce/spool/ceview ${STATE_INSTALL_DIR}/lib/condor-ce/spool/ceview/vos
  ${STATE_INSTALL_DIR}/lib/condor-ce/spool/ceview/metrics ${STATE_INSTALL_DIR}/lib/condor-ce/execute
  ${STATE_INSTALL_DIR}/lock/condor-ce ${STATE_INSTALL_DIR}/lock/condor-ce/user
  ${STATE_INSTALL_DIR}/lib/gratia/condorce_data ${SYSCONF_INSTALL_DIR}/logrotate.d
  ${SYSCONF_INSTALL_DIR}/condor-ce/tokens.d)

foreach(dir IN ITEMS ${HTCONDORCE_DIRS})
  install(DIRECTORY DESTINATION ${dir})
  install(CODE "execute_process(COMMAND chown condor:condor ${dir})")
endforeach(dir)

set(HTCONDORCE_ROOT_DIRS ${SYSCONF_INSTALL_DIR}/condor-ce/passwords.d)

foreach(root_dir IN ITEMS ${HTCONDORCE_ROOT_DIRS})
  install(DIRECTORY DESTINATION ${root_dir})
  install(CODE "execute_process(COMMAND chown root:root ${root_dir})")
endforeach(root_dir)

# These are the tokens for use by the CE registry webapp
set(HTCONDORCE_WEBAPP_DIRS ${SYSCONF_INSTALL_DIR}/condor-ce/webapp.tokens.d
  ${STATE_INSTALL_DIR}/lib/condor-ce/webapp)
foreach(webapp_dir IN ITEMS ${HTCONDORCE_WEBAPP_DIRS})
  install(DIRECTORY DESTINATION ${webapp_dir})
  install(CODE "execute_process(COMMAND chown condorce_webapp:condorce_webapp ${webapp_dir})")
endforeach(webapp_dir)

set(STICKY_HTCONDORCE_DIRS ${STATE_INSTALL_DIR}/log/condor-ce/user ${STATE_INSTALL_DIR}/lock/condor-ce/user
  ${SYSCONF_INSTALL_DIR}/logrotate.d)

foreach(sticky_dir IN ITEMS ${STICKY_HTCONDORCE_DIRS})
  install(CODE "execute_process(COMMAND chmod 1777 ${sticky_dir})")
endforeach(sticky_dir)

set(PRIVATE_HTCONDORCE_DIRS ${SYSCONF_INSTALL_DIR}/condor-ce/passwords.d
  ${SYSCONF_INSTALL_DIR}/condor-ce/tokens.d)

foreach(private_dir IN ITEMS ${PRIVATE_HTCONDORCE_DIRS})
  install(CODE "execute_process(COMMAND chmod 0700 ${private_dir})")
endforeach(private_dir)

install(FILES config/ce-status.cpf config/pilot-status.cpf DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce)
install(FILES templates/index.html templates/vos.html templates/metrics.html
        templates/code.html templates/code_submit.html templates/code_submit_failure.html
	templates/health.html templates/header.html templates/pilots.html DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce/templates)
install(FILES config/condor-ce config/condor-ce-collector DESTINATION ${SYSCONF_INSTALL_DIR}/sysconfig)

install(FILES
  config/condor-ce.service
  config/condor-ce-collector.service
  contrib/apelscripts/condor-ce-apel.service
  contrib/apelscripts/condor-ce-apel.timer
  DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/systemd/system)

install(FILES config/condor-ce.conf config/condor-ce-collector.conf DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/tmpfiles.d)
