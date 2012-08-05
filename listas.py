#-*- coding:utf-8 -*-

import re
import string
import os
import tornado
from tornado.web import Application, RequestHandler, HTTPError, StaticFileHandler
from template import render_template
from lista_model import ListaModel

class ListasHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.lista_model = ListaModel()
        self.opcao_edita_a_lista = "listas-publicas-edita-a-lista/"
        self.opcao_edita_um_item = "listas-publicas-edita-um-item/"
        self.opcao_edita_um_item_regex = r"/listas-publicas-edita-um-item/([0-9]+)/$"
        self.opcao_deleta_todos_os_itens = "listas-publicas-deleta-todos-os-itens/"
        self.opcao_deleta_a_lista = "listas-publicas-deleta-a-lista/"
        self.opcao_deleta_um_item = "listas-publicas-deleta-um-item/"
        self.opcao_deleta_um_item_regex = r"/listas-publicas-deleta-um-item/([0-9]+)/$"

    def __get_slug__(self, slug):
        while slug.count("//") > 0:
            slug = slug.replace("//", "/")
        if not slug.endswith("/"):
            slug = slug + "/"
        return slug
        
    def __get_slugs__(self, slug_lista):
        """ Retorna o slug atual (última parte) e uma lista com o slug e o href para cada pai do slug atual """
        slugs_pais = []
        href = "/"
        slugs = slug_lista.split("/")
        slug_atual = slugs[-2] + "/"
        slug_pai_list = slugs[0:-2]
        for slug in slug_pai_list:
            slug += "/"
            href += slug
            slugs_pais.append({"href": href, "slug": slug})
        
        return (slug_atual, slugs_pais)
    
    def __get_lista_id__(self, slug_lista):
        return int(self.lista_model.get_lista(slug_lista)["id"])

    def get_lista_info(self, slug_lista):
        """ Com o slug da lista, acha todas as informacoes da lista, assim como as suas sublistas e os seus itens """
        slug_lista = self.__get_slug__(slug_lista)
        lista = self.lista_model.get_lista(slug_lista)
        sublistas = self.lista_model.get_sublistas(lista["id"]) if lista else []
        itens = self.lista_model.get_itens(lista["id"]) if lista else []
        return (lista, sublistas, itens, slug_lista)

    def call_template_listas(self, lista, sublistas, itens):
        nome_lista = lista["nome"]
        title = u"Listas Públicas: %s" % nome_lista
        slug_atual, slugs_pais = self.__get_slugs__(lista["slug"])
        options = {"title": title, "lista": lista, "itens": itens, "sublistas": sublistas, "slug_atual": slug_atual, "slugs_pais": slugs_pais,
                    "opcao_deleta_todos_os_itens": self.opcao_deleta_todos_os_itens,
                    "opcao_deleta_a_lista": self.opcao_deleta_a_lista,
                    "opcao_deleta_um_item": self.opcao_deleta_um_item,
                    "opcao_edita_a_lista": self.opcao_edita_a_lista,
                    "opcao_edita_um_item": self.opcao_edita_um_item
                    }
        result = render_template("listas.html", options)
        self.write(result)

    def get(self, slug_lista):
        """ Quando a página slug_lista carregar """

        if slug_lista == "":
            raise tornado.web.HTTPError(404) # Listas não podem vir com o nome vazio
        else: 
            lista, sublistas, itens, slug_lista = self.get_lista_info(slug_lista)
            
            if lista:
                #Chama o templa listas.html que mostra o nome da lista, suas sublistas e os seus itens
                self.call_template_listas(lista, sublistas, itens)
            else:
                #Adiciona a nova lista
                self.lista_model.cria_nova_lista(slug_lista)
                
                #Chama o templa listas.html que mostra o nome da lista, suas sublistas e os seus itens
                lista, sublistas, itens, slug_lista = self.get_lista_info(slug_lista)
                self.call_template_listas(lista, sublistas, itens)

    def post(self, slug_lista):
        """ Quando a página slug_lista pedir para inserir novos itens """

        lista, sublistas, itens, slug_lista = self.get_lista_info(slug_lista)

        if lista:
            # Adiciona novos itens a lista
            lista_id = lista["id"]
            novos_itens_nomes = self.get_argument("novos_itens")
            novos_itens_nomes = novos_itens_nomes.split("\n")
            atuais_itens_nomes = [item["nome"] for item in itens]
            self.lista_model.add_itens(atuais_itens_nomes, novos_itens_nomes, lista_id)
            self.redirect('/' + slug_lista) # Vai pro GET
        else:
            raise tornado.web.HTTPError(404) # Não se adiciona itens numa lista inexistente


    def put(self, slug_lista):
        """ Quando a página slug_lista pedir para editar listas/itens """

        if slug_lista.endswith(self.opcao_edita_a_lista):
            slug_lista = slug_lista.replace(self.opcao_edita_a_lista, "")
            lista_id = self.__get_lista_id__(slug_lista)
            novo_valor = self.get_argument("novo_valor")
            self.lista_model.altera_nome_lista(lista_id, novo_valor)
        else:
            m_obj = re.search(self.opcao_edita_um_item_regex, slug_lista)
            if m_obj:
                item_id = int(m_obj.group(1))
                novo_valor = self.get_argument("novo_valor")
                self.lista_model.altera_item(item_id, novo_valor)
            else:
                raise tornado.web.HTTPError(404)

    def delete(self, slug_lista):
        """ Quando a página slug_lista pedir para deletar listas/itens """
        
        if slug_lista.endswith(self.opcao_deleta_todos_os_itens):
            slug_lista = slug_lista.replace(self.opcao_deleta_todos_os_itens, "")
            lista_id = self.__get_lista_id__(slug_lista)
            self.lista_model.deleta_todos_itens_da_lista(lista_id)
        elif slug_lista.endswith(self.opcao_deleta_a_lista):
            slug_lista = slug_lista.replace(self.opcao_deleta_a_lista, "")
            lista_id = self.__get_lista_id__(slug_lista)
            self.lista_model.deleta_lista(lista_id)
        else:
            m_obj = re.search(self.opcao_deleta_um_item_regex, slug_lista)
            if m_obj:
                item_id = int(m_obj.group(1))
                self.lista_model.deleta_item(item_id)
            else:
                raise tornado.web.HTTPError(404)


class HomeHandler(tornado.web.RequestHandler):
	""" Chama home.html """
	def get(self):
		title = u"Listas Públicas - Home"
		options = {"title": title}
		result = render_template("home.html", options)
		self.write(result)

        
STATIC_PATH = os.path.abspath(os.path.dirname(__file__))
routes_listas_publicas = [
    (r"/css/(.*)", StaticFileHandler, {"path": STATIC_PATH + "/css/"}),
    (r"/js/(.*)", StaticFileHandler, {"path": STATIC_PATH + "/js/"}),
    (r"/img/(.*)", StaticFileHandler, {"path": STATIC_PATH + "/img/"}),
    (r"/(.+)", ListasHandler),
    (r"/?", HomeHandler)
]

application = tornado.web.Application(routes_listas_publicas)

if __name__ == "__main__":
    porta = 8888
    application.listen(porta)
    print "Aplicacao na porta %d" % porta
    tornado.ioloop.IOLoop.instance().start()
    
