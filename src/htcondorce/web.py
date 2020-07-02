
import os
import re
import imp
import json
import time
import types
import socket
import logging
import xml.sax.saxutils
import urlparse

import genshi.template

import classad
htcondor = None

import htcondorce.rrd
import htcondorce.web_utils

_initialized = None
_loader = None
_view = None
_plugins = []
g_is_multice = False
OK_STATUS = '200 OK'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def validate_plugin(name, plugin):
    try:
        for regex, callback in plugin.urls:
            if not hasattr(regex, "match"):
                log.warn("plugin %s: %r is not a compiled regex (real type: %s)" % (name, regex, type(regex)))
                return False
            if not callable(callback):
                log.warn("plugin %s: regex %r does not have a valid callback (real type: %s)"
                      % (name, regex.pattern, type(callback)))
                return False
    except (ValueError, AttributeError) as err:
        log.warn("plugin %s: %s" % (name, err))
        return False
    return True


def check_initialized(environ):
    global _initialized
    global _loader
    global _cp
    global _plugins
    global htcondor

    if not _initialized:
        if 'htcondorce.templates' in environ:
            _loader = genshi.template.TemplateLoader(environ['htcondorce.templates'], auto_reload=True)
        else:
            _loader = genshi.template.TemplateLoader('/usr/share/condor-ce/templates', auto_reload=True)
        ce_config = environ.get('htcondorce.config', '/etc/condor-ce/condor_config')
        htcondor = htcondorce.web_utils.check_htcondor()

        plugins_dir = htcondor.param.get("HTCONDORCE_VIEW_PLUGINS_DIR", "/usr/share/condor-ce/ceview-plugins")
        if os.path.isdir(plugins_dir):
            for filename in sorted(os.listdir(plugins_dir)):
                if not filename.endswith(".py"):
                    continue
                name = filename[:-3]
                plugin = imp.load_source(name, os.path.join(plugins_dir, filename))
                if validate_plugin(name, plugin):
                    log.debug("plugin %s: loaded ok", name)
                    _plugins.append(plugin)

        _initialized = True


def _headers(content_type):
    return [('Content-type', content_type),
            ('Cache-Control', 'max-age=60, public')]


class ClassadEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, classad.ExprTree):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def ad_to_json(ad):
    result = {}
    for (key, val) in ad.items():
        if isinstance(val, classad.ExprTree):
            val = val.eval()
        if val == classad.Value.Undefined:
            val = None
        result[key] = val
    return result


def schedds(environ, start_response):
    ads = htcondorce.web_utils.get_schedd_ads(environ)
    results = {}
    for ad in ads:
        if 'Name' not in ad:
            continue
        results[ad['Name']] = ad_to_json(ad)

    start_response(OK_STATUS, _headers('application/json'))

    return [ json.dumps(results, cls=ClassadEncoder) ]


def schedd(environ, start_response):
    ads = htcondorce.web_utils.get_schedd_ads(environ)
    results = {}
    for ad in ads:
        if 'Name' not in ad:
            continue
        results[ad['Name']] = ad
    keys = results.keys()
    keys.sort()
    result = ad_to_json(results[keys[0]])

    start_response(OK_STATUS, _headers('application/json'))
    return [ json.dumps(result) ]


def totals_ce_json(environ, start_response):
    objs = htcondorce.web_utils.get_schedd_objs(environ)
    results = {"Running": 0, "Idle": 0, "Held": 0, "UpdateDate": time.time()}
    for schedd, name in objs:
        for job in schedd.xquery("true", ["JobStatus"]):
            if job.get("JobStatus") == 1:
                results['Idle'] += 1
            elif job.get("JobStatus") == 2:
                results['Running'] += 1
            elif job.get("JobStatus") == 5:
                results['Held'] += 1

    start_response(OK_STATUS, _headers('application/json'))
    return [ json.dumps(results) ]


def totals(environ, start_response):
    fname = htcondorce.rrd.path_with_spool(environ, "totals")
    results = json.load(open(fname))
    start_response(OK_STATUS, _headers('application/json'))
    return [ json.dumps(results) ]


def pilots_ce_json(environ, start_response):
    objs = htcondorce.web_utils.get_schedd_objs(environ)
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

    start_response(OK_STATUS, _headers('application/json'))
    return [ json.dumps(job_count.values()) ]


def pilots(environ, start_response):
    fname = htcondorce.rrd.path_with_spool(environ, "pilots")
    results = json.load(open(fname))
    start_response(OK_STATUS, _headers('application/json'))
    return [ json.dumps(results) ]


def vos_ce_json(environ, start_response):
    objs = htcondorce.web_utils.get_schedd_objs(environ)
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
    start_response(OK_STATUS, _headers('application/json'))
    return [ json.dumps(job_count) ]


def vos_json(environ, start_response):
    fname = htcondorce.rrd.path_with_spool(environ, "vos.json")
    results = json.load(open(fname))
    start_response(OK_STATUS, _headers('application/json'))
    return [ json.dumps(results) ]


def status_json(environ, start_response):
    response = {"status": htcondorce.web_utils.get_schedd_status(environ)}
    start_response(OK_STATUS, _headers('application/json'))
    return [ json.dumps(response) ]


