
project(condor-ce)

cmake_minimum_required(VERSION 2.6)

set( HTCONDORCE_VERSION "1.6" CACHE INTERNAL "Version of the HTCondor-CE" )

set( CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake )

find_package( Classad REQUIRED )

find_package(PkgConfig)
pkg_check_modules( GLOBUS_RSL REQUIRED globus-rsl )

if( CMAKE_COMPILER_IS_GNUCXX )
  set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Werror" )
endif( CMAKE_COMPILER_IS_GNUCXX )

include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
if(COMPILER_SUPPORTS_CXX11)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
endif()

string(REPLACE ";" " " _GLOBUS_RSL_CFLAGS_OTHER "${GLOBUS_RSL_CFLAGS_OTHER}" )

link_directories ( ${GLOBUS_RSL_LIBRARY_DIRS} )
include_directories ( ${GLOBUS_RSL_INCLUDE_DIRS} ${CLASSAD_INCLUDE_DIRS} )

add_library ( eval_rsl MODULE src/rslConverter.cpp )
target_link_libraries ( eval_rsl ${GLOBUS_RSL_LIBRARIES} ${CLASSAD_LIBRARIES} )
set_property ( TARGET eval_rsl APPEND PROPERTY COMPILE_FLAGS "${_GLOBUS_RSL_CFLAGS_OTHER}" )

add_library ( classad_ce MODULE src/classad_ce.cpp )
target_link_libraries ( classad_ce ${CLASSAD_LIBRARIES} )

add_executable ( rsl_tester src/rslTester.cpp )
add_executable ( classad_ce_tester src/classad_ce_tester.cpp )
target_link_libraries ( classad_ce_tester ${CLASSAD_LIBRARIES} )
target_link_libraries ( rsl_tester ${CLASSAD_LIBRARIES} )

set(SHARE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}/share" CACHE PATH "Base directory for files which go to share/")
set(SYSCONF_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}/etc" CACHE PATH "Base directory for files which go to etc/")
set(CMAKE_INSTALL_LIBDIR "${CMAKE_INSTALL_PREFIX}/lib" CACHE PATH "Base directory for files which go to lib/")

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

install(TARGETS eval_rsl LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}/condor")
install(TARGETS classad_ce LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}/condor")

install(PROGRAMS src/condor-ce src/condor-ce-collector DESTINATION ${SYSCONF_INSTALL_DIR}/rc.d/init.d)
install(PROGRAMS src/condor_ce_startup src/condor_ce_startup_internal src/condor_ce_env_bootstrap src/condor_ce_client_env_bootstrap src/condor_ce_router_defaults src/osg-wrapper src/condor_ce_jobmetrics src/condor_ce_metric src/condor_ce_webapp DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce)
install(PROGRAMS src/condor_ce_config_generator src/condor_ce_config_val src/condor_ce_history src/condor_ce_hold src/condor_ce_info_status src/condor_ce_q src/condor_ce_qedit src/condor_ce_release src/condor_ce_rm src/condor_ce_submit src/condor_ce_version src/condor_ce_reconfig src/condor_ce_router_q src/condor_ce_status src/condor_ce_reschedule src/condor_ce_run src/condor_ce_trace src/condor_ce_ping src/condor_ce_off src/condor_ce_on src/condor_ce_restart src/condor_ce_job_router_info DESTINATION ${CMAKE_INSTALL_PREFIX}/bin)
install(FILES src/condor_ce_info_query.py src/condor_ce_tools.py DESTINATION ${PYTHON_SITELIB})
install(FILES src/htcondor_ce/__init__.py src/htcondor_ce/web.py src/htcondor_ce/rrd.py DESTINATION ${PYTHON_SITELIB}/htcondor_ce)

install(FILES config/condor_config config/condor_mapfile DESTINATION ${SYSCONF_INSTALL_DIR}/condor-ce)
install(FILES config/metrics.d/00-metrics-defaults.conf config/metrics.d/00-example-metrics.conf DESTINATION ${SYSCONF_INSTALL_DIR}/condor-ce/metrics.d)
install(FILES config/01-ce-collector.conf config/01-ce-collector-requirements.conf config/02-ce-auth-generated.conf config/01-ce-auth.conf config/01-common-auth.conf config/01-ce-router.conf config/02-ce-condor.conf config/02-ce-pbs.conf config/02-ce-lsf.conf config/02-ce-sge.conf config/03-ce-shared-port.conf config/03-managed-fork.conf config/04-ce-collector-auth.conf config/05-ce-webapp.conf config/05-ce-health.conf DESTINATION ${SYSCONF_INSTALL_DIR}/condor-ce/config.d)
install(FILES config/01-ce-collector-defaults.conf config/01-ce-auth-defaults.conf config/01-common-auth-defaults.conf config/01-common-collector-defaults.conf config/01-ce-info-services-defaults.conf config/01-ce-router-defaults.conf config/02-ce-condor-defaults.conf config/02-ce-pbs-defaults.conf config/02-ce-lsf-defaults.conf config/02-ce-sge-defaults.conf config/03-ce-shared-port-defaults.conf config/03-managed-fork-defaults.conf config/05-ce-webapp-defaults.conf config/05-ce-health-defaults.conf DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce/config.d)
install(FILES config/ce-status.cpf DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce)
install(FILES templates/index.html templates/vos.html templates/metrics.html DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce/templates)
install(FILES config/99-condor-ce.conf config/50-condor-ce-defaults.conf DESTINATION ${SYSCONF_INSTALL_DIR}/condor/config.d)
install(FILES config/condor-ce config/condor-ce-collector DESTINATION ${SYSCONF_INSTALL_DIR}/sysconfig)
install(FILES config/condor-ce-collector-generator.cron DESTINATION ${SYSCONF_INSTALL_DIR}/cron.d)
install(FILES config/condor-ce-collector.logrotate  RENAME condor-ce-collector  DESTINATION ${SYSCONF_INSTALL_DIR}/logrotate.d)
