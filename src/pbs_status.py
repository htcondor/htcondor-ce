#!/usr/bin/python

#  File:     pbs_status.py
#
#  Author:   Brian Bockelman
#  e-mail:   bbockelm@cse.unl.edu
#
#
# Copyright (c) University of Nebraska-Lincoln.  2012
# 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at 
# 
#     http://www.apache.org/licenses/LICENSE-2.0 
# 
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License.
#

import os
import re
import pwd
import sys
import time
import errno
import fcntl
import struct
import tempfile

cache_timeout = 60

launchtime = time.time()

# This function was written by me for an older project, the OSG-GIP
def pbsOutputFilter(fp):
    """
    PBS can be a pain to work with because it automatically cuts 
    lines off at 80 chars and continues the line on the next line.  For
    example::

        Server: red
        server_state = Active
        server_host = red.unl.edu
        scheduling = True
        total_jobs = 2996
        state_count = Transit:0 Queued:2568 Held:0 Waiting:0 Running:428 Exiting 
         :0 Begun:0 
        acl_roots = t3
        managers = mfurukaw@red.unl.edu,root@t3

    This function puts the line ":0 Begun:0" with the above line.  It's meant
    to filter the output, so you should "scrub" PBS output like this::

        fp = runCommand(<pbs command>)
        for line in pbsOutputFilter(fp):
           ... parse line ...

    This function uses iterators
    """
    class PBSIter:
        """
        An iterator for PBS output; this allows us to easily parse over 
        PBS-style line continuations.
        """

        def __init__(self, fp):
            self.fp = fp
            self.fp_iter = fp.__iter__()
            self.prevline = None
            self.done = False

        def next(self):
            """
            Return the next full line of output for the iterator.
            """
            if self.prevline == None:
                line = self.fp_iter.next()
                if line.startswith('\t'):
                    # Bad! The output shouldn't start with a 
                    # partial line
                    raise ValueError("PBS output contained bad data.")
                self.prevline = line
                return self.next()
            if self.done:
                raise StopIteration()
            try:
                line = self.fp_iter.next()
                if line.startswith('\t'):
                    self.prevline = self.prevline[:-1] + line[1:-1]
                    return self.next()
                else:
                    old_line = self.prevline
                    self.prevline = line
                    return old_line
            except StopIteration:
                self.done = True
                return self.prevline

    class PBSFilter:
        """
        An iterable object based upon the PBSIter iterator.
        """
        
        def __init__(self, myiter):
            self.iter = myiter

        def __iter__(self):
            return self.iter

    return PBSFilter(PBSIter(fp))

# Something else from a prior life - see gratia-probe-common's GratiaWrapper.py
def ExclusiveLock(fd, timeout=120):
    """
    Grabs an exclusive lock on fd

    If the lock is owned by another process, and that process is older than the
    timeout, then the other process will be signaled.  If the timeout is
    negative, then the other process is never signaled.

    If we are unable to hold the lock, this call will not block on the lock;
    rather, it will throw an exception.

    By default, the timeout is 120 seconds.
    """

    # POSIX file locking is cruelly crude.  There's nothing to do besides
    # try / sleep to grab the lock, no equivalent of polling.
    # Why hello, thundering herd.

    # An alternate would be to block on the lock, and use signals to interupt.
    # This would mess up Gratia's flawed use of signals already, and not be
    # able to report on who has the lock.  I don't like indefinite waits!
    max_tries = 5
    for tries in range(1, max_tries+1):
        try:
            fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return
        except IOError, ie:
            if not ((ie.errno == errno.EACCES) or (ie.errno == errno.EAGAIN)):
                raise
            if check_lock(fd, timeout):
                time.sleep(.2) # Fast case; however, we have *no clue* how
                               # long it takes to clean/release the old lock.
                               # Nor do we know if we'd get it if we did
                               # fcntl.lockf w/ blocking immediately.  Blech.
                # Check again immediately, especially if this was the last
                # iteration in the for loop.
                try:
                    fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    return
                except IOError, ie:
                    if not ((ie.errno == errno.EACCES) or (ie.errno == errno.EAGAIN)):
                        raise
        print >> sys.stderr, "Unable to acquire lock, try %i; will sleep for %i " \
            "seconds and try %i more times." % (tries, tries, max_tries-tries)
        time.sleep(tries)

    raise Exception("Unable to acquire lock")

