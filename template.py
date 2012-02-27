#-*- coding:utf-8 -*-

import os
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIRS = os.path.abspath(os.path.dirname(__file__))
environment_listas = Environment(loader=FileSystemLoader(TEMPLATE_DIRS))

def render_template(template_path, context={}):
    template = environment_listas.get_template(template_path)
    return template.render(**context)