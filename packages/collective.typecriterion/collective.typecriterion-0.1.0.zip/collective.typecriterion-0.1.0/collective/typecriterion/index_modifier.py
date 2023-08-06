# -*- coding: utf8 -*-

from zope.interface import implements
from zope.component import queryUtility
from plone.app.querystring.interfaces import IParsedQueryIndexModifier
from plone.registry.interfaces import IRegistry 
from collective.typecriterion.interfaces import ITypesCriterionSettings


class GeneralTypeIndexModifier(object):
    """When querying for general_type you are asking for a set of portal_type"""

    implements(IParsedQueryIndexModifier)

    def __call__(self, value):
        query = value['query']
        if query:
            res_query = []
            registry = queryUtility(IRegistry)
            settings = registry.forInterface(ITypesCriterionSettings, check=False)
            for gtype in query:
                for conf in settings.type_criterion_defined:
                    if gtype==conf.type_name:
                        res_query.extend(list(conf.types_matched))
            value['query'] = res_query
        return ('portal_type', value)