def check_lock(fd, timeout):
    """
    For internal use only.

    Given a fd that is locked, determine which process has the lock.
    Kill said process if it is older than "timeout" seconds.
    This will log the PID of the "other process".
    """

    pid = get_lock_pid(fd)
    if pid == os.getpid():
        return True

    if timeout < 0:
        print >> sys.stderr, "Another process, %d, holds the cache lock." % pid
        return False

    try:
        age = get_pid_age(pid)
    except:
        print >> sys.stderr, "Another process, %d, holds the cache lock." % pid
        print >> sys.stderr, "Unable to get the other process's age; will not time " \
            "it out."
        return False

    print >> sys.stderr, "Another process, %d (age %d seconds), holds the cache " \
        "lock." % (pid, age)

    if age > timeout:
        os.kill(pid, signal.SIGKILL)
    else:
        return False

    return True

linux_struct_flock = "hhxxxxqqixxxx"
try:
    os.O_LARGEFILE
except AttributeError:
    start_len = "hhlli"

def get_lock_pid(fd):
    # For reference, here's the definition of struct flock on Linux
    # (/usr/include/bits/fcntl.h).
    #
    # struct flock
    # {
    #   short int l_type;   /* Type of lock: F_RDLCK, F_WRLCK, or F_UNLCK.  */
    #   short int l_whence; /* Where `l_start' is relative to (like `lseek').  */
    #   __off_t l_start;    /* Offset where the lock begins.  */
    #   __off_t l_len;      /* Size of the locked area; zero means until EOF.  */
    #   __pid_t l_pid;      /* Process holding the lock.  */
    # };
    #
    # Note that things are different on Darwin
    # Assuming off_t is unsigned long long, pid_t is int
    try:
        if sys.platform == "darwin":
            arg = struct.pack("QQihh", 0, 0, 0, fcntl.F_WRLCK, 0)
        else:
            arg = struct.pack(linux_struct_flock, fcntl.F_WRLCK, 0, 0, 0, 0)
        result = fcntl.fcntl(fd, fcntl.F_GETLK, arg)
    except IOError, ie:
        if ie.errno != errno.EINVAL:
            raise
        print >> sys.stderr, "Unable to determine which PID has the lock due to a " \
            "python portability failure.  Contact the developers with your" \
            " platform information for support."
        return False
    if sys.platform == "darwin":
        _, _, pid, _, _ = struct.unpack("QQihh", result)
    else:
        _, _, _, _, pid = struct.unpack(linux_struct_flock, result)
    return pid

def get_pid_age(pid):
    now = time.time()
    st = os.stat("/proc/%d" % pid)
    return now - st.st_ctime

def qstat(jobid=""):
    """
    Call qstat directly for a jobid.
    If none is specified, query all jobid's.

    Returns a python dictionary with the job info.
    """
    qstat = get_qstat_location()
    child_stdout = os.popen("%s -f %s" % (qstat, jobid))
    result = parse_qstat_fd(child_stdout)
    exit_status = child_stdout.close()
    if exit_status:
        exit_code = 0
        if os.WIFEXITED(exit_status):
            exit_code = os.WEXITSTATUS(exit_status)
        if exit_code == 153: # Completed
            result = {jobid: {'BatchJobId': '"%s"' % jobid, "JobStatus": "4", "ExitCode": ' 0'}}
        elif exit_code == 271: # Removed
            result = {jobid: {'BatchJobId': '"%s"' % jobid, 'JobStatus': '3', 'ExitCode': ' 0'}}
        else:
            raise Exception("qstat failed with exit code %s" % str(exit_status))
    return result

_qstat_location_cache = None
def get_qstat_location():
    """
    Locate the copy of qstat the blahp configuration wants to use.
    """
    global _qstat_location_cache
    if _qstat_location_cache != None:
        return _qstat_location_cache
    if os.path.exists("blah_load_config.sh") and os.access("blah_load_config.sh", os.R_OK):
        cmd = 'source blah_load_config.sh && echo "$pbs_binpath/qstat"'
    else:
        cmd = 'which qstat'
    child_stdout = os.popen(cmd)
    output = child_stdout.read()
    location = output.split("\n")[0].strip()
    if child_stdout.close():
        raise Exception("Unable to determine qstat location: %s" % output)
    _qstat_location_cache = location
    return location

