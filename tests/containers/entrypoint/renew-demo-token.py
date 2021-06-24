#!/usr/bin/python3

import os
import json
import time

from urllib import request

# Create the requested json
demo_json = {
    "payload": {
        "aud": "ANY",
        "ver": "scitokens:2.0",
        "scope": "condor:/READ condor:/WRITE",
        "exp": int(time.time() + 3600*8),
        "sub": "abh3"
    }
}

# Convert the format from dictionary to json string
data = json.dumps({
            'payload': json.dumps(demo_json['payload']),
            "algorithm": "ES256"
            }).encode()

# Headers so that heroku doesn't block us
headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3)' +
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
        'Content-Type': 'application/json'
    }

# The actual request
req = request.Request("https://demo.scitokens.org/issue",
                      data=data,
                      headers=headers)  # this will make the method "POST"
resp = request.urlopen(req).read()

# Convert the "bytes" response to text
token_path = os.environ.get('BEARER_TOKEN', '') or \
    f"/tmp/bt_u{os.geteuid()}"

with open(token_path, 'w') as f:
    f.write(resp.decode('utf-8'))
