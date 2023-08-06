# -*- coding: utf-8 -*-

from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implements

PROJECTNAME = 'interlegis.portalmodelo.buscadores'


class HiddenProfiles(object):
    implements(INonInstallable)

    def getNonInstallableProfiles(self):
        return [
            u'interlegis.portalmodelo.buscadores:uninstall',
            u'interlegis.portalmodelo.buscadores.upgrades.v1010:default'
        ]
