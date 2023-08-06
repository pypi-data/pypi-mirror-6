from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class CollectivecustomoverridesLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.customoverrides
        xmlconfig.file(
            'configure.zcml',
            collective.customoverrides,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')


COLLECTIVE_CUSTOMOVERRIDES_FIXTURE = CollectivecustomoverridesLayer()
COLLECTIVE_CUSTOMOVERRIDES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_CUSTOMOVERRIDES_FIXTURE,),
    name="CollectivecustomoverridesLayer:Integration"
)
COLLECTIVE_CUSTOMOVERRIDES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_CUSTOMOVERRIDES_FIXTURE, z2.ZSERVER_FIXTURE),
    name="CollectivecustomoverridesLayer:Functional"
)
