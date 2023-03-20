# TODO: catch rrdtool method exceptions and non-zero return codes from the rrdtool cli with `check_call()`

import os
import re
import errno

# Try using rrdtool Python bindings
try:
    import rrdtool
except ModuleNotFoundError:
    # If not available, fallback to shelling out to the CLI
    import subprocess


def path_with_spool(environ, *paths):
    spool = environ['htcondorce.spool']
    full_spool = os.path.abspath(spool)
    filtered_paths = []
    for path in paths:
        if path:
            filtered_paths.append(path)
    joined_path = os.path.abspath(os.path.join(full_spool, *filtered_paths))
    if not joined_path.startswith(full_spool):
        raise Exception("Unable to construct full path name.")
    return joined_path


def create(path, *args):
    try:
        rrdtool.create(path, *args)
    except NameError:
        cmd = ['/usr/bin/rrdtool', 'create', path] + list(args)
        proc = subprocess.Popen(cmd)  # pylint: disable=used-before-assignment
        proc.communicate()  # wait until 'rrdtool create' completes


def check_rrd(environ, host, plot, group=None, name=None):
    path = path_with_spool(environ, host, plot, group, name)
    dirname, _ = os.path.split(path)
    try:
        os.makedirs(dirname)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
    if os.path.exists(path):
        return path

    if plot in "jobs":
        create(path,
            "--step", "180",
            "DS:running:GAUGE:360:U:U",
            "DS:pending:GAUGE:360:U:U",
            "DS:held:GAUGE:360:U:U",
            "RRA:AVERAGE:0.5:1:1000",
            "RRA:AVERAGE:0.5:20:8760",
            )
    elif plot == "vos":
        create(path,
            "--step", "180",
            "DS:running:GAUGE:360:U:U",
            "DS:pending:GAUGE:360:U:U",
            "DS:held:GAUGE:360:U:U",
            "DS:jobs:GAUGE:360:U:U",
            "RRA:AVERAGE:0.5:1:1000",
            "RRA:AVERAGE:0.5:20:8760",
            )
    elif plot == "metrics":
        create(path,
            "--step", "180",
            "DS:metric:GAUGE:360:U:U",
            "RRA:AVERAGE:0.5:1:1000",
            "RRA:AVERAGE:0.5:20:8760",
            )

    return path


_metric_name_re = re.compile(r'^[-A-za-z0-9_]+[-A-za-z0-9_.]*')
def list_metrics(environ):
    results = {}
    base_path = path_with_spool(environ, "metrics")
    for fname in os.listdir(base_path):
        group_path = os.path.join(base_path, fname)
        if os.path.isdir(group_path) and _metric_name_re.match(fname):
            group_metrics = results.setdefault(fname, [])
            for fname in os.listdir(group_path):
                if os.path.isfile(os.path.join(group_path, fname)) and _metric_name_re.match(fname):
                    group_metrics.append(fname)
    return results


_vo_name_re = re.compile(r'^[-A-za-z0-9_]+[-A-za-z0-9_.]*')
def list_vos(environ):
    results = []
    base_path = path_with_spool(environ, "vos")
    for fname in os.listdir(base_path):
        if os.path.isfile(os.path.join(base_path, fname)) and _vo_name_re.match(fname):
            results.append(fname)
    return results


def get_rrd_interval(interval):
    if interval == "hourly":
        rrd_interval = "h"
    elif interval == "daily":
        rrd_interval = "d"
    elif interval == "weekly":
        rrd_interval = "w"
    elif interval == "monthly":
        rrd_interval = "m"
    elif interval == "yearly":
        rrd_interval = "y"
    else:
        raise ValueError("Unknown interval requested.")
    return rrd_interval


def generate_graph(interval, *args):
    args = ["-",
            "--imgformat", "PNG",
            "--width", "400",
            "--start", "-1%s" % get_rrd_interval(interval),
            "--lower-limit", "0"] + list(args)

    try:
        out = rrdtool.graphv(*args)
        return out['image']
    except NameError:
        # use graph instead of graphv since we don't need the metadata
        cmd = ['/usr/bin/rrdtool', 'graph'] + list(args)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        stdout, _ = proc.communicate()
        return stdout


