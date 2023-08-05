# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements


from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces.plugins import IUserEnumerationPlugin

from silva.core.interfaces import IMember

manage_addMembershipPluginForm = PageTemplateFile("../www/membershipAddForm",
                globals(), __name__="manage_addMembershipPluginForm")

def manage_addMembershipPlugin(self, id, title='', REQUEST=None):
    """Add a membership plugin to a Pluggable Authentication Service.
    """
    p=MembershipPlugin(id, title)
    self._setObject(p.getId(), p)

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect("%s/manage_workspace"
                "?manage_tabs_message=Membership+plugin+added." %
                self.absolute_url())


class MembershipPlugin(BasePlugin):
    """Plugin retrieving users defined in Silva
    """

    meta_type = 'Silva Membership PAS Plugin'
    security = ClassSecurityInfo()

    implements(IUserEnumerationPlugin)

    def __init__(self, id, title=None):
        self._setId(id)
        self.title=title


    def enumerateUsers(self, id=None, login=None,
                       exact_match=False,
                       sort_by=None,
                       max_results=None,
                       **kw
                       ):
        root = self.get_root()
        members = root.Members
        if login is None:
            login = id
        if exact_match:
            # Optimization for exact_match
            user = getattr(members, login, None)
            if user is not None and IMember.providedBy(user):
                return {'id': login,
                        'login': login,
                        'pluginid': self.getId()},
            return tuple()
        users = []
        for user_id, user in members.objectItems():
            if IMember.providedBy(user):
                if user_id.startswith(login):
                    users.append({'id': user_id,
                                  'login': user_id,
                                  'pluginid': self.getId()})
        return tuple(users)

