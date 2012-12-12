class osg_ce_condor::config {

  file { '/etc/lcmaps.db':
    ensure  => present,
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    content => template('osg_ce_condor/lcmaps.db.erb'),
  }

  file { '/etc/gums/gums-client.properties':
    ensure  => present,
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    content => template('osg_ce_condor/gums-client.properties.erb'),
  }

  file { '/etc/blah.config':
    ensure  => present,
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    source  => 'puppet:///modules/osg_ce_condor/blah.config',
  }

  file { '/etc/condor-ce/config.d':
    ensure  => directory,
    recurse => true,
    purge   => true,
    force   => true,
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    source  => 'puppet:///modules/osg_ce_condor/config.d',
    notify  => Service['condor-ce'],
  }

  file { '/etc/condor-ce/condor_mapfile':
    ensure  => present,
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    source  => 'puppet:///modules/osg_ce_condor/condor_mapfile',
    notify  => Service['condor-ce'],
  }

  file { '/etc/grid-security/gsi-authz.conf':
    ensure  => present,
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    source  => 'puppet:///modules/osg_ce_condor/gsi-authz.conf',
  }

  file { '/etc/sysconfig/condor-ce':
    ensure  => present,
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    source  => 'puppet:///modules/osg_ce_condor/sysconfig-condor-ce',
  }

}
