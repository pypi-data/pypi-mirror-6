# -*- coding: utf-8 -*-
"""Base module for unittesting."""
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing import z2

import unittest2 as unittest

import collective.local.contentrules
from plone import api


class ContentrulesLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        self.loadZCML(package=collective.local.contentrules,
                      name='testing.zcml')
        z2.installProduct(app, 'collective.local.contentrules')

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        from ecreall.helpers.testing.member import createMembers
        createMembers(portal, USERDEFS, log_in=False)
        api.content.create(portal, 'Folder', 'workspace')
        portal.workspace.manage_setLocalRoles('editor', ['Editor'])
        portal.workspace.manage_setLocalRoles('reader', ['Reader'])
        portal.workspace.reindexObject()

        # Commit so that the test browser sees these objects
        import transaction
        transaction.commit()

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, 'collective.local.contentrules')


FIXTURE = ContentrulesLayer(
    name="FIXTURE"
    )


INTEGRATION = IntegrationTesting(
    bases=(FIXTURE,),
    name="INTEGRATION"
    )

USERDEFS = [
            {'user': 'superadmin', 'roles': ('Member', 'Manager'), 'groups': ()},
            {'user': 'member', 'roles': ('Member', ), 'groups': ()},
            {'user': 'reader', 'roles': ('Member', ), 'groups': ()},
            {'user': 'editor', 'roles': ('Member', ), 'groups': ()},
            ]

class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']