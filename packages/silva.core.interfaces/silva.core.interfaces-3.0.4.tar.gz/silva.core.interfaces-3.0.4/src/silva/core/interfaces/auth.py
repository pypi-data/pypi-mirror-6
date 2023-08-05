# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from zope import interface, schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from silva.translations import translate as _


class IMember(interface.Interface):
    """A Silva member object.
    """

    def userid():
        """Return unique identifer for member (username).
        """

    def fullname():
        """Return full name of the menber.
        """

    def email():
        """Return user's email address if known, None otherwise.
        """

    def extra(name):
        """Return bit of extra information, keyed by name.
        """

    def allowed_roles():
        """Private method which return a list of roles that that user
        can have.
        """


class IEditableMember(IMember):
    """A member which is able to see its information to be modified.
    """

    def set_email(email):
        """Change member email.
        """

    def set_fullname(fullname):
        """Change member fullname.
        """


class IGroup(interface.Interface):
    """A group can be used to group users and give them roles.
    """

    def groupid():
        """Return group unique identifier.
        """

    def groupname():
        """Return friendly group name (or identifier if unknown).
        """

    def allowed_roles():
        """Private method which return a list of roles that that the
        group can have.
        """


class IAccessSecurity(interface.Interface):
    """Adapter to manage access restriction to a content.
    """
    minimum_role = interface.Attribute(
        u"Property giving access to ``set_minimum_role``/``get_minimum_role``.")
    acquired = interface.Attribute(u"Property giving access to ``is_acquired``.")

    def set_acquired():
        """Set the access restriction to acquire its settings (remove
        any restriction set if any).
        """

    def is_acquired():
        """Check whether the access restriction is acquired (the
        current restriction is set on one of the parents, not the
        content itself).
        """

    def set_minimum_role(role):
        """Set ``role`` as the minimum role needed to access this
        content.

        If ``role`` is Anonymous, the access restriction will be
        acquired.
        """

    def get_minimum_role():
        """Get the minimum role needed to access the content here.
        """

def _add_silva_role(terms):
    for value, title in [('Viewer', _('Viewer')),
                         ('Viewer +', _('Viewer +')),
                         ('Viewer ++', _('Viewer ++')),
                         ('Reader', _('Reader')),
                         ('Author', _('Author')),
                         ('Editor', _('Editor')),
                         ('ChiefEditor', _('ChiefEditor')),
                         ('Manager', _('Manager')),]:
        terms.append(SimpleTerm(value=value, token=value, title=title))

@apply
def role_vocabulary():
    terms = [SimpleTerm(value=None, token='None', title=_(u'select:'))]
    _add_silva_role(terms)
    return SimpleVocabulary(terms)


@apply
def authenticated_role_vocabulary():
    terms = [SimpleTerm(value=None, token='None', title=_(u'select:')),
             SimpleTerm(value='Authenticated',
                        token='Authenticated',
                        title=_('Authenticated'))]
    _add_silva_role(terms)
    return SimpleVocabulary(terms)


class IAuthorization(interface.Interface):
    """Describe all authorizations (accorded roles) of a user a group.
    """
    identifier = schema.TextLine(
        title=_(u"identifier"),
        description=u"unique identifier of the authorized entity.")
    name = schema.TextLine(
        title=_(u'name'),
        description=u'full name of the authorized entity.')
    type = interface.Attribute(
        u"``user`` or ``group`` depending of the authorized entity.")
    acquired_role = schema.Choice(
        title=_(u"role defined above"),
        description=u"list of roles that the entity as above this content.",
        source=role_vocabulary,
        required=False)
    local_role = schema.Choice(
        title=_(u"role defined here"),
        description=u"list of roles that the entity as here on this content.",
        source=role_vocabulary,
        required=False)
    role = schema.Choice(
        title=_(u'role'),
        description=u'role that the entity have at this level ' \
            u'(local or acquired role).',
        source=role_vocabulary,
        required=True)
    email = schema.TextLine(
        title=_(u"email"),
        description=_(u"email associated to the entity, ``None`` if group."),
        required=False)

    def grant(role):
        """Grant a new role to the user, if it doesn't already have it
        The current user must have at least that role for this
        operation to succeed.
        """

    def revoke():
        """Revoke all Silva roles defined at this level for this user,
        if the current user have at least that role for this operation
        to succeed.
        """


class IAuthorizationManager(interface.Interface):
    """Adapter to manage authorization access at a given level.
    """

    def get_user_id(identifier=None):
        """Return the current user identifier, or ``identifier``.
        """

    def get_user_role(identifier=None):
        """Return a list of roles that ``identifier`` has. If ``identifier``
        is None, return a list of roles for currently authenticated
        user.
        """

    def get_authorization(identifer=None, dont_acquire=False):
        """Return an authorization object for the given user or group
        identified by ``identifier``.

        If no ``identifier`` is specified, return authorization object
        for the currently authenticated user.

        If ``dont_acquire`` is set to True, no acquired roles would be
        looked up (only local roles set on the context object).
        """

    def get_authorizations(identifiers, dont_acquire=False):
        """Return all authorizations objects at this level for the
        given list of users or groups identified by ``identifiers``.

        If ``dont_acquire`` is set to True, no acquired roles would be
        looked up (only local roles).
        """

    def get_defined_authorizations(dont_acquire=False):
        """Return current all authorizations objects that defines all
        authorization set in Silva for users and groups at this
        level.

        If ``dont_acquire`` is set to True, no acquired roles would be
        looked up (only local roles).
        """


__all__ = [
    'IMember', 'IEditableMember', 'IGroup',
    'IAccessSecurity', 'IAuthorizationManager', 'IAuthorization',
    'authenticated_role_vocabulary', 'role_vocabulary']
