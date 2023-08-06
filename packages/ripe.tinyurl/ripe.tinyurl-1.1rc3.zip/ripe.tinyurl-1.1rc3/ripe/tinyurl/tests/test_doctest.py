import doctest
import unittest2 as unittest

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import applyProfile
from plone.testing import layered
from plone.testing.z2 import Browser

from ripe.tinyurl.testing import TINYURL_FUNCTIONAL_TESTING

optionflags = (doctest.NORMALIZE_WHITESPACE
               | doctest.ELLIPSIS
               | doctest.REPORT_NDIFF
               | doctest.REPORT_ONLY_FIRST_FAILURE)


def setUp(self):
    layer = self.globs['layer']
    # Update global variables within the tests.
    self.globs.update({
        'portal': layer['portal'],
        'request': layer['request'],
        'browser': Browser(layer['app']),
        'TEST_USER_NAME': TEST_USER_NAME,
        'TEST_USER_PASSWORD': TEST_USER_PASSWORD,
        'self': self,
    })

    portal = self.globs['portal']
    browser = self.globs['browser']

    browser.handleErrors = True
    portal.error_log._ignored_exceptions = ()

    setRoles(portal, TEST_USER_ID, ['Manager'])

    applyProfile(portal, 'Products.CMFPlone:plone')

normal_testfiles = ['RipeTinyURL.txt']


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [layered(doctest.DocFileSuite(test,
                                      optionflags=optionflags),
                 layer=TINYURL_FUNCTIONAL_TESTING)
         for test in normal_testfiles])
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
