
project(condor-ce)

cmake_minimum_required(VERSION 2.6)

set( HTCONDORCE_VERSION "4.0.0" CACHE INTERNAL "Version of the HTCondor-CE" )

set( CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake )

find_package(PkgConfig)

if( CMAKE_COMPILER_IS_GNUCXX )
  set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Werror" )
endif( CMAKE_COMPILER_IS_GNUCXX )

include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
if(COMPILER_SUPPORTS_CXX11)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
endif()

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
  src/condor_ce_client_env_bootstrap
  src/condor_ce_router_defaults
  src/local-wrapper
  src/condor_ce_jobmetrics
  src/condor_ce_metric
  src/condor_ce_view
  src/gratia_cleanup.py
  contrib/apelscripts/condor_blah.sh
  contrib/apelscripts/condor_batch.sh
  contrib/bdii/htcondor-ce-provider
  DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce)

install(PROGRAMS
  src/condor_ce_config_generator
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
  src/condor_ce_reschedule
  src/condor_ce_run
  src/condor_ce_trace
  src/condor_ce_ping
  src/condor_ce_off
  src/condor_ce_on
  src/condor_ce_restart
  src/condor_ce_job_router_info
  src/condor_ce_host_network_check
  DESTINATION ${CMAKE_INSTALL_PREFIX}/bin)
install(FILES
  src/htcondorce/__init__.py
  src/htcondorce/web_utils.py
  src/htcondorce/web.py
  src/htcondorce/rrd.py
  src/htcondorce/tools.py
  src/htcondorce/info_query.py
  src/audit_payloads.py
  DESTINATION ${PYTHON_SITELIB}/htcondorce)

install(FILES config/condor_config config/condor_mapfile config/condor_mapfile.osg DESTINATION ${SYSCONF_INSTALL_DIR}/condor-ce)

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
  config/02-ce-condor.conf
  config/02-ce-pbs.conf
  config/02-ce-lsf.conf
  config/02-ce-sge.conf
  config/02-ce-slurm.conf
  config/02-ce-bosco.conf
  config/03-managed-fork.conf
  config/04-ce-collector-auth.conf
  config/05-ce-view.conf
  config/05-ce-health.conf
  contrib/apelscripts/50-ce-apel.conf
  DESTINATION ${SYSCONF_INSTALL_DIR}/condor-ce/config.d)
install(FILES
  config/01-blahp-location.conf
  config/01-ce-collector-defaults.conf
  config/01-ce-collector-requirements.conf
  config/01-ce-audit-payloads-defaults.conf
  config/01-ce-auth-defaults.conf
  config/01-common-auth-defaults.conf
  config/01-common-collector-defaults.conf
  config/01-ce-info-services-defaults.conf
  ${CMAKE_CURRENT_BINARY_DIR}/config/01-ce-router-defaults.conf
  config/02-ce-collector-auth-generated.conf
  config/02-ce-condor-defaults.conf
  config/02-ce-pbs-defaults.conf
  config/02-ce-lsf-defaults.conf
  config/02-ce-sge-defaults.conf
  config/02-ce-slurm-defaults.conf
  config/02-ce-bosco-defaults.conf
  config/03-managed-fork-defaults.conf
  config/03-gratia-cleanup.conf
  config/05-ce-view-defaults.conf
  config/05-ce-health-defaults.conf
  contrib/apelscripts/50-ce-apel-defaults.conf
  DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce/config.d)
install(FILES
  config/99-condor-ce.conf
  config/50-condor-ce-defaults.conf
  contrib/bdii/99-ce-bdii.conf
  contrib/bdii/50-ce-bdii-defaults.conf
  DESTINATION
  ${SYSCONF_INSTALL_DIR}/condor/config.d)

set(HTCONDORCE_DIRS ${STATE_INSTALL_DIR}/run/condor-ce ${STATE_INSTALL_DIR}/log/condor-ce
  ${STATE_INSTALL_DIR}/log/condor-ce/user ${STATE_INSTALL_DIR}/lib/condor-ce ${STATE_INSTALL_DIR}/lib/condor-ce/spool
  ${STATE_INSTALL_DIR}/lib/condor-ce/spool/ceview ${STATE_INSTALL_DIR}/lib/condor-ce/spool/ceview/vos
  ${STATE_INSTALL_DIR}/lib/condor-ce/spool/ceview/metrics ${STATE_INSTALL_DIR}/lib/condor-ce/execute
  ${STATE_INSTALL_DIR}/lock/condor-ce ${STATE_INSTALL_DIR}/lock/condor-ce/user
  ${STATE_INSTALL_DIR}/lib/gratia/condorce_data ${SYSCONF_INSTALL_DIR}/logrotate.d)

foreach(dir IN ITEMS ${HTCONDORCE_DIRS})
  install(DIRECTORY DESTINATION ${dir})
  install(CODE "execute_process(COMMAND chown condor:condor ${dir})")
endforeach(dir)

set(STICKY_HTCONDORCE_DIRS ${STATE_INSTALL_DIR}/log/condor-ce/user ${STATE_INSTALL_DIR}/lock/condor-ce/user
  ${SYSCONF_INSTALL_DIR}/logrotate.d)

foreach(sticky_dir IN ITEMS ${STICKY_HTCONDORCE_DIRS})
  install(CODE "execute_process(COMMAND chmod 1777 ${sticky_dir})")
endforeach(sticky_dir)

install(FILES config/ce-status.cpf config/pilot-status.cpf DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce)
install(FILES templates/index.html templates/vos.html templates/metrics.html
	templates/health.html templates/header.html templates/pilots.html DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce/templates)
install(FILES config/condor-ce config/condor-ce-collector DESTINATION ${SYSCONF_INSTALL_DIR}/sysconfig)
install(FILES config/condor-ce-collector.logrotate  RENAME condor-ce-collector  DESTINATION ${SYSCONF_INSTALL_DIR}/logrotate.d)

install(FILES
  config/condor-ce.service
  config/condor-ce-collector.service
  config/condor-ce-collector-config.service
  config/condor-ce-collector-config.timer
  DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/systemd/system)

install(FILES config/condor-ce.conf config/condor-ce-collector.conf DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/tmpfiles.d)
