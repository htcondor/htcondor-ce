class osg_ce_condor::service inherits osg_ce_condor {

  service { 'condor-ce':
    ensure     => running,
    hasstatus  => true,
    hasrestart => true,
    enable     => true,
    require    => Package['condor-ce'],
  }

}
