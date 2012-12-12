#
# Class: hostcert
#
# hostcert (host and http) distribution
# File distribution is done out-of-band.
#

class osg_ce_condor::hostcert {

  include osg-ca-certs

  file { '/etc/grid-security':
    ensure => directory,
    owner  => 'root',
    group  => 'root',
    mode   => '0755',
  }

  file { 'hostcert.pem':
    path    => '/etc/grid-security/hostcert.pem',
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    require => [ File['/etc/grid-security'], Class['osg-ca-certs'], ],
  }

  file { 'hostkey.pem':
    path    => '/etc/grid-security/hostkey.pem',
    owner   => 'root',
    group   => 'root',
    mode    => '0600',
    require => [ File['/etc/grid-security'], Class['osg-ca-certs'], ],
  }

}