job_id_re = re.compile("\s*Job Id: ([0-9]+[\.\w\-]+)")
exec_host_re = re.compile("\s*exec_host = ([\w\-\/.]+)")
status_re = re.compile("\s*job_state = ([QRECH])")
exit_status_re = re.compile("\s*exit_status = (-?[0-9]+)")
status_mapping = {"Q": 1, "R": 2, "E": 2, "C": 4, "H": 5}
def parse_qstat_fd(fd):
    """
    Parse the stdout fd of "qstat -f" into a python dictionary containing
    the information we need.
    """
    job_info = {}
    cur_job_id = None
    cur_job_info = {}
    for line in pbsOutputFilter(fd):
        line = line.strip()
        m = job_id_re.match(line)
        if m:
            if cur_job_id:
                job_info[cur_job_id] = cur_job_info
            cur_job_id = m.group(1)
            cur_job_info = {"BatchJobId": '"%s"' % cur_job_id.split(".")[0]}
            continue
        if cur_job_id == None:
            continue
        m = exec_host_re.match(line)
        if m:
            cur_job_info["WorkerNode"] = '"' + m.group(1).split("/")[0] + '"'
            continue
        m = status_re.match(line)
        if m:
            status = status_mapping.get(m.group(1), 0)
            if status != 0:
                cur_job_info["JobStatus"] = str(status)
            continue
        m = exit_status_re.match(line)
        if m:
            cur_job_info["ExitCode"] = ' %s' % m.group(1)
            continue
    if cur_job_id:
        job_info[cur_job_id] = cur_job_info
    return job_info

def job_dict_to_string(info):
    result = ["%s=%s;" % (i[0], i[1]) for i in info.items()]
    return "[" + " ".join(result) + " ]"

def fill_cache(cache_location):
    results = qstat()
    (fd, filename) = tempfile.mkstemp()
    try:
        for key, val in results.items():
            key = key.split(".")[0]
            os.write(fd, "%s: %s\n" % (key, job_dict_to_string(val)))
        os.fsync(fd)
        os.close(fd)
    except:
        os.unlink(filename)
        raise
    os.rename(filename, cache_location)
    global launchtime
    launchtime = time.time()

cache_line_re = re.compile("([0-9]+[\.\w\-]+):\s+(.+)")
def cache_to_status(jobid, fd):
    for line in fd.readlines():
        line = line.strip()
        m = cache_line_re.match(line)
        if m and m.group(1) == jobid:
            return m.group(2)

def check_cache(jobid, recurse=True):
    uid = os.geteuid()
    username = pwd.getpwuid(uid).pw_name
    cache_dir = os.path.join("/tmp", "qstat_cache_%s" % username)
    if recurse:
        try:
            s = os.stat(cache_dir)
        except OSError, oe:
            if oe.errno != 2:
                raise
            os.mkdir(cache_dir)
            s = os.stat(cache_dir)
        if s.st_uid != uid:
            raise Exception("Unable to check cache because it is owned by UID %d" % s.st_uid)
    cache_location = os.path.join(cache_dir, "results_cache")
    try:
        fd = open(cache_location, "a+")
    except IOError, ie:
        if ie.errno != 2:
            raise
        # Create an empty file so we can hold the file lock
        fd = open(cache_location, "w+")
        ExclusiveLock(fd)
        # If someone grabbed the lock between when we opened and tried to
        # acquire, they may have filled the cache
        if os.stat(cache_location).st_size == 0:
            fill_cache(cache_location)
        fd.close()
        if recurse:
            return check_cache(jobid, recurse=False)
        else:
            return None
    ExclusiveLock(fd)
    s = os.fstat(fd.fileno())
    if s.st_uid != uid:
        raise Exception("Unable to check cache file because it is owned by UID %d" % s.st_uid)
    if (s.st_size == 0) or (launchtime - s.st_mtime > cache_timeout):
        # If someone filled the cache between when we opened the file and
        # grabbed the lock, we may not need to fill the cache.
        s2 = os.stat(cache_location)
        if (s2.st_size == 0) or (launchtime - s2.st_mtime > cache_timeout):
            fill_cache(cache_location)
        if recurse:
            return check_cache(jobid, recurse=False)
        else:
            return None
    return cache_to_status(jobid, fd)

def main():
    # To debug, uncommenting these lines is useful.
    fd = open("/dev/null", "w")
    old_stderr = os.dup(2)
    os.dup2(fd.fileno(), 2)
    if len(sys.argv) != 2:
        print "1Usage: pbs_status.sh pbs/<date>/<jobid>"
        return 1
    jobid = sys.argv[1].split("/")[-1].split(".")[0]
    cache_contents = check_cache(jobid)
    if not cache_contents:
        results = qstat(jobid)
        if not results or jobid not in results:
            print "1ERROR: Unable to find job %s" % jobid
        else:
            print "0%s" % job_dict_to_string(results[jobid])
    else:
        print "0%s" % cache_contents
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception, e:
        print "1ERROR: %s" % str(e).replace("\n", "\\n")
        sys.exit(0)

