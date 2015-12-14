#!/usr/bin/env python

import os
import re
import datetime
import sys
import subprocess
import ConfigParser
os.environ.setdefault('CONDOR_CONFIG', '/etc/condor-ce/condor_config')
import classad
import htcondor
import optparse
import collections
import time
import socket
import struct
import logging
try:
    from kazoo.client import KazooClient
    from kazoo.exceptions import LockTimeout
except ImportError:
    pass

logging.basicConfig()

service_template = """
dn: GLUE2ServiceID=%(cescheddname)s_ComputingElement,GLUE2GroupID=resource,o=glue
GLUE2ServiceType: %(gocservice)s
GLUE2ServiceID: %(cescheddname)s_ComputingElement
objectClass: GLUE2Entity
objectClass: GLUE2Service
objectClass: GLUE2ComputingService
GLUE2ServiceQualityLevel: production
GLUE2EntityOtherInfo: InfoProviderName=condorce-glue2-computingservice-static
GLUE2EntityOtherInfo: InfoProviderVersion=1.1
GLUE2EntityOtherInfo: InfoProviderHost=%(cescheddname)s
GLUE2ServiceComplexity: endpointType=2, share=20, resource=1
GLUE2ServiceCapability: executionmanagement.jobexecution
GLUE2EntityName: Computing Service %(cescheddname)s_ComputingElement
GLUE2ServiceAdminDomainForeignKey: %(sitename)s
GLUE2EntityCreationTime: %(dateandtime)s"""

resource_template = """
dn: GLUE2ResourceID=%(cescheddname)s,GLUE2ServiceID=%(cescheddname)s_ComputingElemen
 t,GLUE2GroupID=resource,o=glue
GLUE2ExecutionEnvironmentMainMemorySize: 2000
GLUE2ExecutionEnvironmentOSFamily: linux
GLUE2ExecutionEnvironmentCPUModel: Xeon
GLUE2EntityName: 5(cescheddname)s
GLUE2ExecutionEnvironmentCPUMultiplicity: singlecpu-multicore
GLUE2ExecutionEnvironmentVirtualMemorySize: 2048
GLUE2ExecutionEnvironmentConnectivityIn: FALSE
GLUE2ExecutionEnvironmentCPUClockSpeed: 2800
GLUE2ExecutionEnvironmentCPUVendor: intel
GLUE2ExecutionEnvironmentOSName: ScientificCERNSLC
GLUE2ResourceID: %(cescheddname)s
GLUE2ExecutionEnvironmentComputingManagerForeignKey: %(cescheddname)s_ComputingElement_Manager
GLUE2ExecutionEnvironmentPlatform: amd64
GLUE2ResourceManagerForeignKey: %(cescheddname)s_ComputingElement_Manager
objectClass: GLUE2Entity
objectClass: GLUE2Resource
objectClass: GLUE2ExecutionEnvironment
GLUE2ExecutionEnvironmentCPUVersion: Intel Core i7 9xx (Nehalem Class Core i7)
GLUE2ExecutionEnvironmentOSVersion: 6.7
GLUE2ExecutionEnvironmentConnectivityOut: TRUE
GLUE2ExecutionEnvironmentTotalInstances: %(totalinstances)d
GLUE2ExecutionEnvironmentLogicalCPUs: %(cores)s
GLUE2EntityCreationTime: %(dateandtime)s
GLUE2ExecutionEnvironmentCPUTimeScalingFactor: 1
GLUE2EntityOtherInfo: InfoProviderName=condorce-glue2-executionenvironment-static
GLUE2EntityOtherInfo: InfoProviderVersion=1.1
GLUE2EntityOtherInfo: InfoProviderHost=%(cescheddname)s
GLUE2EntityOtherInfo: SmpSize=2
GLUE2EntityOtherInfo: Cores=0
GLUE2ExecutionEnvironmentWallTimeScalingFactor: 1
GLUE2ExecutionEnvironmentPhysicalCPUs:%(cores)s
GLUE2EntityCreationTime: %(dateandtime)s
GLUE2ComputingShareTotalJobs: %(totaljobs)d
GLUE2ComputingShareRunningJobs: %(runningjobs)d
GLUE2ComputingShareMaxWaitingJobs: 349952
GLUE2ComputingShareRequestedSlots: %(idlejobs)d"""

