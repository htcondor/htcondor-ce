"""Utility library for HTCondor-CE tools"""

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
    """Exception for handling errors from HTCondor"""
    pass

class CondorUserException(Exception):
    """Exception for handling user errors"""
    pass

def print_formatted_msg(msg):
    """Limit output messages to 80 characters in width"""
    print "*"*80
    wrapper = textwrap.TextWrapper(width=80)
    for line in msg.split('\n'):
        print wrapper.fill(line)
    print "*"*80

def print_timestamped_msg(msg):
    """Prepend the current date and time to a message"""
    print_formatted_msg("%s %s" % (time.strftime('%F %T'), msg))

def run_command(command):
    """Run a command and return its return code, stdout, and stderr"""
    p = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    return p.returncode, stdout, stderr

def generate_job_files():
    """Create temporary job log, stdout, and stderr files"""
    pid = os.getpid()
    job_info = {}
    for filetype in JOB_FILES:
        try:
            fd, job_info[filetype + '_file'] = tempfile.mkstemp(dir=".", prefix=".%s_%d_" % (filetype, pid))
            os.close(fd)
        except OSError:
            raise RuntimeError('Unable to create temporary files in the current working directory: %s' % os.getcwd())

    return job_info

def cleanup_job_files(job_info):
    """Remove temporary job log, stdout, and stderr files  """
    for filetype in JOB_FILES + ['submit']:
        try:
            os.unlink(job_info[filetype + '_file'])
        except KeyError:
            pass
        except OSError, e:
            if e.errno != errno.ENOENT:
                raise
