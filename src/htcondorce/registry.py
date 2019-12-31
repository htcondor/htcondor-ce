#!/usr/bin/python2

import json
import os

from flask import Flask, url_for, make_response, request
import genshi.template
import subprocess

_loader = None

class CondorToolException(Exception):
    pass

def osgid_to_ce(osgid):
    """
    Map a given OSG ID to a list of authorized CEs they can
    register
    """
    # TODO: Here, we need to create a mapping from CILogon IDs to authorized CEs.
    if osgid == 'OSG1000001':
        return ['hcc-briantest7.unl.edu']

def fetch_tokens(reqid, config):
    binary = config.get('CONDOR_TOKEN_REQUEST_LIST', 'condor_token_request_list')
    pool = config.get('CONDORCE_COLLECTOR')
    args = [binary, '-reqid', str(reqid), '-json']
    if pool:
        args.append('-pool', pool)
    req_environ = dict(os.environ)
    req_environ.setdefault('CONDOR_CONFIG', '/etc/condor-ce/condor_config')
    req_environ['_condor_SEC_CLIENT_AUTHENTICATION_METHODS'] = "TOKEN"
    req_environ['_condor_SEC_TOKEN_DIRECTORY'] = '/etc/condor-ce/webapp.tokens.d'
    process = subprocess.Popen(args, stderr=subprocess.PIPE,
        stdout=subprocess.PIPE, env=req_environ)
    stdout, stderr = process.communicate()
    if process.returncode:
        raise CondorToolException("Failed to list internal requests: %s" % stderr)
    try:
        json_obj = json.loads(stdout)
    except json.JSONDecodeError:
        raise CondorToolException("Internal error: invalid format of request list")

    return json_obj


def approve_token(reqid, config):
    binary = config.get('CONDOR_TOKEN_REQUEST_APPROVE', 'condor_token_request_approve')
    pool = config.get('CONDORCE_COLLECTOR')
    args = [binary, '-reqid', str(reqid)]
    if pool:
        args.append('-pool', pool)
    req_environ = dict(os.environ)
    req_environ.setdefault('CONDOR_CONFIG', '/etc/condor-ce/condor_config')
    req_environ['_condor_SEC_CLIENT_AUTHENTICATION_METHODS'] = "TOKEN"
    req_environ['_condor_SEC_TOKEN_DIRECTORY'] = '/etc/condor-ce/webapp.tokens.d'
    process = subprocess.Popen(args, stderr=subprocess.PIPE,
        stdout=subprocess.PIPE, stdin=subprocess.PIPE, env=req_environ)
    stdout, stderr = process.communicate(input="yes\n")
    if process.returncode:
        raise CondorToolException("Failed to approve request: %s" % stderr)


def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.update(test_config)

    global _loader
    template_location = app.config.get('HTCONDORCE_TEMPLATES', '/usr/share/condor-ce/templates')
    _loader = genshi.template.TemplateLoader(template_location, auto_reload=True)

    @app.route("/code", methods=['GET', 'POST'])
    def code():

        if request.method == 'POST':
            return code_submit()

        tmpl = _loader.load('code.html')
        info = {
            'pin_js': url_for('static', filename='bootstrap-pincode-input.js'),
            'pin_css': url_for('static', filename='bootstrap-pincode-input.css'),
            'code_submit': url_for('code')
        }
        response = make_response(tmpl.generate(**info).render('html', doctype='html'))
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'none';"
        return response

    def code_submit():
        if 'code' not in request.form:
            tmpl = _loader.load('code_submit_failure.html')
            info = {'info': "The code parameter is missing"}
            return make_response(tmpl.generate(**info).render('html', doctype='html'), 400)
        osgid = request.environ.get('OIDC_CLAIM_osgid')
        if not osgid:
            tmpl = _loader.load('code_submit_failure.html')
            info = {'info': "User is not registered with the OSG"}
            return make_response(tmpl.generate(**info).render('html', doctype='html'), 401)
        try:
            result = fetch_tokens(request.form.get('code'), app.config)
        except CondorToolException as cte:
            tmpl = _loader.load('code_submit_failure.html')
            return make_response(tmpl.generate(info=str(cte)).render('html', doctype='html'), 400)

        if not result:
            tmpl = _loader.load('code_submit_failure.html')
            info = {'info': "Request %s is unknown" % request.form.get('code')}
            return make_response(tmpl.generate(**info).render('html', doctype='html'), 400)
        result = result[0]

        authz = result.get('LimitAuthorization')
        if authz != 'ADVERTISE_SCHEDD':
            tmpl = _loader.load('code_submit_failure.html')
            info = {'info': "Token must be limited to the ADVERTISE_SCHEDD authorization"}
            return make_response(tmpl.generate(**info).render('html', doctype='html'), 400)

        allowed_identity = osgid_to_ce(osgid)
        if not allowed_identity:
            tmpl = _loader.load('code_submit_failure.html')
            info = {'info': "OSG registration not associated with any CE"}
            return make_response(tmpl.generate(**info).render('html', doctype='html'), 400)

        found_requested_identity = False
        for hostname in allowed_identity:
            identity = hostname + "@users.htcondor.org"
            if identity == result.get("RequestedIdentity"):
                found_requested_identity = True
                break
        if not found_requested_identity:
            tmpl = _loader.load('code_submit_failure.html')
            info = {'info': "Requested identity (%s) not in the list of allowed CEs (%s)" % \
                (result.get("RequestedIdentity"), ", ".join(allowed_identity))}
            return make_response(tmpl.generate(**info).render('html', doctype='html'), 400)

        try:
            approve_token(request.form.get('code'), app.config)
        except CondorToolException as cte:
            tmpl = _loader.load('code_submit_failure.html')
            return make_response(tmpl.generate(info=str(cte)).render('html', doctype='html'), 400)

        tmpl = _loader.load('code_submit.html')
        info = {
            'info': "Request approved."
        }
        response = make_response(tmpl.generate(**info).render('html', doctype='html'))
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
