
import os
import re
import json
import time
import types
import socket
import wsgiref.util
import xml.sax.saxutils
import urlparse

import genshi.template

import classad
htcondor = None

import htcondor_ce.rrd

_initialized = None
_loader = None
_view = None
g_is_multice = False

def check_initialized(environ):
    global _initialized
    global _loader
    global _cp
    global htcondor
    if not _initialized:
        if 'htcondorce.templates' in environ:
            _loader = genshi.template.TemplateLoader(environ['htcondorce.templates'], auto_reload=True)
        else:
            _loader = genshi.template.TemplateLoader('/usr/share/condor-ce/templates', auto_reload=True)
        ce_config = environ.get('htcondorce.config', '/etc/condor-ce/condor_config')
        _check_htcondor()
        _initialized = True


def _check_htcondor():
    global _initialized
    global htcondor
    if not _initialized and not htcondor:
        os.environ.setdefault('CONDOR_CONFIG', "/etc/condor-ce/condor_config")
        htcondor = __import__("htcondor")


def _get_pool(environ):
    environ_pool = None
    if environ and 'htcondorce.pool' in environ:
        environ_pool = environ['htcondorce.pool']
    if environ_pool:
        return environ_pool
    _check_htcondor()
    if not htcondor:
        return None

    return htcondor.param.get("HTCONDORCE_VIEW_POOL")


def _get_name(environ):
    environ_name = None
    if environ and 'htcondorce.name' in environ:
        environ_name = environ['htcondorce.name']
    if environ_name:
        return environ_name
    _check_htcondor()
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


def get_spooldir():
    _check_htcondor()
    spooldir = htcondor.param.get("HTCONDORCE_VIEW_SPOOL")
    if not spooldir:
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        spooldir = "tmp"
    return spooldir


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


