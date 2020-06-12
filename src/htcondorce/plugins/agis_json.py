import re
import json
import traceback

from htcondorce import web_utils


OK_STATUS = '200 OK'


def _headers(content_type):
    return [('Content-type', content_type),
            ('Cache-Control', 'max-age=60, public')]


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
    ads = web_utils.get_schedd_ads(environ)
    results = {"ce_services": {}, "queues": {}, "failed_ces": {}, "resource_groups": {}}
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
        except (KeyError, TypeError):
            # No way to log an error, stderr doesn't work, stdout, or logging module
            # So, just add it to the json as "failed_ces"
            error = traceback.format_exc()
            results['failed_ces'][ad['Name']] = error

    return results


def agis_json(environ, start_response):

    results = agis_data(environ)

    start_response(OK_STATUS, _headers('application/json'))

    return [ json.dumps(results) ]


urls = [
    (re.compile(r'^json/+agis-compat$'), agis_json),
]