endpoint_template = """
dn: GLUE2EndpointID=%(cescheddname)s_%(gocservice)s,GLUE2ServiceID=%(cescheddname)s
 .ch_ComputingElement,GLUE2GroupID=resource,o=glue
GLUE2ComputingEndpointStaging: staginginout
GLUE2EndpointQualityLevel: production
GLUE2EndpointImplementor: %(gocservice)s
GLUE2EndpointHealthStateInfo: condor (pid 7035) is running...[  OK  ]
GLUE2EntityOtherInfo: HostDN=CN=%(cescheddname)s,OU=computers,DC=cern,DC=ch
GLUE2EntityOtherInfo: InfoProviderName=htcondor-ce-glue2-endpoint-static
GLUE2EntityOtherInfo: InfoProviderVersion=1.1
GLUE2EntityOtherInfo: InfoProviderHost=%(cescheddname)s
GLUE2EntityOtherInfo: MiddlewareName=OSG
GLUE2EntityOtherInfo: MiddlewareVersion=%(ceversion)s
GLUE2EntityOtherInfo: ArgusEnabled=TRUE
GLUE2EndpointCapability: executionmanagement.jobexecution
GLUE2EndpointHealthState: ok
GLUE2EndpointServiceForeignKey: _ComputingElement
GLUE2EntityName: %(cescheddname)s_%(gocservice)s
GLUE2EndpointTechnology: webservice
GLUE2EndpointWSDL: https://%(cescheddname)s:8443/
GLUE2EndpointInterfaceName: org.opensciencegrid.htcondorce
GLUE2ComputingEndpointComputingServiceForeignKey: %(cescheddname)s_ComputingEleme
 nt
GLUE2EndpointURL: https://%(cescheddname)s:8443/
GLUE2EndpointDowntimeInfo: See the GOC DB for downtimes: https://goc.egi.eu/
GLUE2EndpointImplementationVersion: 1.0.0
GLUE2EndpointSemantics: https://twiki.opensciencegrid.org/bin/view/Documentation/Release3/HTCondorCEOverview
GLUE2EndpointIssuerCA: CN=CERN Grid Certification Authority,DC=cern,DC=ch
GLUE2EndpointImplementationName: HTCONDORCE
GLUE2EndpointInterfaceVersion: 1.0
GLUE2EndpointSupportedProfile: http://www.ws-i.org/Profiles/BasicProfile-1.0.h
 tml
objectClass: GLUE2Entity
objectClass: GLUE2Endpoint
objectClass: GLUE2ComputingEndpoint
%(endpointtrustedcas)s
GLUE2ComputingEndpointJobDescription: condor:sdl
GLUE2EndpointID: %(cescheddname)s_%(gocservice)s
GLUE2EndpointServingState: production
GLUE2EndpointStartTime: %(startdate)s
GLUE2EntityCreationTime: %(dateandtime)s"""

