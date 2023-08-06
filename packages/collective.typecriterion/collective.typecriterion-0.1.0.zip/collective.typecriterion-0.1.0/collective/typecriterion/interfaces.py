# -*- coding: utf8 -*-

from zope.interface import Interface
from zope import schema

from collective.typecriterion import _
from collective.typecriterion.persistent import IRowTypesCriterionSettings 
from collective.typecriterion.persistent import PersistentObject


class ITypeCriterionLayer(Interface):
    """Marker interface for collective.typecriterion browser layer"""


class ITypesCriterionSettings(Interface):
    """Settings used in the control panel for types criterion"""

    type_criterion_defined = schema.Tuple(
            title=_(u"Content type"),
            description=_(u"A new general content type for criteria collections"),
            required=False,
            default=(),
            missing_value=(),
            value_type=PersistentObject(IRowTypesCriterionSettings, title=_(u"Type configuration")),
    )

