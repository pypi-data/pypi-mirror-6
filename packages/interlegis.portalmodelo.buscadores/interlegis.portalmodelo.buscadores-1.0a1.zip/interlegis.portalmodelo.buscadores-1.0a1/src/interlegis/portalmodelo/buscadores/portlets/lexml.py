# -*- coding: utf-8 -*-

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class ILexMLPortlet(IPortletDataProvider):
    """A portlet which renders a search form for LexML Brasil.
    """


class Assignment(base.Assignment):
    implements(ILexMLPortlet)

    title = _(u'Search on LexML Brazil')


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('lexml.pt')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
