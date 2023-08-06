# -*- coding: utf-8 -*-

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class IBuscaLegPortlet(IPortletDataProvider):
    """A portlet which renders a search form for LexML Brasil.
    """


class Assignment(base.Assignment):
    implements(IBuscaLegPortlet)

    title = _(u'Search on Buscador Legislativo')


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('buscaleg.pt')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