def graph(environ, host, plot, interval):

    if plot not in ['jobs', 'vos', 'metrics']:
        raise ValueError("Unknown plot type requested.")

    if plot == "jobs":
        fname = check_rrd(environ, host, plot)
        graph = generate_graph(interval,
            "--vertical-label", "Pilots",
            "--title", "CE Pilot Counts",
            "DEF:Running=%s:running:AVERAGE" % fname,
            "DEF:Idle=%s:pending:AVERAGE" % fname,
            "DEF:Held=%s:held:AVERAGE" % fname,
            "LINE1:Running#00FF00:Running",
            "LINE2:Idle#FF0000:Idle",
            "LINE3:Held#0000FF:Held",
            "COMMENT:\\n",
            "COMMENT:            max     avg     cur\\n",
            "COMMENT:Running ",
            "GPRINT:Running:MAX:%-6.0lf",
            "GPRINT:Running:AVERAGE:%-6.0lf",
            "GPRINT:Running:LAST:%-6.0lf",
            "COMMENT:\\n",
            "COMMENT:Idle    ",
            "GPRINT:Idle:MAX:%-6.0lf",
            "GPRINT:Idle:AVERAGE:%-6.0lf",
            "GPRINT:Idle:LAST:%-6.0lf\\n",
            "COMMENT:\\n",
            "COMMENT:Held    ",
            "GPRINT:Held:MAX:%-6.0lf",
            "GPRINT:Held:AVERAGE:%-6.0lf",
            "GPRINT:Held:LAST:%-6.0lf\\n",
            )
    elif plot == 'vos':
        vo = environ.get('vo', 'Unknown')
        fname = check_rrd(environ, host, plot, vo)
        graph = generate_graph(interval,
            "--vertical-label", "Pilots",
            "--title", "%s Pilot Counts" % vo,
            "DEF:Running=%s:running:AVERAGE" % fname,
            "DEF:Idle=%s:pending:AVERAGE" % fname,
            "DEF:Held=%s:held:AVERAGE" % fname,
            "LINE1:Running#00FF00:Running",
            "LINE2:Idle#FF0000:Idle",
            "LINE3:Held#0000FF:Held",
            "COMMENT:\\n",
            "COMMENT:            max     avg     cur\\n",
            "COMMENT:Running ",
            "GPRINT:Running:MAX:%-6.0lf",
            "GPRINT:Running:AVERAGE:%-6.0lf",
            "GPRINT:Running:LAST:%-6.0lf",
            "COMMENT:\\n",
            "COMMENT:Idle    ",
            "GPRINT:Idle:MAX:%-6.0lf",
            "GPRINT:Idle:AVERAGE:%-6.0lf",
            "GPRINT:Idle:LAST:%-6.0lf\\n",
            "COMMENT:\\n",
            "COMMENT:Held    ",
            "GPRINT:Held:MAX:%-6.0lf",
            "GPRINT:Held:AVERAGE:%-6.0lf",
            "GPRINT:Held:LAST:%-6.0lf\\n",
            )
    elif plot == 'metrics':
        group = environ.get('group', 'Unknown')
        name = environ.get('name', 'Unknown')
        fname = check_rrd(environ, host, plot, group, name)
        graph = generate_graph(interval,
            "--title", "%s %s" % (group, name),
            "DEF:metric=%s:metric:AVERAGE" % fname,
            "LINE2:metric#FF0000:%s" % name,
            "COMMENT:\\n",
            "COMMENT:    max     avg     cur\\n",
            "GPRINT:metric:MAX:%-6.0lf",
            "GPRINT:metric:AVERAGE:%-6.0lf",
            "GPRINT:metric:LAST:%-6.0lf",
            "COMMENT:\\n",
            )


    return graph


def update(fname, value):
    try:
        rrdtool.update(fname, value)
    except NameError:
        cmd = ['/usr/bin/rrdtool', 'update', fname, value]
        proc = subprocess.Popen(cmd)
        proc.communicate()  # wait until 'rrdtool update' completes
