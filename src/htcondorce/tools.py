"""Utility library for HTCondor-CE tools"""

import errno
import os
import tempfile
import textwrap
import time
from subprocess import Popen, PIPE

HELP_EMAIL = 'htcondor-users@cs.wisc.edu'

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
    print("*"*80)
    wrapper = textwrap.TextWrapper(width=80)
    for line in msg.split('\n'):
        print(wrapper.fill(line))
    print("*"*80)

def print_timestamped_msg(msg):
    """Prepend the current date and time to a message"""
    print_formatted_msg("%s %s" % (time.strftime('%F %T'), msg))

def run_command(command):
    """Run a command and return its return code, stdout, and stderr"""
    p = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    return p.returncode, to_str(stdout), to_str(stderr)

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
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise

def to_str(strlike, encoding="latin-1", errors="strict"):
    """Turns a bytes into a str or leaves it alone.
    The default encoding is latin-1 (which will not raise
    a UnicodeDecodeError); best to use when you want to treat the data
    as arbitrary bytes, but some function is expecting a str.
    """
    if isinstance(strlike, bytes):
        return strlike.decode(encoding, errors)
    return strlike

def to_bytes(strlike, encoding="latin-1", errors="backslashreplace"):
    """Turns a str into bytes or leaves it alone.
    The default encoding is latin-1 under the assumption that you have
    obtained the str from to_str, applied some transformation, and want
    to pass it back to the system.
    """
    if isinstance(strlike, str):
        return strlike.encode(encoding, errors)
    return strlike


def x509_user_proxy_path():
    """Return the path to the user's X.509 proxy or raise FileNotFoundError if it doesn't exist on disk
    """
    try:
        path = os.environ['X509_USER_PROXY']
    except KeyError:
        path = f'/tmp/x509up_u{os.geteuid()}'

    if os.path.exists(path):
        return path
    raise FileNotFoundError


def bearer_token_path():
    """Return the path to the user's X.509 proxy or raise FileNotFoundError if it doesn't exist on disk
    """
    def check_token_path(path, suffix=''):
        token_path = f'{path}{suffix}'
        if os.path.exists(token_path):
            return token_path
        raise FileNotFoundError

    # 1. BEARER_TOKEN env var containing the token itself
    #    Punt on this one until we address HTCONDOR-634

    try:
        # 2. BEARER_TOKEN_PATH containing the path to the token
        path = check_token_path(os.environ['BEARER_TOKEN_FILE'])
    except (KeyError, FileNotFoundError):
        try:
            # 3. XDG_RUNTIME_DIR containing the path to the folder containing the token at bt_u$UID
            path = check_token_path(os.environ['XDG_RUNTIME_DIR'], suffix=f'/bt_u{os.geteuid()}')
        except (KeyError, FileNotFoundError):
            # 4. Otherwise, the token is expected at /tmp/bt_u$UID
            #    Raise FileExceptionError if it doesn't exist
            path = check_token_path(f'/tmp/bt_u{os.geteuid()}')

    return path
