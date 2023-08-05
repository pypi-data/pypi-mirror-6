from zope.component.hooks import getSite
from AccessControl.SecurityManagement import (
    getSecurityManager, setSecurityManager, newSecurityManager)

from Products.CMFCore.utils import getToolByName
from plone.stringinterp.adapters import MailAddressSubstitution,\
    _recursiveGetMembersFromIds, ReaderEmailSubstitution,\
    MemberEmailSubstitution, EditorEmailSubstitution

from collective.local.contentrules import PMF, _


class BaseAllowedEmailSubstitution(MailAddressSubstitution):

    def getEmailsForRole(self, role):

        portal = getSite()
        acl_users = getToolByName(portal, 'acl_users')

        # get a set of ids of members with the global role
        ids = set([p[0] for p in acl_users.portal_role_manager.listAssignedPrincipals(role)])
        # union with set of ids of members with the local role
        ids |= set([user_id for user_id, irole
                       in acl_users._getAllLocalRoles(self.context).items()
                       if role in irole])

        # get members from group or member ids
        members = _recursiveGetMembersFromIds(portal, ids)

        # get only allowed members
        allowed_members = []
        old_sm = getSecurityManager()
        try:
            for m in members:
                # m is a MemberData instance,
                # it doesn't have an allowed method on it,
                # so checkPermission doesn't properly work.
                # PloneUser have this method.
                user = acl_users.getUserById(m.getId())
                newSecurityManager(None, user)
                sm = getSecurityManager()
                if sm.checkPermission('View', self.context):
                    allowed_members.append(m)
        finally:
            setSecurityManager(old_sm)

        # get emails
        return u', '.join(self.getPropsForMembers(allowed_members, 'email'))


class AllowedMemberEmailSubstitution(BaseAllowedEmailSubstitution, MemberEmailSubstitution):

    category = PMF(u'E-Mail Addresses')
    description = _(u'Members of the site who have access to the content')


class AllowedReaderEmailSubstitution(BaseAllowedEmailSubstitution, ReaderEmailSubstitution):

    category = PMF(u'E-Mail Addresses')
    description = _(u"Users that have 'can read' role in the folder and who have read access to the content")


class AllowedEditorEmailSubstitution(BaseAllowedEmailSubstitution, EditorEmailSubstitution):

    category = PMF(u'E-Mail Addresses')
    description = _(u"Users that have 'can add' role in the folder and who have read access to the content")