def statuses_json(environ, start_response):
    result = htcondorce.web_utils.get_schedd_statuses(environ)
    response = {}
    for name, status in result.items():
        response[name] = {'status': status}
    start_response(OK_STATUS, _headers('application/json'))
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
    objs = htcondorce.web_utils.get_schedd_objs(environ)
    schedd, name = objs[0]

    # Query the schedd
    jobs = schedd.query(constraint, projection)

    parsed_jobs = map(ad_to_json, jobs)

    start_response(OK_STATUS, _headers('application/json'))
    return [ json.dumps(parsed_jobs) ]


def vos(environ, start_response):
    vos = htcondorce.rrd.list_vos(environ)
    start_response(OK_STATUS, _headers('text/html'))
    tmpl = _loader.load('vos.html')

    info = {
        'vos': vos,
        'multice': g_is_multice
    }

    return [tmpl.generate(**info).render('html', doctype='html')]


def metrics(environ, start_response):
    metrics = htcondorce.rrd.list_metrics(environ)
    start_response(OK_STATUS, _headers('text/html'))
    tmpl = _loader.load('metrics.html')

    info = {
        'metrics': metrics,
        'multice': g_is_multice
    }

    return [tmpl.generate(**info).render('html', doctype='html')]


def health(environ, start_response):
    start_response(OK_STATUS, _headers('text/html'))
    tmpl = _loader.load('health.html')
    info = {
        'multice': g_is_multice
    }

    return [tmpl.generate(**info).render('html', doctype='html')]


def pilots_page(environ, start_response):
    start_response(OK_STATUS, _headers('text/html'))
    tmpl = _loader.load('pilots.html')
    info = {'multice': g_is_multice}
    return [tmpl.generate(**info).render('html', doctype='html')] 


def index(environ, start_response):
    start_response(OK_STATUS, _headers('text/html'))
    tmpl = _loader.load('index.html')
    info = {'multice': g_is_multice}
    return [tmpl.generate(**info).render('html', doctype='html')]


def robots(environ, start_response):
    start_response(OK_STATUS, _headers('text/plain'))
    return_text = """User-agent: *
Disallow: /
"""
    return return_text


ce_graph_re = re.compile(r'^/+graphs/+ce/?([a-zA-Z]+)?/?$')
def ce_graph(environ, start_response):
    start_response(OK_STATUS, _headers('image/png'))
    path = environ.get('PATH_INFO', '')
    m = ce_graph_re.match(path)
    interval = "daily"
    if m.group(1):
        interval=m.groups()[0]

    return [ htcondorce.rrd.graph(environ, None, "jobs", interval) ]


vo_graph_re = re.compile(r'^/*graphs/+vos/+([a-zA-Z._]+)/?([a-zA-Z]+)?/?$')
def vo_graph(environ, start_response):
    start_response(OK_STATUS, _headers('image/png'))
    path = environ.get('PATH_INFO', '')
    m = vo_graph_re.match(path)
    interval = "daily"
    environ['vo'] = m.group(1)
    if m.group(2):
        interval=m.group(2)

    return [ htcondorce.rrd.graph(environ, None, "vos", interval) ]


metrics_graph_re = re.compile(r'^/*graphs/+metrics/+([a-zA-Z._]+)/+([a-zA-Z._]+)/?([a-zA-Z]+)?/?$')
def metrics_graph(environ, start_response):
    start_response(OK_STATUS, _headers('image/png'))
    path = environ.get('PATH_INFO', '')
    m = metrics_graph_re.match(path)
    interval = "daily"
    environ['group'] = m.group(1)
    environ['name'] = m.group(2)
    if m.groups()[-1]:
        interval=m.groups()[-1]

    return [ htcondorce.rrd.graph(environ, None, "metrics", interval) ]


def get_tableattribs(environ):
    attribs = []
    label_params = sorted(it for it in htcondor.param.keys() if it.upper().startswith("HTCONDORCE_VIEW_INFO_TABLE_LABEL_"))
    for label_param in label_params:
        attrib_param = label_param.upper().replace("LABEL", "ATTRIB", 1)
        try:
            if htcondor.param[label_param] and htcondor.param[attrib_param]:
                attribs.append(
                    dict(label=htcondor.param[label_param],
                         attrib=htcondor.param[attrib_param])
                )
        except KeyError:
            log.warn("%s has no corresponding %s", label_param, attrib_param)
            continue
    return attribs


def tableattribs_json(environ, start_response):
    start_response(OK_STATUS, _headers('application/json'))
    return [ json.dumps(get_tableattribs(environ)) ]


def not_found(environ, start_response):
    status = '404 Not Found'
    headers = _headers('text/html') + [('Location', '/')]
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
    (re.compile(r'^json/+tableattribs*$'), tableattribs_json),
    (re.compile(r'^graphs/ce/?'), ce_graph),
    (vo_graph_re, vo_graph),
    (metrics_graph_re, metrics_graph),
]


def application(environ, start_response):

    check_initialized(environ)

    path = environ.get('PATH_INFO', '').lstrip('/')

    for plugin in _plugins:
        for regex, callback in plugin.urls:
            match = regex.match(path)
            if match:
                environ['htcondorce.url_args'] = match.groups()
                return callback(environ, start_response)

    for regex, callback in urls:
        match = regex.match(path)
        if match:
            environ['htcondorce.url_args'] = match.groups()
            return callback(environ, start_response)

    return not_found(environ, start_response)
