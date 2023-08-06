# Makefile for PyDitz.

SETUP = python setup.py

.DEFAULT:;	@ $(SETUP) $@
.PHONY:		build doc

all:		build

build doc:;	@ $(SETUP) $@

tags:;		find . -name '*.py' | xargs etags

clean:;		rm -rf $(MANIFEST) build dist *.egg-info
