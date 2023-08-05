# -*- coding: utf-8 -*-
from zope.intid.interfaces import IIntIds
from zope.component import getUtility
from brasil.gov.portal.testing import INTEGRATION_TESTING
from brasil.gov.portal.browser.viewlets.destaques import Destaques_Viewlet
from brasil.gov.portal.browser.viewlets.logo import LogoViewlet
from brasil.gov.portal.browser.viewlets.redes import RedesSociaisViewlet
from brasil.gov.portal.browser.viewlets.related import RelatedItemsViewlet
from brasil.gov.portal.browser.viewlets.servicos import ServicosViewlet
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from z3c.relationfield import RelationValue

import unittest


class DestaquesViewletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('collective.cover.content',
                                  'destaques', title=u'Destaques')
        self.destaques = self.portal['destaques']

    def viewlet(self, context=None):
        context = context or self.portal
        viewlet = Destaques_Viewlet(context, self.request, None, None)
        viewlet.update()
        return viewlet

    def test_available(self):
        viewlet = self.viewlet()
        self.assertTrue(viewlet.available())

    def test_not_available_on_folder(self):
        self.portal.invokeFactory('Folder',
                                  'folder', title=u'Uma pasta')
        viewlet = self.viewlet(self.portal['folder'])
        self.assertFalse(viewlet.available())

    def test_not_available(self):
        # Apagamos a capa de destaques
        self.portal.manage_delObjects(['destaques'])
        viewlet = self.viewlet()
        self.assertFalse(viewlet.available())

    def test_available_for_different_content_type(self):
        portal = self.portal
        # Apagamos a capa de destaques
        portal.manage_delObjects(['destaques'])
        # Colocamos uma pasta no mesmo lugar
        portal.invokeFactory('Folder',
                             'destaques', title=u'Destaques')
        viewlet = self.viewlet()
        # O Viewlet deve detectar o problema e nao exibir nada
        self.assertFalse(viewlet.available())

    def test_editable(self):
        viewlet = self.viewlet()
        self.assertTrue(viewlet.editable())

    def test_not_editable_by_anonymous(self):
        logout()
        viewlet = self.viewlet()
        self.assertFalse(viewlet.editable())

    def test_portal_url(self):
        logout()
        viewlet = self.viewlet()
        self.assertEqual(viewlet.portal_url,
                         self.portal.portal_url())


class LogoViewletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal.title = u'Portal Brasil'
        self.portal.title_1 = u'Portal'
        self.portal.title_2 = u'Brasil'
        self.portal.orgao = u'Presidencia da República'
        self.portal.description = u'O portal do Brasil'

    def viewlet(self):
        viewlet = LogoViewlet(self.portal, self.request, None, None)
        viewlet.update()
        return viewlet

    def test_title(self):
        expected = self.portal.title
        viewlet = self.viewlet()
        self.assertEqual(viewlet.title(), expected)

    def test_title_1(self):
        expected = self.portal.title_1
        viewlet = self.viewlet()
        self.assertEqual(viewlet.title_1(), expected)

    def test_title_2(self):
        expected = self.portal.title_2
        viewlet = self.viewlet()
        self.assertEqual(viewlet.title_2(), expected)

    def test_title_2_class(self):
        # texto curto
        self.portal.title_2 = u'Brasil'
        viewlet = self.viewlet()
        self.assertEqual(viewlet.title_2_class(), 'corto')
        # texto longo
        self.portal.title_2 = u'Desenvolvimento Social e Combate à Fome'
        viewlet = self.viewlet()
        self.assertEqual(viewlet.title_2_class(), 'luongo')

    def test_orgao(self):
        expected = self.portal.orgao
        viewlet = self.viewlet()
        self.assertEqual(viewlet.orgao(), expected)

    def test_description(self):
        expected = self.portal.description
        viewlet = self.viewlet()
        self.assertEqual(viewlet.description(), expected)

    def test_portal(self):
        expected = self.portal
        viewlet = self.viewlet()
        self.assertEqual(viewlet.portal(), expected)


class RedesViewletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.sheet = self.portal.portal_properties.brasil_gov
        self.sheet.manage_changeProperties(social_networks=[
            'twitter|portalbrasil',
        ])

    def viewlet(self):
        viewlet = RedesSociaisViewlet(self.portal, self.request, None, None)
        viewlet.update()
        return viewlet

    def test_available(self):
        viewlet = self.viewlet()
        self.assertTrue(viewlet.available())

    def test_not_available(self):
        # Removemos a configuracao de redes sociais
        self.sheet.manage_changeProperties(social_networks=[])
        viewlet = self.viewlet()
        self.assertFalse(viewlet.available())

    def test_redes(self):
        viewlet = self.viewlet()
        redes = viewlet.redes
        self.assertEqual(len(redes), 1)
        self.assertEqual(redes[0]['site'], 'twitter')


class RelatedViewletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        intids = getUtility(IIntIds)
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Link', 'servico-1', title=u'Servico 1')
        to_id = intids.getId(self.portal['servico-1'])
        self.portal.invokeFactory('collective.nitf.content',
                                  'artigo', title=u'Artigo')
        self.artigo = self.portal['artigo']
        self.artigo.relatedItems = [RelationValue(to_id), ]

    def viewlet(self, context=None):
        if not context:
            context = self.artigo
        viewlet = RelatedItemsViewlet(context, self.request, None, None)
        viewlet.update()
        return viewlet

    def test_related(self):
        viewlet = self.viewlet()
        self.assertEqual(len(viewlet.related()), 1)

    def test_related_on_type_without_behavior(self):
        self.portal.invokeFactory('Audio',
                                  'audio', title=u'Audio')
        audio = self.portal['audio']
        audio_file = audio.invokeFactory('MPEG Audio File',
                                         'file.mp3')
        viewlet = self.viewlet(audio_file)
        self.assertEqual(len(viewlet.related()), 0)


class ServicosViewletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'servicos')
        self.servicos = self.portal['servicos']
        self.servicos.invokeFactory('Link', 'servico-1', title=u'Servico 1')
        self.servicos.invokeFactory('Link', 'servico-2', title=u'Servico 2')

    def viewlet(self):
        viewlet = ServicosViewlet(self.portal, self.request, None, None)
        viewlet.update()
        return viewlet

    def test_available(self):
        viewlet = self.viewlet()
        self.assertTrue(viewlet.available())

    def test_not_available(self):
        # Apagamos a pasta servicos
        self.portal.manage_delObjects(['servicos'])
        viewlet = self.viewlet()
        self.assertFalse(viewlet.available())

    def test_servicos(self):
        viewlet = self.viewlet()
        servicos = viewlet.servicos()
        self.assertEqual(len(servicos), 2)
        self.assertEqual(servicos[0].Title, u'Servico 1')
        self.assertEqual(servicos[1].Title, u'Servico 2')
