# -- coding: UTF-8 --

import re
import string
from sqlalchemy import *

class ListaModel:
    def __init__(self):
        db = create_engine('mysql://root:@localhost/listas_publicas')
        metadata = MetaData(db)
        self.lista_table = Table('lista', metadata, autoload=True)
        self.item_table = Table('item', metadata, autoload=True)
    
    def __get_result__(self, select, fetchone=False):
        rs = select.execute()
        if fetchone:
            return rs.fetchone()
        return rs.fetchall()
    
    def __get_listas_slugs__(self):
        """ Retorna todas as listas no BD """
        select_lista = self.lista_table.select()
        listas_result = self.__get_result__(select_lista)
        slugs = []
        for lista in listas_result:
            slug = lista[2]
            slugs.append(slug)
        return slugs
    
    def get_lista(self, slug_lista):
        select_lista = self.lista_table.select(self.lista_table.c.slug == slug_lista)
        result = self.__get_result__(select_lista, fetchone=True)
        if result:
            return {"id": result[0], "nome": result[1], "slug": result[2], "lista_pai": result[3]}
        else:
            return None
    
    def get_sublistas(self, lista_pai_id):
        select_lista = self.lista_table.select(self.lista_table.c.lista_pai == lista_pai_id)
        sublistas_result = self.__get_result__(select_lista)
        sublistas = []
        for lista in sublistas_result:
            sublistas.append({"id": lista[0], "nome": lista[1], "slug": lista[2], "lista_pai": lista[3]})
        return sublistas
    
    def get_itens(self, lista_id):
        select_itens = self.item_table.select(self.item_table.c.lista_id == lista_id)
        itens_result = self.__get_result__(select_itens)
        itens = []
        for item in itens_result:
            itens.append({"id": item[0], "nome": item[1], "lista_id": item[2]})
        return itens
    
    def __get_nome_lista__(self, slug_lista):
        nome_lista = slug_lista.split("/")[-1]
        nome_lista = " ".join( nome_lista.split("-") ) # Exemplo: aniversario-guilherme-2012 vira aniversario guilherme 2012
        nome_lista = string.capwords(nome_lista) # Exemplo: aniversario guilherme 2012 vira Aniversario Guilherme 2012
        return nome_lista
        
    def __insere_nova_lista__(self, slug_lista, lista_pai):
        """ Insere uma lista na qual já se sabe o slug e a sua lista pai """
    
        insert_lista = self.lista_table.insert()
        nome_lista = self.__get_nome_lista__(slug_lista)
        
        if lista_pai:
            insert_lista.execute(nome=nome_lista, slug=slug_lista, lista_pai=lista_pai["id"])
        else:
            insert_lista.execute(nome=nome_lista, slug=slug_lista)
    
    def __get_lista_pai__(self, slug_lista, slugs_BD):
        """ Verifica se a lista pai já existe no banco e se não existir cria ela a retorna """
        
        slug_pai_list = slug_lista.split("/")[0:-1]
        slug_pai = "/".join(slug_pai_list)
        
        if slug_pai == "": # Não se cria uma lista pai se a lista está sendo adicionada na Raiz
            return None
        
        if slug_pai not in slugs_BD: # Se a lista não existe
            lista_pai = self.__get_lista_pai__(slug_pai, slugs_BD)
            self.__insere_nova_lista__(slug_pai, lista_pai)
        
        return self.get_lista(slug_pai)

    def cria_nova_lista(self, slug_lista):
        """ Insere uma lista na qual já se sabe o slug, porém a sua lista pai pode não ter sido criada ainda"""
        
        slugs_BD = self.__get_listas_slugs__() # Recebe todos os slugs do BD, para ser mais rápido de criar novas listas
        
        lista_pai = self.__get_lista_pai__(slug_lista, slugs_BD)
        self.__insere_nova_lista__(slug_lista, lista_pai)
    
    def __eh_url_valida__(self, url):
        url_regex = r"^(http[s]?://|ftp://)?(www\.)?[a-zA-Z0-9-\.]+\.(com|org|net|mil|edu|ca|co.uk|com.au|gov|br)$"
        m_obj = re.search(url_regex, url)
        return True if m_obj else False
    
    def add_itens(self, novos_itens_nomes, lista_id):
        novos_itens = []
        for nome in novos_itens_nomes:
            nome = nome.strip()
            if self.__eh_url_valida__(nome):
                nome = "<a href='%s'>%s</a>" % (nome, nome)
            if nome != "":
                novos_itens.append({"nome": nome, "lista_id": lista_id})
        
        insert_itens = self.item_table.insert()
        insert_itens.execute(novos_itens)

