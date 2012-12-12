class osg_ce_condor::install inherits osg_ce_condor {

  # We depend on yum priorities to select the right repo
  package { 'ce-yum-priorities':
    ensure  => present,
    name    => 'yum-plugin-priorities',
  }

  # Ask for condor, otherwise we might get empty-condor
  package { 'condor':
    ensure  => present,
    require => Package['ce-yum-priorities'],
  }

  package { 'condor-ce':
    ensure  => present,
    require => Package['condor'],
  }

  # Install condor-ce-$RMS
  package { $osg_ce_condor::rms:
    ensure  => present,
    require => Package['condor-ce'],
  }

  package { 'lcas-lcmaps-gt4-interface':
    ensure => present,
  }

}
