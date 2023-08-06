# -*- coding:utf-8 -*-
import datetime
import requests
import re


NASCIMENTO_PATTERN = '(Nascimento|Data de nasc.)<.+?>\s<.+>(\d+?)\sde\s(\w.+)</a>\sde\s<a[^>]+?>(\d{4})'
FALECIMENTO_PATTERN = '(Data\sde\smorte|Falecimento)<.+?>\s<.+>(\d+?)\sde\s(\w.+)</a>\sde\s<a[^>]+?>(\d{4})'
NOME_1 = '<th [^>]+?><span [^>]+?>(.+)</span></th>'
NOME_2 = '<th [^>]+?>Nome completo</th>[\r\n\t]<td colspan=\"2\">(.+)</td>'
NOME_PATTERN = '('+NOME_1+'|'+NOME_2+')'


def adaptar_mes(mes):
    if mes.lower() == u'janeiro':
        return 1
    if mes.lower() == u'fevereiro':
        return 2
    if mes.lower() == u'março':
        return 3
    if mes.lower() == u'abril':
        return 4
    if mes.lower() == u'maio':
        return 5
    if mes.lower() == u'junho':
        return 6
    if mes.lower() == u'julho':
        return 7
    if mes.lower() == u'agosto':
        return 8
    if mes.lower() == u'setembro':
        return 9
    if mes.lower() == u'outubro':
        return 10
    if mes.lower() == u'novembro':
        return 11
    if mes.lower() == u'dezembro':
        return 12


class WikipediaParserAPI:

    def __init__(self, url=None, contexto=None):
        self.url = url
        self.contexto = contexto
        self.conteudo = None

    def get_conteudo(self):
        if self.conteudo:
            return self.conteudo
        if not self.url:
            self.url = 'http://pt.wikipedia.org/wiki/' + self.contexto
        return requests.get(self.url)

    def get_nome(self):
        nome_pattern = re.search(NOME_PATTERN, self.get_conteudo().text)
        nome = nome_pattern.group(2)
        if not nome:
            nome = nome_pattern.group(3)
        return nome

    def get_nascimento(self):
        nascimento = re.search(NASCIMENTO_PATTERN, self.get_conteudo().text)
        if nascimento:
            dia = int(nascimento.group(2))
            mes = adaptar_mes(nascimento.group(3))
            ano = int(nascimento.group(4))
            return datetime.datetime(ano, mes, dia)
        return None

    def get_falecimento(self):
        m_falecimento = re.search(FALECIMENTO_PATTERN, self.get_conteudo().text)
        if m_falecimento:
            dia = int(m_falecimento.group(2))
            mes = adaptar_mes(m_falecimento.group(3))
            ano = int(m_falecimento.group(4))
            return datetime.datetime(ano, mes, dia)
        return None


