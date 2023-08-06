**********************************
interlegis.portalmodelo.buscadores
**********************************

.. contents:: Conteúdo
   :depth: 2

Introdução
==========

Este pacote define portlets e browser pages especiais para integrar buscas,
dentro do Portal Modelo, dos seguintes sites externos:

* `LexML Brasil`_ (Rede de Informação Legislativa e Jurídica)
* `Buscador Legislativo`_ do Interlegis

As buscas são integradas através de ``iframes``.

.. _`LexML Brasil`: http://www.lexml.gov.br/
.. _`Buscador Legislativo`: http://busca.interlegis.leg.br/

Implementação
=============

A implementação das buscas é feita em duas partes: um portlet fornece um
formulário para realizar a busca e chama um browser page que inclui um iframe
com o link de resultados da busca no buscador especificado.

Portlets
--------

Os seguintes portles são registrados:

* ``interlegis.portalmodelo.buscadores.portlets.lexml`` para o `LexML Brasil`_
* ``interlegis.portalmodelo.buscadores.portlets.buscaleg`` para o
  `Buscador Legislativo`_

Browser pages
-------------

As seguintes browser pages de resultados são registradas:

* ``/lexml`` para o `LexML Brasil`_
* ``/buscaleg`` para o `Buscador Legislativo`_
