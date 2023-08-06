# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView


class LexMLResults(BrowserView):
    """Define the page used to return the results of the external search on
    the LexML Brasil site. The implementation is iframe-based on ``lexml.pt``.
    """
