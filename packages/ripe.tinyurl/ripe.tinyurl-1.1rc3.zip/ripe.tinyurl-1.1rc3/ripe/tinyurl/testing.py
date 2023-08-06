from zope.configuration import xmlconfig
from Products.CMFCore.utils import getToolByName
from plone.testing import z2
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import setRoles
from plone.app.testing import login
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME


class RIPETinyUrl(PloneSandboxLayer):

    defaultsBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import ripe.tinyurl
        xmlconfig.file('configure.zcml',
                       ripe.tinyurl,
                       context=configurationContext)
        z2.installProduct(app, 'ripe.tinyurl')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ripe.tinyurl:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        acl_users = getToolByName(portal, 'acl_users')
        acl_users.userFolderAddUser(
            'contributor',
            'secret',
            ['Member', 'Contributor'],
            []
        )

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'ripe.tinyurl')


RIPE_TINYURL_FIXTURE = RIPETinyUrl()


TINYURL_INTEGRATION_TESTING = IntegrationTesting(
    bases=(RIPE_TINYURL_FIXTURE,),
    name="RIPETinyUrlFixture:Integration")

TINYURL_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(RIPE_TINYURL_FIXTURE,),
    name="RIPETinyUrlFixture:Functional")
