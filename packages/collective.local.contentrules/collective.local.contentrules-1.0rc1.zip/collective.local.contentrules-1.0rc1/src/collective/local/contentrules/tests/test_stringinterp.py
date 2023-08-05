# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""
from Products.DCWorkflow.utils import modifyRolesForPermission
from plone import api
from plone.stringinterp.interfaces import IStringInterpolator
from plone.app.testing.helpers import login

from collective.local.contentrules.testing import IntegrationTestCase


class TestStringinterp(IntegrationTestCase):

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        login(self.portal, 'superadmin')
        self.doc = api.content.create(self.portal.workspace, 'Document', 'document')

    def hide(self, doc):
        modifyRolesForPermission(doc, 'View', ('Manager', 'Owner'))

    def test_allowed_member_emails(self):
        """Test if collective.local.contentrules is installed with portal_quickinstaller."""
        emails = IStringInterpolator(self.doc)("${allowed_member_emails}")
        self.assertEqual(emails, u'member@example.com, reader@example.com, editor@example.com, superadmin@example.com')

        self.hide(self.doc)
        emails = IStringInterpolator(self.doc)("${allowed_member_emails}")
        self.assertEqual(emails, 'superadmin@example.com')

    def test_allowed_reader_emails(self):
        """Test if collective.local.contentrules is installed with portal_quickinstaller."""
        emails = IStringInterpolator(self.doc)("${allowed_reader_emails}")
        self.assertEqual(emails, 'reader@example.com')

        self.hide(self.doc)
        emails = IStringInterpolator(self.doc)("${allowed_reader_emails}")
        self.assertEqual(emails, '')

    def test_allowed_editor_emails(self):
        """Test if collective.local.contentrules is installed with portal_quickinstaller."""
        emails = IStringInterpolator(self.doc)("${allowed_editor_emails}")
        self.assertEqual(emails, 'editor@example.com')

        self.hide(self.doc)
        emails = IStringInterpolator(self.doc)("${allowed_editor_emails}")
        self.assertEqual(emails, '')
