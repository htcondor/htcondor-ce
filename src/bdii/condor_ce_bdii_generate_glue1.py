#!/usr/bin/python

import os
import re
import sys
os.environ.setdefault('CONDOR_CONFIG', '/etc/condor-ce/condor_config')
import classad
import htcondor
import optparse
import collections

cluster_template = """
dn: GlueClusterUniqueID=%(cescheddname)s,mds-vo-name=resource,o=grid
GlueClusterName: %(sitename)s
GlueClusterService: %(cescheddname)s
GlueClusterUniqueID: %(cescheddname)s
GlueForeignKey: GlueCEUniqueID=%(ceunique)s
GlueForeignKey: GlueSiteUniqueID=%(sitename)s
objectClass: GlueClusterTop
objectClass: GlueCluster
objectClass: GlueSchemaVersion
objectClass: GlueInformationService
objectClass: GlueKey
GlueSchemaVersionMajor: 1
GlueSchemaVersionMinor: 2"""

service_template = """
dn: GlueServiceUniqueID=%(cescheddname)s.condorce,mds-vo-name=resource,o=grid
GlueServiceName: %(sitename)s-condorce
GlueServiceEndpoint: https://%(cepoolname)s/%(cescheddname)s
GlueServiceVersion: %(ceversion)s
GlueServiceType: HTCondorCE
GlueServiceStatus: %(status)s
GlueServiceStatusInfo: %(statusinfo)s
GlueServiceUniqueID: %(cescheddname)s.condorce
objectClass: GlueKey
objectClass: GlueTop
objectClass: GlueService
objectClass: GlueSchemaVersion
GlueSchemaVersionMajor: 1
GlueSchemaVersionMinor: 3"""

ce_template = """
dn: GlueCEUniqueID=%(ceunique)s,mds-vo-name=resource,o=grid
GlueCEName: condor
GlueCEInfoHostName: %(hostname)s
GlueCEStateStatus: %(cestatus)s
GlueCEInfoJobManager: HTCondorCE
GlueCEImplementationName: HTCondorCE
GlueCEImplementationVersion: %(ceversion)s
GlueCECapability: CPUScalingReferenceSI00=3100
GlueCEInfoContactString: condor %(cescheddname)s %(cepoolname)s
GlueCEInfoGatekeeperPort: 9619
GlueCEHostingCluster: %(cescheddname)s
GlueCEInfoLRMSType: %(batch)s
GlueCEInfoLRMSVersion: %(condorversion)s
GlueCEInfoTotalCPUs: %(totalcores)s
GlueCEStateFreeCPUs: %(idlecores)s
GlueCEPolicyAssignedJobSlots: %(busycores)s
GlueCEStateTotalJobs: %(totaljobs)s
GlueCEStateFreeJobSlots: %(idlecores)s
GlueCEStateWaitingJobs: %(idlejobs)s
GlueCEStateRunningJobs: %(runningjobs)s
%(acbr)s
GlueCEUniqueID: %(ceunique)s
GlueForeignKey: GlueClusterUniqueID=%(cescheddname)s
GlueInformationServiceURL: ldap://%(hostname)s:2135/mds-vo-name=resource,o=grid
objectClass: GlueCETop
objectClass: GlueCE
objectClass: GlueSchemaVersion
objectClass: GlueCEAccessControlBase
objectClass: GlueCEInfo
objectClass: GlueCEPolicy
objectClass: GlueCEState
objectClass: GlueInformationService
objectClass: GlueKey
GlueSchemaVersionMajor: 1
GlueSchemaVersionMinor: 2"""

subcluster_template = """
dn: GlueSubClusterUniqueID=%(cescheddname)s,GlueClusterUniqueID=%(cescheddname)s,mds-vo-name=resource,o=grid
GlueSubClusterName: %(sitename)s
GlueHostArchitecturePlatformType: x86_64
GlueHostProcessorOtherDescription: Cores=%(cores)s,Benchmark=%(hepspec_info)s
GlueHostBenchmarkSI00: 0
GlueHostBenchmarkSF00: 0
GlueHostMainMemoryRAMSize: 0
GlueHostMainMemoryVirtualSize: 0
GlueHostNetworkAdapterOutboundIP: TRUE
GlueHostNetworkAdapterInboundIP: TRUE
GlueHostArchitectureSMPSize: %(cores)s
GlueSubClusterPhysicalCPUs: %(cores)s
GlueSubClusterLogicalCPUs: %(cores)s
GlueSubClusterUniqueID: %(cescheddname)s
GlueChunkKey: GlueClusterUniqueID=%(cescheddname)s
objectClass: GlueClusterTop
objectClass: GlueSubCluster
objectClass: GlueSchemaVersion
objectClass: GlueHostApplicationSoftware
objectClass: GlueHostArchitecture
objectClass: GlueHostBenchmark
objectClass: GlueHostMainMemory
objectClass: GlueHostNetworkAdapter
objectClass: GlueHostOperatingSystem
objectClass: GlueHostProcessor
objectClass: GlueInformationService
objectClass: GlueKey
GlueSchemaVersionMajor: 1
GlueSchemaVersionMinor: 2"""

voview_template = """
dn: GlueVOViewLocalID=%(voname)s,GlueCEUniqueID=%(ceunique)s,mds-vo-name=resource,o=grid
GlueVOViewLocalID: %(voname)s
GlueCEStateFreeCPUs: %(idlecores)d
GlueCEStateTotalJobs: %(totalvojobs)d
GlueCEStateFreeJobSlots: %(idlecores)d
GlueCEStateRunningJobs: %(runningvojobs)d
GlueCEStateWaitingJobs: %(idlevojobs)d
GlueCEAccessControlBaseRule: VO:%(voname)s
GlueChunkKey: GlueCEUniqueID=%(ceunique)s
objectClass: GlueCETop
objectClass: GlueVOView
objectClass: GlueCEInfo
objectClass: GlueCEState
objectClass: GlueCEAccessControlBase
objectClass: GlueCEPolicy
objectClass: GlueKey
objectClass: GlueSchemaVersion
GlueSchemaVersionMajor: 1
GlueSchemaVersionMinor: 2"""

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

    hepspec_info = htcondor.param.get('HTCONDORCE_HEPSPEC_INFO')
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
    poolcoll = htcondor.Collector(opts.pool)
    for ad in poolcoll.query(htcondor.AdTypes.Startd, 'State=!="Owner"', ["State", "Cpus"]):
        if not ad.get('State') or not ad.get('Cpus'):
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

    info = { \
        'cepoolname': htcondor.param['COLLECTOR_HOST'],
        'cescheddname': schedd_name,
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
        'condorversion': htcondor.version(),
        'ceversion': ceversion,
        'cores': cores,
        'hepspec_info': hepspec_info,
    }
    if vonames:
        info['acbr'] = '\n'.join(['GlueCEAccessControlBaseRule: VO:%s' % vo for vo in vonames])

    print cluster_template % info
    print service_template % info
    print ce_template % info
    print subcluster_template % info

    for vo in vonames:
        vo_info = { \
            'voname': vo,
            'totalvojobs': total_vo_jobs.get(vo, 0),
            'idlevojobs': idle_vo_jobs.get(vo, 0),
            'runningvojobs': running_vo_jobs.get(vo, 0),
        }
        vo_info.update(info)
        print voview_template % vo_info

if __name__ == '__main__':
    main()

