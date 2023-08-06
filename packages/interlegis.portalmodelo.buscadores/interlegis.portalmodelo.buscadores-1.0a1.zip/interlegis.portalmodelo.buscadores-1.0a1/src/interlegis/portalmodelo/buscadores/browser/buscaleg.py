# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView


class BuscaLegResults(BrowserView):
    """Define the page used to return the results of the external search on
    the Buscador Legislativo site. The implementation is iframe-based on
    ``buscaleg.pt``.
    """
