#!/usr/bin/python

import os
import subprocess

try:
    import classad
    import htcondor
except ImportError:
    sys.exit("ERROR: Could not load HTCondor Python bindings. "
             "Ensure the 'htcondor' and 'classad' are in PYTHONPATH")

jre    = classad.parseAds('JOB_ROUTER_ENTRIES')
grs    = ( x["GridResource"] for x in jre )
rhosts = ( x.split()[1:3]    for x in grs )

for batchtype, rhost in rhosts:
    subprocess.call(['bosco_cluster', '-o', os.getenv("OVERRIDE_DIR"),
                     rhost, batchtype])

