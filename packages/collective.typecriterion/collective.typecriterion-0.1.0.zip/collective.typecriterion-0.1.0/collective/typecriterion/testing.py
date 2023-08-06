# -*- coding: utf-8 -*-

from zope.configuration import xmlconfig

from plone.testing import z2

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

class TypeCriterionLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import collective.typecriterion
        xmlconfig.file('configure.zcml',
                       collective.typecriterion,
                       context=configurationContext)
        z2.installProduct(app, 'collective.typecriterion')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.typecriterion:default')
        #quickInstallProduct(portal, 'collective.typecriterion')
        setRoles(portal, TEST_USER_ID, ['Member', 'Manager'])


TYPE_CRITERION_FIXTURE = TypeCriterionLayer()
TYPE_CRITERION_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(TYPE_CRITERION_FIXTURE, ),
                       name="TypeCriterion:Integration")
TYPE_CRITERION_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(TYPE_CRITERION_FIXTURE, ),
                       name="TypeCriterion:Functional")

