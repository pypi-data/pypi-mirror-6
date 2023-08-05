# -*- coding: utf-8 -*-

from five import grok

from AccessControl.security import checkPermission
from Products.CMFCore.utils import getToolByName

from seantis.dir.events.interfaces import IEventsDirectoryItem, IActionGuard

groups = {
    u'baar': u'Verwaltung Baar',
    u'cham': u'Verwaltung Cham',
    u'huenenberg': u'Verwaltung Hünenberg',
    u'menzingen': u'Verwaltung Menzingen',
    u'neuheim': u'Verwaltung Neuheim',
    u'oberaegeri': u'Verwaltung Oberägeri',
    u'risch': u'Verwaltung Risch',
    u'stadt-zug': u'Verwaltung Stadt Zug',
    u'steinhausen': u'Verwaltung Steinhausen',
    u'unteraegeri': u'Verwaltung Unterägeri',
    u'walchwil': u'Verwaltung Walchwil',
    u'andere-orte': u'Verwaltung Andere Orte'
}


class ZugActionGuard(grok.Adapter):
    grok.context(IEventsDirectoryItem)
    grok.implements(IActionGuard)

    @property
    def portal_groups(self):
        return getToolByName(self.context, 'portal_groups')

    @property
    def current_user(self):
        return getToolByName(self.context, 'portal_membership')

    @property
    def usergroups(self):
        return map(
            lambda g: g.getGroupId().replace('verwaltung-', ''),
            self.portal_groups.getGroupsByUserId(
                self.current_user.getAuthenticatedMember().id
            )
        )

    @property
    def anonymous(self):
        return self.current_user.isAnonymousUser() != 0

    def allow_action(self, action):

        if action == 'submit':
            return True

        if checkPermission('cmf.ManagePortal', self.context):
            return True

        usergroups = self.usergroups

        for town in self.context.keywords(categories=['cat2']):
            town = town.lower()

            town = town.replace(' ', '-')

            town = town.replace(u'ü', 'ue')
            town = town.replace(u'ö', 'oe')
            town = town.replace(u'ä', 'ae')

            if town in usergroups:
                return True

        return False
