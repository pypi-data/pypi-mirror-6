# -*- coding: utf-8 -*-

from interlegis.portalmodelo.buscadores.portlets import lexml
from interlegis.portalmodelo.buscadores.testing import INTEGRATION_TESTING
from plone import api
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class PortletTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_portlet_type_registered(self):
        name = 'interlegis.portalmodelo.buscadores.portlets.lexml'
        last = getUtility(IPortletType, name=name)
        self.assertEqual(last.addview, name)

    def test_interfaces(self):
        last = lexml.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(last))
        self.assertTrue(IPortletDataProvider.providedBy(last.data))

    def test_invoke_add_view(self):
        name = 'interlegis.portalmodelo.buscadores.portlets.lexml'
        last = getUtility(IPortletType, name=name)
        path = '++contextportlets++plone.leftcolumn'
        mapping = self.portal.restrictedTraverse(path)

        for m in mapping.keys():
            del mapping[m]

        with api.env.adopt_roles(['Manager']):
            addview = mapping.restrictedTraverse('+/' + last.addview)
           # This is a NullAddForm - calling it does the work
            addview()

        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], lexml.Assignment))

    def test_obtain_renderer(self):
        context = self.portal
        request = self.request
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(
            IPortletManager, name='plone.rightcolumn', context=context)

        assgmnt1 = lexml.Assignment()

        renderer1 = getMultiAdapter(
            (context, request, view, manager, assgmnt1), IPortletRenderer)

        self.assertTrue(isinstance(renderer1, lexml.Renderer))
