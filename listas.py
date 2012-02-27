# -- coding: UTF-8 --

import string
import os
import tornado
from tornado.web import Application, RequestHandler, HTTPError, StaticFileHandler
from template import render_template

class ListasHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.itens = []

    def get_title(self, nome_lista):
        nome_lista = " ".join( nome_lista.split("-") ) # Exemplo: aniversario-guilherme-2012 vira aniversario guilherme 2012
        nome_lista = string.capwords(nome_lista) # Exemplo: aniversario guilherme 2012 vira Aniversario Guilherme 2012
        if nome_lista == "":
            raise tornado.web.HTTPError(404) # Listas não podem vir com o nome vazio
        return "Lista de " + nome_lista

    def get(self, nome_lista):
        itens = ["item1", "item2", "item3"]
        title = self.get_title(nome_lista)
        options = {"nome_lista": nome_lista, "itens": itens, "title": title}

        result = render_template("listas.html", options)
        self.write(result)

    def post(self, nome_lista):
        itens = self.get_argument("itens")
        itens = itens.split("\n")
        title = self.get_title(nome_lista)
        options = {"nome_lista": nome_lista, "itens": itens, "title": title}

        result = render_template("listas.html", options)
        self.write(result)
        

STATIC_PATH = os.path.abspath(os.path.dirname(__file__))
routes_listas_publicas = [
    (r"/listas-publicas/css/(.*)", StaticFileHandler, {"path": STATIC_PATH + "/css/"}),
    (r"/listas-publicas/js/(.*)", StaticFileHandler, {"path": STATIC_PATH + "/js/"}),
    (r"/listas-publicas/img/(.*)", StaticFileHandler, {"path": STATIC_PATH + "/img/"}),
    (r"/listas-publicas/(.*)", ListasHandler)
]
