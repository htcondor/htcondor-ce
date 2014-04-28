
project(condor-ce)

cmake_minimum_required(VERSION 2.6)

set( CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake )

find_package( Classad REQUIRED )

find_package(PkgConfig)
pkg_check_modules( GLOBUS_RSL REQUIRED globus-rsl )

if( CMAKE_COMPILER_IS_GNUCXX )
  set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Werror" )
endif( CMAKE_COMPILER_IS_GNUCXX )

string(REPLACE ";" " " _GLOBUS_RSL_CFLAGS_OTHER "${GLOBUS_RSL_CFLAGS_OTHER}" )

link_directories ( ${GLOBUS_RSL_LIBRARY_DIRS} )
include_directories ( ${GLOBUS_RSL_INCLUDE_DIRS} ${CLASSAD_INCLUDE_DIRS} )

add_library ( eval_rsl MODULE src/rslConverter.cpp )
target_link_libraries ( eval_rsl ${GLOBUS_RSL_LIBRARIES} ${CLASSAD_LIBRARIES}
)
set_property ( TARGET eval_rsl APPEND PROPERTY COMPILE_FLAGS
"${_GLOBUS_RSL_CFLAGS_OTHER}" )

add_executable ( rsl_tester src/rslTester.cpp )
target_link_libraries ( rsl_tester ${CLASSAD_LIBRARIES} )

set(SHARE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}/share" CACHE PATH "Base directory for files which go to share/")
set(SYSCONF_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}/etc" CACHE PATH "Base directory for files which go to etc/")
set(CMAKE_INSTALL_LIBDIR "${CMAKE_INSTALL_PREFIX}/lib" CACHE PATH "Base directory for files which go to lib/")

configure_file (
  "${PROJECT_SOURCE_DIR}/config/01-ce-router.conf.in"
  "${CMAKE_CURRENT_BINARY_DIR}/config/01-ce-router.conf"
)

configure_file (
  "${PROJECT_SOURCE_DIR}/config/01-ce-router-defaults.conf.in"
  "${CMAKE_CURRENT_BINARY_DIR}/config/01-ce-router-defaults.conf"
)

install(TARGETS eval_rsl LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}/condor")

install(PROGRAMS src/condor-ce DESTINATION ${SYSCONF_INSTALL_DIR}/rc.d/init.d)
install(PROGRAMS src/condor_ce_env_bootstrap src/condor_ce_router_defaults src/osg-wrapper DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce)
install(PROGRAMS src/condor_ce_config_val src/condor_ce_history src/condor_ce_hold src/condor_ce_q src/condor_ce_qedit src/condor_ce_release src/condor_ce_rm src/condor_ce_submit src/condor_ce_version src/condor_ce_reconfig src/condor_ce_router_q src/condor_ce_status src/condor_ce_reschedule src/condor_ce_run src/condor_ce_trace src/condor_ce_ping src/condor_ce_off src/condor_ce_on src/condor_ce_restart DESTINATION ${CMAKE_INSTALL_PREFIX}/bin)

install(FILES config/condor_config config/condor_mapfile DESTINATION ${SYSCONF_INSTALL_DIR}/condor-ce)
install(FILES config/01-ce-auth.conf config/01-common-auth.conf config/01-ce-router.conf config/02-ce-condor.conf config/02-ce-pbs.conf config/03-ce-shared-port.conf DESTINATION ${SYSCONF_INSTALL_DIR}/condor-ce/config.d)
install(FILES config/01-ce-auth-defaults.conf config/01-common-auth-defaults.conf config/01-ce-router-defaults.conf config/02-ce-condor-defaults.conf config/02-ce-pbs-defaults.conf config/03-ce-shared-port-defaults.conf DESTINATION ${SHARE_INSTALL_PREFIX}/condor-ce/config.d)
install(FILES config/99-condor-ce.conf config/99-condor-ce-defaults.conf DESTINATION ${SYSCONF_INSTALL_DIR}/condor/config.d)
install(FILES config/condor-ce DESTINATION ${SYSCONF_INSTALL_DIR}/sysconfig)

