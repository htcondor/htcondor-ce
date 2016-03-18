import itertools

import classad
import htcondor

import logging
_logger = logging.getLogger(__name__)



class ResourceAd(classad.ClassAd):
    """Contains information about a resource in a ResourceCatalog
    Members:
        ce_ad:         The classad the ResourceCatalog was found in.
        catalog_entry: The classad in OSG_ResourceCatalog that corresponds
                       to this resource.

    """

    def __init__(self, ce_ad, catalog_entry):
        classad.ClassAd.__init__(self, '[]')

        self.ce_ad         = ce_ad
        self.catalog_entry = catalog_entry

        for cekey in ['OSG_Resource', 'OSG_ResourceGroup', 'OSG_BatchSystems']:
            self[cekey] = ce_ad[cekey]
        self['grid_resource'] = ce_ad['grid_resource'].eval()

        for catkey, catval in catalog_entry.items():
            if isinstance(catval, classad.ClassAd):
                # dict needed to work around a bug where subclassads are added as lists
                self[catkey] = dict(catval)
            else:
                self[catkey] = catval


def getSubmitFileAdditions(resource_ad):
    """Returns additions to a submit file (as list of strings) to make the
    submitted job match the given resource

    """
    global _logger

    lines = []
    if 'grid_resource' in resource_ad:
        lines.append('+GridResource = %s' % classad.quote(resource_ad['grid_resource']))
    if 'Transform' in resource_ad:
        transform_ad = resource_ad['Transform']
        set_lines = []
        copy_lines = []
        eval_set_lines = []
        for key, value in transform_ad.iteritems():
            if key.startswith('set_'):
                set_lines.append('+%s = %s' % (key.replace('set_', '', 1), value))
            elif key.startswith('copy_'):
                if value in resource_ad:
                    copy_lines.append('+%s = %s' % (key.replace('copy_', '', 1), resource_ad[value]))
                else:
                    _logger.warning("Ignoring '%s': '%s' missing from Resource Ad" % (key, value))
            elif key.startswith('eval_set_'):
                eval_set_lines.append('+%s = %s' % (key.replace('eval_set_', '', 1), resource_ad.eval(value)))
            elif key.startswith('delete_'):
                _logger.warning("Ignoring '%s': 'delete' transforms not supported", key)
            else:
                _logger.warning("Ignoring '%s': unknown transform type", key)
        lines += copy_lines + set_lines + eval_set_lines
    return lines


def fetchCEAds(collector_addr):
    """Query a condor collector for ads containing the CE info
    attributes we want to examine

    """
    required_attrs = ['OSG_Resource', 'OSG_ResourceGroup', 'OSG_ResourceCatalog', 'OSG_BatchSystems', 'grid_resource']
    constraint     = '! (%s)' % ' || '.join(["isUndefined("+x+")" for x in required_attrs])
    collector      = htcondor.Collector(collector_addr)
    ads            = collector.query(htcondor.AdTypes.Any, constraint)
    return ads


def getResourceAdsIter(ce_ads):
    """Get an iterator over all ResourceAd objects that can be created
    from an iterable of CE ads

    """
    for ce_ad in ce_ads:
        for catalog_entry in ce_ad['OSG_ResourceCatalog']:
            yield ResourceAd(ce_ad, catalog_entry)


def matchWallTime(walltime, resource_ad):
    """True if `walltime` <= MaxWallTime in `resource_ad`, or if
    MaxWallTime is undefined or 0

    """
    max_wall_time = resource_ad.get('MaxWallTime', 0)
    if not max_wall_time:
        return True
    else:
        return (int(max_wall_time) >= walltime)


def matchAllowedVOs(vo, resource_ad):
    """True if `vo` is in the AllowedVOs list in `resource_ad`, or
    if AllowedVOs is undefined or empty

    """
    allowed_vos = resource_ad.get('AllowedVOs', None)
    if not allowed_vos:
        return True
    else:
        return vo in list(allowed_vos)


def evalExpressionStr(expression_str, context):
    """Evaluate a classad expression (in a string) in the given context (a
    ClassAd).

    Can raise:
    - SyntaxError (if expression_str is unparseable)

    """
    return context.flatten(classad.ExprTree(expression_str))


def filterResourceAds(constraints, resources):
    """Filter a list of ResourceAds in `resources` based on a set of
    constraints on attributes given in the dict `constraints`.

    The recognized keys in `constraints` are:
        'constrain' : arbitrary ClassAd expression
        'cpus'     : minimum CPUs of resource
        'memory'   : minimum Memory of resource
        'name'     : Name of resource
        'vo'       : VO which must be in AllowedVOs of resource (if
                     AllowedVOs is present)
        'walltime' : minimum MaxWallTime of resource (if MaxWallTime
                     is present)

    """
    predicates = []
    for attr, value in constraints.iteritems():
        if value is None:
            continue
        # NB: Do not use 'attr' or 'value' inside the lambdas because that
        # would be 'closing over the loop variable'
        if attr == 'cpus':
            predicates.append(
                lambda res: constraints['cpus'] <= res.get('CPUs', res.get('Cpus')))
        elif attr == 'constrain':
            predicates.append(
                lambda res: bool(evalExpressionStr(constraints['constrain'], res)))
        elif attr == 'memory':
            predicates.append(
                lambda res: constraints['memory'] <= res['Memory'])
        elif attr == 'name':
            predicates.append(
                lambda res: constraints['name'] == res['Name'])
        elif attr == 'vo':
            predicates.append(
                lambda res: matchAllowedVOs(constraints['vo'], res))
        elif attr == 'walltime':
            predicates.append(
                lambda res: matchWallTime(constraints['walltime'], res))

    for pred in predicates:
        resources = itertools.ifilter(pred, resources)

    return resources


