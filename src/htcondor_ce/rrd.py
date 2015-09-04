
import os
import re
import errno
import tempfile

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

    if plot in "jobs":
        rrdtool.create(path,
            "--step", "180",
            "DS:running:GAUGE:360:U:U",
            "DS:pending:GAUGE:360:U:U",
            "DS:held:GAUGE:360:U:U",
            "RRA:AVERAGE:0.5:1:1000",
            "RRA:AVERAGE:0.5:20:8760",
            )
    elif plot == "vos":
        rrdtool.create(path,
            "--step", "180",
            "DS:running:GAUGE:360:U:U",
            "DS:pending:GAUGE:360:U:U",
            "DS:held:GAUGE:360:U:U",
            "DS:jobs:GAUGE:360:U:U",
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
def list_metrics(environ):
    results = {}
    base_path = get_rrd_name(environ, "metrics")
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
    base_path = get_rrd_name(environ, "vos")
    for fname in os.listdir(base_path):
        if os.path.isfile(os.path.join(base_path, fname)) and _vo_name_re.match(fname):
            results.append(fname)
    return results


def clean_and_return(fd, pngpath):
    try:
        os.unlink(pngpath)
    finally:
        return os.fdopen(fd).read()


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


def graph(environ, plot, interval):

    if plot not in ['jobs', 'vos', 'metrics']:
        raise ValueError("Unknown plot type requested.")

    fd, pngpath = tempfile.mkstemp(".png")
    if plot == "jobs":
        fname = check_rrd(environ, plot)
        rrdtool.graph(pngpath,
            "--imgformat", "PNG",
            "--width", "400",
            "--start", "-1%s" % get_rrd_interval(interval),
            "--vertical-label", "Pilots",
            "--lower-limit", "0",
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
        fname = check_rrd(environ, plot, vo)
        rrdtool.graph(pngpath,
            "--imgformat", "PNG",
            "--width", "400",
            "--start", "-1%s" % get_rrd_interval(interval),
            "--vertical-label", "Pilots",
            "--lower-limit", "0",
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
        fname = check_rrd(environ, plot, group, name)
        rrdtool.graph(pngpath,
            "--imgformat", "PNG",
            "--width", "400",
            "--start", "-1%s" % get_rrd_interval(interval),
            "--lower-limit", "0",
            "--title", "%s %s" % (group, name),
            "DEF:metric=%s:metric:AVERAGE" % fname,
            "LINE2:metric#FF0000:%s" % name,
            "COMMENT:\\n",
            "COMMENT:    max     avg     cur\\n",
            "GPRINT:metric:MAX:%-6.0lf",
            "GPRINT:metric:AVERAGE:%-6.0lf",
            "GPRINT:metric:LAST:%-6.0lf",
            )


    return clean_and_return(fd, pngpath)

