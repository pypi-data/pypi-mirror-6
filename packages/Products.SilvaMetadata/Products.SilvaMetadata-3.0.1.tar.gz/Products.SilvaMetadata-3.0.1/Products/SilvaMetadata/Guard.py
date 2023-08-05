# -*- coding: utf-8 -*-
# Copyright (c) 2001-2013 Zope Corporation and Contributors. All Rights Reserved.
# See also LICENSE.txt
##############################################################################
#
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Guard conditions in a web-configurable workflow.

Changes to file as per ZPL
- 4/11/03 - permission import from accesscontrol in absense of cmf
- 4/11/03 - change expression context creation
- 4/11/03 - misc import cleanups
- 9/15/03 - import cleanups

"""

from string import split, strip, join

from AccessControl import ClassSecurityInfo, Permissions
from Acquisition import Explicit
from App.class_init import InitializeClass
from Persistence import Persistent

from Products.SilvaMetadata.Expression import Expression, createExprContext


class Guard (Persistent, Explicit):
    permissions = ()
    roles = ()
    expr = None

    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.view_management_screens)

    def check(self, sm, element, ob):
        '''
        Checks conditions in this guard.
        '''
        pp = self.permissions
        if pp:
            found = 0
            for p in pp:
                if sm.checkPermission(p, ob):
                    found = 1
                    break
            if not found:
                return 0
        roles = self.roles
        if roles:
            # Require at least one of the given roles.
            found = 0
            u_roles = sm.getUser().getRolesInContext(ob)
            for role in roles:
                if role in u_roles:
                    found = 1
                    break
            if not found:
                return 0
        expr = self.expr
        if expr is not None:
            econtext = createExprContext(ob, element)
            res = expr(econtext)
            if not res:
                return 0
        return 1

    security.declareProtected(
        Permissions.view_management_screens, 'changeFromProperties')
    def changeFromProperties(self, props):
        '''
        Returns 1 if changes were specified.
        '''
        if props is None:
            return 0
        res = 0
        s = props.get('permissions', None)
        if s:
            res = 1
            p = map(strip, split(s, ';'))
            self.permissions = tuple(p)
        else:
            self.permissions = ()
        s = props.get('roles', None)
        if s:
            res = 1
            r = map(strip, split(s, ';'))
            self.roles = tuple(r)
        else:
            self.roles = ()
        s = props.get('expression', None)
        if s:
            res = 1
            self.expr = Expression(s)
        else:
            self.expr = None
        return res

    security.declareProtected(
        Permissions.view_management_screens, 'getPermissionsText')
    def getPermissionsText(self):
        if not self.permissions:
            return ''
        return join(self.permissions, '; ')

    security.declareProtected(
        Permissions.view_management_screens, 'getRolesText')
    def getRolesText(self):
        if not self.roles:
            return ''
        return join(self.roles, '; ')

    security.declareProtected(
        Permissions.view_management_screens, 'getExprText')
    def getExprText(self):
        if not self.expr:
            return ''
        return str(self.expr.text)


InitializeClass(Guard)
