#!/usr/bin/python3

import json
import os
import xml.etree.ElementTree as ET
import typing.Dict

from http.client import HTTPException
from urllib.request import urlopen
from urllib.error import URLError

from flask import Flask, Config, url_for, make_response, request
import genshi.template
import subprocess
from tools import to_str

_loader = None

TOPOLOGY_RG = "https://topology.opensciencegrid.org/rgsummary/xml"


class CondorToolException(Exception):
    pass


class TopologyError(Exception):
    pass


def osgid_to_ce(osgid):
    """
    Map a given OSG ID to a list of authorized CEs they can
    register
    """
    # URL for all Production CE resources
    topology_url = TOPOLOGY_RG + '?gridtype=on&gridtype_1=on&service_on&service_1=on'
    try:
        response = urlopen(topology_url)
        topology_xml = response.read()
    except (URLError, HTTPException):
        raise TopologyError('Error retrieving OSG Topology registrations')

    try:
        topology_et = ET.fromstring(topology_xml)
    except ET.ParseError:
        if not topology_xml:
            msg = 'OSG Topology query returned empty response'
        else:
            msg = 'OSG Topology query returned malformed XML'
        raise TopologyError(msg)

    ces = []
    resources = topology_et.findall('./ResourceGroup/Resources/Resource')
    if not resources:
        raise TopologyError('Failed to find any OSG Topology resources')

    for resource in resources:
        try:
            fqdn = resource.find('./FQDN').text.strip()
        except AttributeError:
            # skip malformed resource missing an FQDN
            continue

        try:
            admin_contacts = [contact_list.find('./Contacts')
                              for contact_list in resource.findall('./ContactLists/ContactList')
                              if contact_list.findtext('./ContactType', '').strip() == 'Administrative Contact']
        except AttributeError:
            # skip malformed resource missing contacts
            continue

        for contact in admin_contacts:
            if contact.findtext('./Contact/CILogonID', '').strip() == osgid:
                ces.append(fqdn)

    return ces


def validate_code(reqid: str):
    """Ensure that the code we receive from the form submission is a positive integer
    """
    try:
        assert int(reqid) > 0
    except (ValueError, AssertionError):
        raise CondorToolException("Received invalid code: %s" % reqid)


def fetch_tokens(reqid: str, config: Config) -> typing.Dict:
    binary = config.get('CONDOR_TOKEN_REQUEST_LIST', 'condor_token_request_list')
    pool = config.get('CONDORCE_COLLECTOR')

    validate_code(reqid)
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
        raise CondorToolException("Failed to list internal requests: %s" % to_str(stderr))
    try:
        json_obj = json.loads(to_str(stdout))
    except json.JSONDecodeError:
        raise CondorToolException("Internal error: invalid format of request list")

    return json_obj


def approve_token(reqid: str, config: Config):
    binary = config.get('CONDOR_TOKEN_REQUEST_APPROVE', 'condor_token_request_approve')
    pool = config.get('CONDORCE_COLLECTOR')

    validate_code(reqid)
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
        raise CondorToolException("Failed to approve request: %s" % to_str(stderr))


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

        tmpl = _loader.load('code_submit_failure.html')
        try:
            allowed_identity = osgid_to_ce(osgid)
        except TopologyError as exc:
            info = {'info': exc}
            return make_response(tmpl.generate(**info).render('html', doctype='html'), 400)

        if not allowed_identity:
            info = {'info': "OSG registration not associated with any CE"}
            return make_response(tmpl.generate(**info).render('html', doctype='html'), 400)

        if result.get("RequestedIdentity") not in [hostname + "@users.htcondor.org" for hostname in allowed_identity]:
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
