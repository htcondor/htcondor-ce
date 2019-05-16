
import os
import re
import json
import time
import types
import socket

import classad
htcondor = None

def check_htcondor():
    global htcondor
    if not htcondor:
        os.environ.setdefault('CONDOR_CONFIG', "/etc/condor-ce/condor_config")
        htcondor = __import__("htcondor")
    return htcondor


def _get_pool(environ):
    check_htcondor()
    environ_pool = None
    if environ and 'htcondorce.pool' in environ:
        environ_pool = environ['htcondorce.pool']
    if environ_pool:
        return environ_pool
    if not htcondor:
        return None

    return htcondor.param.get("HTCONDORCE_VIEW_POOL")


def _get_name(environ):
    environ_name = None
    if environ and 'htcondorce.name' in environ:
        environ_name = environ['htcondorce.name']
    if environ_name:
        return environ_name
    check_htcondor()
    if not htcondor:
        return _get_pool(environ)

    return htcondor.param.get("HTCONDORCE_VIEW_NAME")


def get_schedd_objs(environ=None):
    pool = _get_pool(environ)
    if pool:
        name = _get_name(environ)
        coll = htcondor.Collector(pool)
        if name:
            schedds = [coll.locate(htcondor.DaemonTypes.Schedd, name)]
        else:
            schedds = coll.locateAll(htcondor.DaemonTypes.Schedd)
        results = []
        for ad in schedds:
            if not ad.get("Name"):
                continue
            results.append((htcondor.Schedd(ad), ad['Name']))
        return results
    return [(htcondor.Schedd(), socket.getfqdn())]


def get_schedd_ads(environ):
    pool = _get_pool(environ)
    coll = htcondor.Collector(pool)
    if pool:
        name = _get_name(environ)
        if name:
            return [coll.query(htcondor.AdTypes.Schedd, "Name=?=%s" % classad.quote(name))[0]]
        else:
            return coll.query(htcondor.AdTypes.Schedd, "true")
    return [coll.locate(htcondor.DaemonTypes.Schedd)]


def get_schedd_statuses(environ={}):
    ads = get_schedd_ads(environ)
    results = {}
    for ad in ads:
        if 'Name' not in ad:
            continue

        for missing_attr in ['Status', 'IsOK', 'IsWarning', 'IsCritical']:
            if missing_attr in ad:
                continue
            if missing_attr not in htcondor.param:
                continue
            ad[missing_attr] = classad.ExprTree(htcondor.param[missing_attr])

        if 'Status' not in ad:
            results[ad['Name']] = 'Unknown'
        else:
            results[ad['Name']] = ad['Status'].eval()

    return results


def get_schedd_status(environ={}):
    statuses = get_schedd_statuses()
    keys = statuses.keys()
    keys.sort()
    return statuses[keys[0]]


def ad_to_json(ad):
    result = {}
    for key in ad:
        val_expr = ad.lookup(key)
        if classad.ExprTree("%s =?= UNDEFINED" % key).eval(ad):
            result[key] = {"_condor_type": "expr", "expr": val_expr.__repr__()}
        else:
            val = val_expr.eval()
            if isinstance(val, types.ListType) or isinstance(val, types.DictType):
                result[key] = {"_condor_type": "expr", "expr": val_expr.__repr__()}
            else:
                result[key] = val
    return result


def generate_queue_ad(resource_catalog, ce):
    queues = {}
    for entry in resource_catalog:

        queue = entry.get('Transform', {}).get('set_remote_queue', 'default')
        queues[queue] = {'ce': ce,
                         'max_wallclocktime': int(entry.get('MaxWallTime', 1440)),
                         'entry': entry.get('Name', ''),
                         'name': queue,
                         'status': 'Production',
                         'memory': int(entry.get('Memory')),
                         'cpus': int(entry.get('CPUs', 1)),
                         'votag': entry.get('VOTag', ''),
                         'subclusters': entry.get('Subclusters', [])
                        }
    return queues


def agis_data(environ):
    ads = get_schedd_ads(environ)
    results = {"ce_services": {}, "queues": {}, "failed_ces": [], "resource_groups": {}}
    for ad in ads:
        if 'Name' not in ad:
            continue
        try:
            ce_ad = {
                "endpoint": ad['CollectorHost'],
                "flavour": "HTCONDOR-CE",
                "jobmanager": ad['OSG_BatchSystems'].lower(),
                "name": "%s-CE-HTCondorCE-%s" % (ad['OSG_ResourceGroup'], ad['CollectorHost'].split(':')[0]),
                "site": ad['OSG_ResourceGroup'],
                "status": "Production",
                "type": "CE",
                "version": ad['HTCondorCEVersion']
            }
            rgroup = ad.get('OSG_ResourceGroup')
            if rgroup:
                ce_ad['resource_group'] = rgroup
                results['resource_groups'][rgroup] = {'name': rgroup}
            default_queue_ad = {
                "default": {
                    "ce": ad['OSG_Resource'],
                    "max_cputime": 1440,
                    "max_wallclocktime": 1440,
                    "name": "default",
                    "status": "Production"
                }
            }
            results['ce_services'][ad['OSG_Resource']] = ce_ad
            results['queues'][ad['OSG_Resource']] = default_queue_ad
            queue_ad = generate_queue_ad(ad['OSG_ResourceCatalog'], ad['OSG_Resource'])
            if queue_ad:
                results['queues'][ad['OSG_Resource']] = queue_ad
        except KeyError as e:
            # No way to log an error, stderr doesn't work, stdout, or logging module
            # So, just add it to the json as "failed_ces"
            results['failed_ces'].append(ad['Name'])

    return results

def get_spooldir():
    check_htcondor()
    spooldir = htcondor.param.get("HTCONDORCE_VIEW_SPOOL")
    if not spooldir:
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        spooldir = "tmp"
    return spooldir