manager_template = """
dn: GLUE2ManagerID=%(cescheddname)s_ComputingElement_Manager,GLUE2ServiceID=%(cescheddname)s_ComputingElement,GLUE2GroupID=resource,o=glue
GLUE2ComputingManagerComputingServiceForeignKey: %(cescheddname)s_ComputingElement
GLUE2ManagerProductName: HTCondor
objectClass: GLUE2Entity
objectClass: GLUE2Manager
objectClass: GLUE2ComputingManager
GLUE2EntityOtherInfo: InfoProviderName=condorce-glue2-manager-static
GLUE2EntityOtherInfo: InfoProviderVersion=1.1
GLUE2EntityOtherInfo: InfoProviderHost=%(cescheddname)s
GLUE2EntityOtherInfo: CPUScalingReferenceSI00=381
GLUE2EntityOtherInfo: CPUScalingReferenceSI00=1000
GLUE2EntityOtherInfo: Share=atlas:22
GLUE2EntityOtherInfo: Share=alice:20
GLUE2EntityOtherInfo: Share=cms:24
GLUE2EntityOtherInfo: Share=lhcb:8
GLUE2EntityOtherInfo: Share=vo.gear.cern.ch:0
GLUE2EntityOtherInfo: Share=geant4:0
GLUE2EntityOtherInfo: Share=dteam:0
GLUE2EntityOtherInfo: Share=ilc:0
GLUE2EntityOtherInfo: Share=vo.compass.cern.ch:0
GLUE2ManagerServiceForeignKey: %(cescheddname)s_ComputingElement
GLUE2EntityName: Computing Manager on %(cescheddname)s
GLUE2ManagerID: %(cescheddname)s_ComputingElement_Manager
GLUE2ManagerProductVersion: %(ceversion)s
GLUE2EntityCreationTime: %(dateandtime)s
GLUE2ComputingManagerTotalPhysicalCPUs: 8
GLUE2ComputingManagerTotalLogicalCPUs: 8"""

benchmark_template="""
dn: GLUE2BenchmarkID=%(cescheddname)s_hep-spec06,GLUE2ResourceID=%(cescheddname)s,GLUE2ServiceID=%(cescheddname)s_ComputingElement,GLUE2GroupID=resource,GLUE2DomainID=%(sitename)s,o=glue
GLUE2EntityOtherInfo: InfoProviderName=htcondorce-glue2-benchmark-static
GLUE2EntityOtherInfo: InfoProviderVersion=1.1
GLUE2EntityOtherInfo: InfoProviderHost=%(cescheddname)s
GLUE2BenchmarkID: %(cescheddname)s_hep-spec06
GLUE2BenchmarkType: hep-spec06
objectClass: GLUE2Entity
objectClass: GLUE2Benchmark
GLUE2BenchmarkValue: %(hepspec_info)s
GLUE2BenchmarkExecutionEnvironmentForeignKey: %(cescheddname)s
GLUE2BenchmarkComputingManagerForeignKey: %(cescheddname)s_ComputingElement_Manager
GLUE2EntityName: Benchmark hep-spec06
GLUE2EntityCreationTime: %(dateandtime)s
"""

