#
# Class: osg_ce_condor
#
class osg_ce_condor (
  $gums_server = params_lookup( 'gums_server' ),
  $rms         = params_lookup( 'rms' ),
) inherits osg_ce_condor::params {

  stage { 'pre': before => Stage['main'] }

  # Install the RPMs first
  class { 'osg_ce_condor::install': stage => 'pre' }

  include osg_ce_condor::config, osg_ce_condor::service
  include osg_ce_condor::hostcert

}
