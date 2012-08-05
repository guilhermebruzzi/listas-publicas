SHELL := /bin/bash

root_dir		= $(realpath .)


help:
	@echo 'USAGE: make <target>'
	@echo '-----------------'
	@echo 'Available targets'
	@echo '-----------------'
	@echo '    install..........................instala as dependências da aplicação'
	@echo '    run............................start da aplicação'

install:
	@pip install -r requirements.txt

clean:
	@find . -type f -name "*.pyc" -exec rm -rf {} \;

run: clean
	@foreman start

simple_run: clean
	@python ${root_dir}/listas.py

