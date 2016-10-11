
import pprint

import htcondorce.web_utils


def agis_compat_main(pool=None):
    environ = {}
    if pool:
        environ['htcondorce.pool'] = pool
    pprint.pprint(htcondorce.web_utils.agis_data(environ))