shares_template = """
dn: GLUE2ShareID=grid_%(voname)s_%(voname)s_%(cescheddname)s_ComputingElement,GLUE2ServiceID=%(cescheddname)s_ComputingElement,GLUE2GroupID=resource,o=glue
GLUE2ComputingShareMinCPUTime: 0
GLUE2ComputingShareComputingServiceForeignKey: %(cescheddname)s_ComputingElement
GLUE2ComputingShareComputingEndpointForeignKey: %(cescheddname)s_%(gocservice)s
GLUE2EntityOtherInfo: HTCondorCEId=%(cescheddname)s:9619/htcondorce-condor-group_%(voname)s
GLUE2EntityOtherInfo: ServiceType=%(gocservice)s
GLUE2EntityOtherInfo: InfoProviderName=condor-ce-glue2-share-static
GLUE2EntityOtherInfo: InfoProviderVersion=1.1
GLUE2EntityOtherInfo: InfoProviderHost=%(cescheddname)s
GLUE2ShareServiceForeignKey: %(cescheddname)s_ComputingElement
GLUE2ShareDescription: Share of grid_%(voname)s for %(voname)s
GLUE2ComputingShareMinWallTime: 0
GLUE2ShareResourceForeignKey: %(cescheddname)s
GLUE2ComputingShareGuaranteedVirtualMemory: 0
GLUE2ComputingShareExecutionEnvironmentForeignKey: %(cescheddname)s
GLUE2ComputingShareGuaranteedMainMemory: 0
GLUE2ShareID: grid_%(voname)s_%(voname)s_%(cescheddname)s_ComputingElement
GLUE2ComputingShareMappingQueue: grid_%(voname)s
GLUE2ComputingShareUsedSlots: 0
objectClass: GLUE2Entity
objectClass: GLUE2Share
objectClass: GLUE2ComputingShare
GLUE2ShareEndpointForeignKey: %(cescheddname)s_%(gocservice)s
GLUE2ComputingShareDefaultCPUTime: 10080
GLUE2ComputingShareMaxTotalCPUTime: 10080
GLUE2ComputingShareMaxMainMemory: 3906
GLUE2ComputingShareDefaultWallTime: 30240
GLUE2ComputingShareMaxSlotsPerJob: 8
GLUE2ComputingShareMaxTotalJobs: 30000
GLUE2ComputingShareMaxCPUTime: 10080
GLUE2ComputingShareMaxWallTime: 30240
GLUE2ComputingShareMaxMultiSlotWallTime: 30240
GLUE2ComputingShareServingState: production
GLUE2ComputingShareMaxVirtualMemory: 17916
GLUE2ComputingShareMaxUserRunningJobs: 10000
GLUE2ComputingShareMaxRunningJobs: 10000
GLUE2ComputingShareWaitingJobs: %(idlevojobs)d
GLUE2ComputingShareEstimatedAverageWaitingTime: 90
GLUE2ComputingShareEstimatedWorstWaitingTime: 180
GLUE2ComputingShareFreeSlots: %(idlecores)d
GLUE2EntityCreationTime: %(dateandtime)s
GLUE2ComputingShareTotalJobs: %(totalvojobs)d
GLUE2ComputingShareRunningJobs: %(runningvojobs)d
GLUE2ComputingShareMaxWaitingJobs: 349952
GLUE2ComputingShareRequestedSlots: %(idlevojobs)d"""


class PublicationLeader(object):

    def __init__(self, leader):
        self.leader = leader
        self.is_leader = False

    def should_publish(self):
        self.is_leader = self.leader == socket.getfqdn()

    def update_ts(self):
        pass

    def leader(self):
        return self.is_leader


class TimeStampLeader(PublicationLeader):

    def __init__(self, zk_hosts, bdii_path):
        self.zk_hosts = zk_hosts
        self.zk = KazooClient(self.zk_hosts)
        self.bdii_path = bdii_path
        self.is_leader = False

    def pack_ts(self, input_dt):
        return struct.pack('f', self.gen_ts(input_dt))

    def gen_ts(self, input_dt):
        return time.mktime(input_dt.timetuple())

    def does_exist(self):
        if self.zk.exists(self.bdii_path) is not None:
            return True
        else:
            return False

    def is_stale(self, current_time):
        data, stat = self.zk.get(self.bdii_path)
        if data == '':
            return True
        last_updated_timestamp = struct.unpack('f',data)[0]
        if last_updated_timestamp <= (self.gen_ts(current_time) - 120):
            return True
        else:
            return False

    def should_publish(self):
        self.zk.start()
        current_time = datetime.datetime.utcnow()
        if not self.does_exist():
            self.zk.create(self.bdii_path, self.pack_ts(current_time))
            self.is_leader = True
            return self.is_leader
        bdii_lock = self.zk.Lock(self.bdii_path, socket.getfqdn())
        try:
            lock_acquired = bdii_lock.acquire(5.0)
            if lock_acquired:
                self.is_leader = self.is_stale(current_time)
                bdii_lock.release()
                self.zk.stop()
                return self.is_leader
        except LockTimeout:
            # Another Compute Element has the lock
            pass
        return False

    def update_ts(self):
        if self.is_leader:
            self.zk.start()
            current_ts = self.gen_ts(datetime.datetime.utcnow())
            self.zk.set(self.bdii_path, struct.pack('f', current_ts))
            self.zk.stop()


