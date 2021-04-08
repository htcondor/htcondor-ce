#!/usr/bin/python3

import os
import datetime

os.environ['CONDOR_CONFIG'] = '/etc/condor-ce/condor_config'

import htcondor

GRATIA_DIR = htcondor.param['PER_JOB_HISTORY_DIR']
HISTORY_FILES = [os.path.join(GRATIA_DIR, x) for x in os.listdir(GRATIA_DIR)]
THRESHOLD = datetime.datetime.now() - datetime.timedelta(days=31)

for history_file in HISTORY_FILES:
    file_ctime = datetime.datetime.fromtimestamp(os.path.getctime(history_file))
    if file_ctime < THRESHOLD:
        os.unlink(history_file)
