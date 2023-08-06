import unittest
import ripe.tinyurl.browser.tinyurl as tu
from ripe.tinyurl.testing import TINYURL_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import login
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName

hashed = 'cXbMCZIvBgczDvE1RNBcPw=='
url = "http://www.testurl.com/test/test"


class TinyTestCase(unittest.TestCase):

    layer = TINYURL_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_test(self):
        self.assertTrue(True)

    def test_encode_url(self):
        self.assertEquals(tu.encode_url(url), hashed)

    def test_encode_url_len(self):
        length = '5'
        self.assertEquals(tu.encode_url_len(hashed, length), 'cXbMC')
        length = '6'
        self.assertNotEquals(tu.encode_url_len(hashed, length), 'cXbMC')

    def test_id_exists(self):
        ids = ['1', '2', '3', '4']
        new_id = 'a'
        self.assertEquals(tu.id_exists(new_id, ids), False)
        new_id = '1'
        self.assertEquals(tu.id_exists(new_id, ids), True)

    def test_create_link(self):
        portal = self.layer['portal']
        wf = getToolByName(portal, 'portal_workflow')
        cat = getToolByName(portal, 'portal_catalog')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        # create a folder
        self.portal.invokeFactory('Folder', 'test-folder')
        parent = portal['test-folder']
        self.assertEquals(tu.create_link(parent, url, '5', wf, cat),
                          {'msg': '', 'hashid': 'cXbMC'})

    def test_valid_url(self):
        url = ''
        self.assertEquals(tu.valid_url(url), 'Please enter a URL')
        url = 'http//'
        self.assertEquals(tu.valid_url(url), 'Please enter a valid URL')
        url = 'http://www.test.com'
        self.assertEquals(tu.valid_url(url), '')

    def test_link_exists(self):
        portal = self.layer['portal']
        cat = getToolByName(portal, 'portal_catalog')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'test-folder')
        parent = portal['test-folder']
        parent.invokeFactory('Link', 'cXbMCtttt', remoteUrl=url)
        self.assertEquals(tu.link_exists(cat, 'cXbMCtttt', url),
                          {'hashid': 'cXbMCtttt',
                           'msg':
                           'The URL has already been applied to the site'})
