
import os
import re
import errno

import rrdtool


def path_with_base(base, *paths):
    full_base = os.path.abspath(base)
    filtered_paths = []
    for path in paths:
        if path:
            filtered_paths.append(path)
    joined_path = os.path.abspath(os.path.join(full_base, *filtered_paths))
    if not joined_path.startswith(full_base):
        raise Exception("Unable to construct full path name.")
    return joined_path


def get_rrd_name(environ, plot, *other):
    return path_with_base(environ['htcondorce.spool'], plot, *other)


def check_rrd(environ, plot, group=None, name=None):
    path = get_rrd_name(environ, plot, group, name)
    dir, fname = os.path.split(path)
    try:
        os.makedirs(dir)
    except OSError, oe:
        if oe.errno != errno.EEXIST:
            raise
    if os.path.exists(path):
        return path

    if plot == "jobs":
        rrdtool.create(path,
            "--step", "180",
            "DS:running:GAUGE:360:U:U",
            "DS:pending:GAUGE:360:U:U",
            "DS:held:GAUGE:360:U:U",
            "RRA:AVERAGE:0.5:1:1000",
            "RRA:AVERAGE:0.5:20:8760",
            )
    elif plot == "metrics":
        rrdtool.create(path,
            "--step", "180",
            "DS:metric:GAUGE:360:U:U",
            "RRA:AVERAGE:0.5:1:1000",
            "RRA:AVERAGE:0.5:20:8760",
            )

    return path


_metric_name_re = re.compile(r'^[-A-za-z0-9_]+[-A-za-z0-9_.]*')
def list_metrics(environ, group_name):
    results = []
    for fname in os.listdir(get_rrd_name(environ, "metrics", group_name)):
        if os.path.isfile(fname) and _metric_name_re.matches(fname):
            results.append(fname)
    return results
            

