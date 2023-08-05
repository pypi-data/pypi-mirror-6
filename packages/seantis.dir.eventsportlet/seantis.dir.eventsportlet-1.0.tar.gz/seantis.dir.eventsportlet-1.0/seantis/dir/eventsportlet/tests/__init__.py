import unittest2 as unittest

from plone.testing import z2
from plone.app import testing
from collective.betterbrowser import new_browser

from seantis.dir.eventsportlet.tests.layer import INTEGRATION_TESTING
from seantis.dir.eventsportlet.tests.layer import FUNCTIONAL_TESTING


class IntegrationTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        pass
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def tearDown(self):
        testing.logout()

    def login_admin(self):
        """ Login as site owner (does not work with testing.login)"""
        z2.login(self.app['acl_users'], 'admin')

    def login_testuser(self):
        """ Login as test-user (does not work with z2.login)"""
        testing.login(self.portal, 'test-user')

    def logout(self):
        testing.logout()


class FunctionalTestCase(IntegrationTestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def new_browser(self):
        return new_browser(self.layer)

    def tearDown(self):
        pass
