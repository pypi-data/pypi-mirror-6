# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface, implements

from z3c.form.object import registerFactoryAdapter

from plone.registry.field import PersistentField

from collective.typecriterion import  _


class IRowTypesCriterionSettings(Interface):
    """Single configuration entry for types criterion"""
    
    type_name = schema.TextLine(
            title=_(u"General type name"),
            description=_(u"A descriptive name for the content type you want to define"),
            default=u"",
            missing_value=u"",
            required=True,
    )

    types_matched = schema.Tuple(
            title=_(u'Select all native content types that match'),
            description=_('help_types_matched',
                          default=u"Select all primitive content types that will be queried when this new "
                                  u"general type will be selected."),
            required=True,
            default=(),
            missing_value=(),
            value_type=schema.Choice(vocabulary=u'plone.app.vocabularies.ReallyUserFriendlyTypes'),
    )


class RowTypesCriterionSettings(object):
    implements(IRowTypesCriterionSettings)
    
    def __init__(self, type_name=u'', types_matched=()):
        self.type_name = type_name
        self.types_matched = types_matched


class PersistentObject(PersistentField, schema.Object):
    pass


registerFactoryAdapter(IRowTypesCriterionSettings, RowTypesCriterionSettings)
