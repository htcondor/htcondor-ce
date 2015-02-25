#!/usr/bin/python

import errno
import os
import tempfile
import textwrap
import time
from subprocess import Popen, PIPE

# Excluding submit file so the respective scripts
# can generate it as they see fit
JOB_FILES = ['stdout', 'stderr', 'log']

class CondorRunException(Exception):
    pass

class CondorUserException(Exception):
    pass

def print_formatted_msg(msg):
    print "*"*80
    for line in textwrap.wrap(msg, 80):
        print line
    print "*"*80

def print_timestamped_msg(msg):
    print_formatted_msg("%s %s" % (time.strftime('%F %T'), msg))

def run_command(command):
    p = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    return p.returncode, stdout, stderr

def generate_job_files(job_info):
    pid = os.getpid()
    for filetype in JOB_FILES:
        fd, job_info[filetype + '_file'] = tempfile.mkstemp(dir=".", prefix=".%s_%d_" % (filetype, pid))
        os.close(fd)
    return job_info

def cleanup_job_files(job_info):
    for filetype in JOB_FILES + ['submit']:
        try:
            os.unlink(job_info[filetype + '_file'])
        except KeyError:
            pass
        except OSError, e:
            if e.errno != errno.ENOENT:
                raise
