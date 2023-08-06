# -*- coding: utf-8 -*-
from unittest import TestCase
import datetime

from api import WikipediaParserAPI


class WikipediaParserAPITest(TestCase):
    def test_get_wiki_date_jo_soares_url(self):
        wp = WikipediaParserAPI('http://pt.wikipedia.org/wiki/J%C3%B4_Soares')
        assert u'Jô Soares' == wp.get_nome()
        assert datetime.datetime(1938, 1, 16) == wp.get_nascimento()
        assert None == wp.get_falecimento()

    def test_get_wiki_date_jo_soares_contexto(self):
        wp = WikipediaParserAPI(contexto='J%C3%B4_Soares')
        assert u'Jô Soares' == wp.get_nome()
        assert datetime.datetime(1938, 1, 16) == wp.get_nascimento()
        assert None == wp.get_falecimento()

    def test_get_wiki_date_rubinho(self):
        wp = WikipediaParserAPI('http://pt.wikipedia.org/wiki/Rubens_Barrichello')
        assert u'Rubens Barrichello' == wp.get_nome()
        assert datetime.datetime(1972, 5, 23) == wp.get_nascimento()
        assert None == wp.get_falecimento()

    def test_get_wiki_date_cartola(self):
        wp = WikipediaParserAPI('http://pt.wikipedia.org/wiki/Cartola_(compositor)')
        assert u'Cartola' == wp.get_nome()
        assert datetime.datetime(1908, 10, 11) == wp.get_nascimento()
        assert datetime.datetime(1980, 11, 30) == wp.get_falecimento()

    def test_get_wiki_date_tim_maia(self):
        wp = WikipediaParserAPI('http://pt.wikipedia.org/wiki/Tim_Maia')
        assert u'Tim Maia' == wp.get_nome()
        assert datetime.datetime(1942, 9, 28) == wp.get_nascimento()
        assert datetime.datetime(1998, 3, 15) == wp.get_falecimento()

    def test_get_wiki_date_itamar_franco(self):
        wp = WikipediaParserAPI('http://pt.wikipedia.org/wiki/Itamar_Franco')
        assert u'Itamar Franco' == wp.get_nome()
        assert datetime.datetime(1930, 6, 28) == wp.get_nascimento()
        assert datetime.datetime(2011, 7, 2) == wp.get_falecimento()

    def test_get_wiki_date_renato_portaluppi(self):
        wp = WikipediaParserAPI('http://pt.wikipedia.org/wiki/Renato_Ga%C3%BAcho')
        assert u'Renato Portaluppi' == wp.get_nome()
        assert datetime.datetime(1962, 9, 9) == wp.get_nascimento()
        assert None == wp.get_falecimento()

    def test_get_wiki_date_paulo_henrique_ganso(self):
        wp = WikipediaParserAPI('http://pt.wikipedia.org/wiki/Paulo_Henrique_Ganso')
        print wp.get_nome()
        assert u'Paulo Henrique Chagas de Lima' == wp.get_nome()
        assert datetime.datetime(1989, 10, 12) == wp.get_nascimento()
        assert None == wp.get_falecimento()