class TrustedCAPopulator(object):

    def __init__(self):
        self.certs_path = '/etc/grid-security/certificates'

    def get_certs(self):
        return [cert for cert in os.listdir(self.certs_path) if os.path.splitext(cert)[-1].lower() == '.pem']

    def format_rfc2253(self, cert):
        cmd = ['/usr/bin/openssl', 'x509', '-noout', '-subject', '-nameopt', 'RFC2253', '-in', os.path.join(self.certs_path, cert)]
        cp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return cp.communicate()[0].rstrip('\n').replace('subject= ','').lstrip()

    def populate(self):
        """
        Gets a list of all trustedcas from /etc/grid-security/certificates
        Will be improved, but pyOpenssl currently doesn't allow RFC2253 output.
        """
        certs = self.get_certs()
        trusted_cas = [self.format_rfc2253(cert) for cert in certs]
        return '\n'.join(["GLUE2EndpointTrustedCA: {0}".format(tca) for tca in trusted_cas])

def leader_config():
    config = ConfigParser.SafeConfigParser()
    config.read('/etc/condor-ce/bdii.cfg')
    return config

def parse_opts():
    parser = optparse.OptionParser()
    parser.add_option("-p", "--pool", default=None, help="Batch system pool to query.", dest="pool")
    parser.add_option("-c", "--cepool", default=None, help="CE pool to query.", dest="cepool")
    parser.add_option("-n", "--name", default=None, help="Name of schedd to query.", dest="name")
    opts, _ = parser.parse_args()
    if not opts.pool:
        opts.pool = htcondor.param['JOB_ROUTER_SCHEDD2_POOL']
    return opts

