# Makefile for python module.

SETUP = python setup.py

FORMATS = sdist --formats=gztar,zip bdist_egg

.DEFAULT:;	@ $(SETUP) $@
.PHONY:		build dist

all:		build
dist:		sdist
tags:;		find . -name '*.py' | xargs etags

release:;	@ $(SETUP) $(FORMATS) upload

build:;		@ $(SETUP) $@
help:;		@ $(SETUP) --help
commands:;	@ $(SETUP) --help-commands

clean:;		rm -rf MANIFEST PKG-INFO build dist *.egg-info