def schedds(environ, start_response):
    ads = get_schedd_ads(environ)
    results = {}
    for ad in ads:
        if 'Name' not in ad:
            continue
        results[ad['Name']] = ad_to_json(ad)

    status = '200 OK'
    headers = [('Content-type', 'application/json'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    return [ json.dumps(results) ]

def agis_json(environ, start_response):
    ads = get_schedd_ads(environ)
    results = { "ce_services": {}, "queues": {}, "failed_ces": []}
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
            queue_ad = {
                "cms": {
                    "ce": ad['OSG_Resource'],
                    "max_cputime": 1440,
                    "max_wallclocktime": 1440,
                    "name": "cms",
                    "status": "Production"
                },
                "atlas": {
                    "ce": ad['OSG_Resource'],
                    "max_cputime": 1440,
                    "max_wallclocktime": 1440,
                    "name": "atlas",
                    "status": "Production"
                }
            }
            results['ce_services'][ad['OSG_Resource']] = ce_ad
            results['queues'][ad['OSG_Resource']] = queue_ad
        except KeyError as e:
            # No way to log an error, stderr doesn't work, stdout, or logging module
            # So, just add it to the json as "failed_ces"
            results['failed_ces'].append(ad['Name'])

    status = '200 OK'
    headers = [('Content-type', 'application/json'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    return [ json.dumps(results) ]



def schedd(environ, start_response):
    ads = get_schedd_ads(environ)
    results = {}
    for ad in ads:
        if 'Name' not in ad:
            continue
        results[ad['Name']] = ad
    keys = results.keys()
    keys.sort()
    result = ad_to_json(results[keys[0]])

    status = '200 OK'
    headers = [('Content-type', 'application/json'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    return [ json.dumps(result) ]


def totals_ce_json(environ, start_response):
    objs = get_schedd_objs(environ)
    results = {"Running": 0, "Idle": 0, "Held": 0, "UpdateDate": time.time()}
    for schedd, name in objs:
        for job in schedd.xquery("true", ["JobStatus"]):
            if job.get("JobStatus") == 1:
                results['Idle'] += 1
            elif job.get("JobStatus") == 2:
                results['Running'] += 1
            elif job.get("JobStatus") == 5:
                results['Held'] += 1

    status = '200 OK'
    headers = [('Content-type', 'application/json'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    return [ json.dumps(results) ]


def totals(environ, start_response):
    fname = htcondor_ce.rrd.get_rrd_name(environ, "totals")
    results = json.load(open(fname))

    status = '200 OK'
    headers = [('Content-type', 'application/json'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    return [ json.dumps(results) ]


def pilots_ce_json(environ, start_response):
    objs = get_schedd_objs(environ)
    job_count = {}
    for schedd, name in objs:
        for job in schedd.xquery('true', ['x509UserProxyVOName', 'x509UserProxyFirstFQAN', 'JobStatus', 'x509userproxysubject']):
            DN = job.get("x509userproxysubject", 'Unknown')
            VO = job.get('x509UserProxyVOName', 'Unknown')
            VOMS = job.get('x509UserProxyFirstFQAN', '').replace("/Capability=NULL", "").replace("/Role=NULL", "")
            job_key = (DN, VO, VOMS)
            if job_key not in job_count:
                job_count[job_key] = {"Running": 0, "Idle": 0, "Held": 0, "Jobs": 0, "DN": DN, "VO": VO, "VOMS": VOMS}
            results = job_count[job_key];
            results["Jobs"] += 1
            if job.get("JobStatus") == 1:
                results['Idle'] += 1
            elif job.get("JobStatus") == 2:
                results['Running'] += 1
            elif job.get("JobStatus") == 5:
                results['Held'] += 1

    status = '200 OK'
    headers = [('Content-type', 'application/json'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    return [ json.dumps(job_count.values()) ]


def pilots(environ, start_response):
    fname = htcondor_ce.rrd.get_rrd_name(environ, "pilots")
    results = json.load(open(fname))

    status = '200 OK'
    headers = [('Content-type', 'application/json'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    return [ json.dumps(results) ]


def vos_ce_json(environ, start_response):
    objs = get_schedd_objs(environ)
    job_count = {}
    for schedd, name in objs:
        for job in schedd.xquery('true', ['x509UserProxyVOName', 'JobStatus']):
            VO = job.get('x509UserProxyVOName', 'Unknown')
            job_key = VO
            if job_key not in job_count:
                job_count[job_key] = {"Running": 0, "Idle": 0, "Held": 0, "Jobs": 0}
            results = job_count[job_key];
            results["Jobs"] += 1
            if job.get("JobStatus") == 1:
                results['Idle'] += 1
            elif job.get("JobStatus") == 2:
                results['Running'] += 1
            elif job.get("JobStatus") == 5:
                results['Held'] += 1

    status = '200 OK'
    headers = [('Content-type', 'application/json'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    return [ json.dumps(job_count) ]


def vos_json(environ, start_response):
    fname = htcondor_ce.rrd.get_rrd_name(environ, "vos.json")
    results = json.load(open(fname))

    status = '200 OK'
    headers = [('Content-type', 'application/json'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    return [ json.dumps(results) ]


def status_json(environ, start_response):
    response = {"status": get_schedd_status(environ)}

    status = '200 OK'
    headers = [('Content-type', 'application/json'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    return [ json.dumps(response) ]


def statuses_json(environ, start_response):
    result = get_schedd_statuses(environ)
    response = {}
    for name, status in result.items():
        response[name] = {'status': status}

    status = '200 OK'
    headers = [('Content-type', 'application/json'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    return [ json.dumps(response) ]

def jobs_json(environ, start_response):
    response = {}


    parsed_qs = urlparse.parse_qs(environ['QUERY_STRING'])

    if 'projection' in parsed_qs:
        projection = parsed_qs['projection'][0].split(',')
    else:
        projection = []

    if 'constraint' in parsed_qs:
        constraint = parsed_qs['constraint'][0]
    else:
        constraint = True
    
    # Get the Schedd object
    objs = get_schedd_objs(environ)
    schedd, name = objs[0]

    # Query the schedd
    jobs = schedd.query(constraint, projection)

    parsed_jobs = map(ad_to_json, jobs)

    status = '200 OK'
    headers = [('Content-type', 'application/json'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    return [ json.dumps(parsed_jobs) ]


def vos(environ, start_response):
    vos = htcondor_ce.rrd.list_vos(environ)

    status = '200 OK'
    headers = [('Content-type', 'text/html'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    tmpl = _loader.load('vos.html')

    info = {
        'vos': vos,
        'multice': g_is_multice
    }

    return [tmpl.generate(**info).render('html', doctype='html')]


def metrics(environ, start_response):

    metrics = htcondor_ce.rrd.list_metrics(environ)

    status = '200 OK'
    headers = [('Content-type', 'text/html'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    tmpl = _loader.load('metrics.html')

    info = {
        'metrics': metrics,
        'multice': g_is_multice
    }

    return [tmpl.generate(**info).render('html', doctype='html')]


def health(environ, start_response):

    status = '200 OK'
    headers = [('Content-type', 'text/html'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    tmpl = _loader.load('health.html')
    info = {
        'multice': g_is_multice
    }

    return [tmpl.generate(**info).render('html', doctype='html')]


def pilots_page(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    tmpl = _loader.load('pilots.html')

    info = {'multice': g_is_multice}

    return [tmpl.generate(**info).render('html', doctype='html')] 


def index(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    tmpl = _loader.load('index.html')

    info = {'multice': g_is_multice}

    return [tmpl.generate(**info).render('html', doctype='html')]


def robots(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain'),
              ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    return_text = """User-agent: *
Disallow: /
"""

    return return_text


ce_graph_re = re.compile(r'^/+graphs/+ce/?([a-zA-Z]+)?/?$')
def ce_graph(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'image/png'),
               ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    path = environ.get('PATH_INFO', '')
    m = ce_graph_re.match(path)
    interval = "daily"
    if m.groups()[0]:
        interval=m.groups()[0]

    return [ htcondor_ce.rrd.graph(environ, None, "jobs", interval) ]


vo_graph_re = re.compile(r'^/*graphs/+vos/+([a-zA-Z._]+)/?([a-zA-Z]+)?/?$')
def vo_graph(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'image/png'),
               ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    path = environ.get('PATH_INFO', '')
    m = vo_graph_re.match(path)
    interval = "daily"
    environ['vo'] = m.groups()[0]
    if m.groups()[1]:
        interval=m.groups()[1]

    return [ htcondor_ce.rrd.graph(environ, None, "vos", interval) ]


metrics_graph_re = re.compile(r'^/*graphs/+metrics/+([a-zA-Z._]+)/+([a-zA-Z._]+)/?([a-zA-Z]+)?/?$')
def metrics_graph(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'image/png'),
               ('Cache-Control', 'max-age=60, public')]
    start_response(status, headers)

    path = environ.get('PATH_INFO', '')
    m = metrics_graph_re.match(path)
    interval = "daily"
    environ['group'] = m.groups()[0]
    environ['name'] = m.groups()[1]
    if m.groups()[-1]:
        interval=m.groups()[-1]

    return [ htcondor_ce.rrd.graph(environ, None, "metrics", interval) ]


def not_found(environ, start_response):
    status = '404 Not Found'
    headers = [('Content-type', 'text/html'),
              ('Cache-Control', 'max-age=60, public'),
              ('Location', '/')]
    start_response(status, headers)
    path = environ.get('PATH_INFO', '').lstrip('/')
    return ["Resource %s not found" % xml.sax.saxutils.escape(path)]


urls = [
    (re.compile(r'^/*$'), index),
    (re.compile(r'^robots\.txt$'), robots),
    (re.compile(r'^vos/*$'), vos),
    (re.compile(r'^metrics/*$'), metrics),
    (re.compile(r'^health/*$'), health),
    (re.compile(r'^pilots/*$'), pilots_page),
    (re.compile(r'^json/+totals$'), totals),
    (re.compile(r'^json/+pilots$'), pilots),
    (re.compile(r'^json/+schedds$'), schedds),
    (re.compile(r'^json/+schedd$'), schedd),
    (re.compile(r'^json/+vos$'), vos_json),
    (re.compile(r'^json/+statuses$'), statuses_json),
    (re.compile(r'^json/+status$'), status_json),
    (re.compile(r'^json/+jobs*$'), jobs_json),
    (re.compile(r'^json/+agis-compat$'), agis_json),
    (re.compile(r'^graphs/ce/?'), ce_graph),
    (vo_graph_re, vo_graph),
    (metrics_graph_re, metrics_graph),
]


def application(environ, start_response):

    check_initialized(environ)

    path = environ.get('PATH_INFO', '').lstrip('/')
    
    for regex, callback in urls:
        match = regex.match(path)
        if match:
            environ['htcondorce.url_args'] = match.groups()
            return callback(environ, start_response)
    return not_found(environ, start_response)