def main():
    opts = parse_opts()
    if not opts.cepool:
        coll = htcondor.Collector()
    else:
        coll = htcondor.Collector(opts.cepool)
    if not opts.name:
        schedd_ad = coll.locate(htcondor.DaemonTypes.Schedd)
    else:
        schedd_ad = coll.locate(htcondor.DaemonTypes.Schedd, opts.name)
    sitename = htcondor.param.get('OSG_ResourceGroup', htcondor.param.get('HTCONDORCE_SiteName'))
    if not sitename:
        print >> sys.stderr, "Neither OSG_ResourceGroup nor HTCONDORCE_SiteName set in config file."
        sys.exit(1)
    batch = htcondor.param.get('OSG_BatchSystems', htcondor.param.get('HTCONDORCE_BatchSystem', 'Condor')).split(",")[0]
    status = htcondor.param.get('HTCONDORCE_Status', 'Production')
    hepspec_info = htcondor.param.get('HTCONDORCE_HEPSPEC_INFO').split('-')[0]
    if not hepspec_info:
        print >> sys.stderr, "HTCONDORCE_HEPSPEC_INFO not provided."
        sys.exit(1)
    cores = htcondor.param.get('HTCONDORCE_CORES')
    if not cores:
        print >> sys.stderr, "HTCONDORCE_CORES not available."
        sys.exit(1)
    schedd_name = schedd_ad['Name']
    schedd = htcondor.Schedd(schedd_ad)
    query = schedd.xquery("x509userproxyvoname isnt undefined", ["JobStatus", "x509userproxyvoname"])
    idle_vo_jobs = collections.defaultdict(int)
    running_vo_jobs = collections.defaultdict(int)
    total_vo_jobs = collections.defaultdict(int)
    for job in query:
        if not job.get("JobStatus") or not job.get("x509userproxyvoname"):
            continue
        total_vo_jobs[job['x509userproxyvoname']] += 1
        if job['JobStatus'] == 1:
            idle_vo_jobs[job['x509userproxyvoname']] += 1
        elif job['JobStatus'] == 2:
            running_vo_jobs[job['x509userproxyvoname']] += 1
    idle_cores = 0
    busy_cores = 0
    total_cores = 0
    leader_election = htcondor.param.get('HTCONDORCE_BDII_ELECTION')
    if leader_election == 'ZOOKEEPER':
        zkhosts = htcondor.param.get('HTCONDORCE_BDII_ZKHOSTS')
        leader = TimeStampLeader(zkhosts, "/htcondor/bdii_update")
    else:
        leader = PublicationLeader(htcondor.param.get('HTCONDORCE_BDII_LEADER'))
    leader.should_publish()
    poolcoll = htcondor.Collector(opts.pool)
    hosts = poolcoll.query(htcondor.AdTypes.Collector, True, ['HostsUnclaimed'])[0]
    total_instances = hosts.get('HostsUnclaimed', 0)
    if not leader.leader():
        total_instances = 0
    for ad in poolcoll.query(htcondor.AdTypes.Startd, 'State=!="Owner"', ["State", "Cpus"]):
        if not ad.get('State') or not ad.get('Cpus') or not leader.leader():
            continue
        total_cores += ad['Cpus']
        if ad['State'] == 'Unclaimed':
            idle_cores += ad['Cpus']
        elif ad['State'] == 'Claimed':
            busy_cores += ad['Cpus']
    vonames = set()
    vonames.update(idle_vo_jobs.keys())
    vonames.update(running_vo_jobs.keys())
    vonames.update([i.strip() for i in re.split('\s*,?\s*', htcondor.param.get('HTCONDORCE_VONAMES', '')) if i])
    try:
        if htcondor.SecMan().ping(schedd_ad, "READ")['AuthorizationSucceeded']:
            cestatus = 'OK'
        else:
            cestatus = 'CRITICAL'
        cestatusinfo = 'Authorization ping successful'
    except Exception, e:
        cestatus = 'UNKNOWN'
        cestatusinfo = 'Authorization ping failed: %s' % str(e)
    ceversion = classad.ExprTree(htcondor.param['HTCondorCEVersion']).eval()
    isodatetime = datetime.datetime.utcnow()
    dateandtime = isodatetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    ca_pop = TrustedCAPopulator()
    trustedcas = ca_pop.populate()
    constraint = 'Machine =?= "{0}"'.format(schedd_name)
    starttimequery = coll.query(htcondor.AdTypes.Schedd, constraint, ['DaemonStartTime'])
    scheddstarttime = starttimequery[0]['DaemonStartTime']
    info = { \
        'cepoolname': htcondor.param['COLLECTOR_HOST'],
        'cescheddname': schedd_name,
        'gocservice': 'org.opensciencegrid.htcondorce',
        'idlecores': idle_cores,
        'ceunique': '%s/%s-condor' % (htcondor.param['COLLECTOR_HOST'], schedd_name),
        'statusinfo': cestatusinfo,
        'cestatus': status,
        'status': cestatus,
        'sitename': sitename,
        'batch': batch,
        'hostname': htcondor.param['FULL_HOSTNAME'],
        'totalcores': total_cores,
        'busycores': busy_cores,
        'runningjobs': sum(running_vo_jobs.values()),
        'idlejobs': sum(idle_vo_jobs.values()),
        'totaljobs': sum(total_vo_jobs.values()),
        'totalinstances': total_instances,
        'condorversion': htcondor.version(),
        'ceversion': ceversion,
        'cores': cores,
        'hepspec_info': hepspec_info,
        'endpointtrustedcas': trustedcas,
        'dateandtime': dateandtime,
        'startdate': scheddstarttime
           }
    if vonames:
        info['acbr'] = '\n'.join(['GlueCEAccessControlBaseRule: VO:%s' % vo for vo in vonames])
    print service_template % info
    print resource_template % info
    print endpoint_template % info
    print manager_template % info
    print benchmark_template % info
    for vo in vonames:
        vo_info = { \
            'voname': vo,
            'totalvojobs': total_vo_jobs.get(vo, 0),
            'idlevojobs': idle_vo_jobs.get(vo, 0),
            'runningvojobs': running_vo_jobs.get(vo, 0),
                  }
        vo_info.update(info)
        print shares_template % vo_info
    leader.update_ts()

if __name__ == '__main__':
    main()

