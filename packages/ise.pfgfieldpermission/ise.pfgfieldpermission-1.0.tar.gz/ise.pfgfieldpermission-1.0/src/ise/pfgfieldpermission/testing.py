from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class IsepfgfieldpermissionLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ise.pfgfieldpermission
        xmlconfig.file(
            'configure.zcml',
            ise.pfgfieldpermission,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ise.pfgfieldpermission:default')

ISE_PFGFIELDPERMISSION_FIXTURE = IsepfgfieldpermissionLayer()
ISE_PFGFIELDPERMISSION_INTEGRATION_TESTING = IntegrationTesting(
    bases=(ISE_PFGFIELDPERMISSION_FIXTURE,),
    name="IsepfgfieldpermissionLayer:Integration"
)
ISE_PFGFIELDPERMISSION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(ISE_PFGFIELDPERMISSION_FIXTURE, z2.ZSERVER_FIXTURE),
    name="IsepfgfieldpermissionLayer:Functional"
)
