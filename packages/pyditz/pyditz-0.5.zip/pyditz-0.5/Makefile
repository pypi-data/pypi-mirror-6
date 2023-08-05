# Makefile for pyditz.

SETUP = python setup.py
MANIFEST = MANIFEST.in
EXCLUDE = .hgignore .hgtags $(MANIFEST)

.DEFAULT:;	@ $(SETUP) $@
.PHONY:		build

all:		build

build:;		@ $(SETUP) $@

sdist:;		@ echo "exclude $(EXCLUDE)" > $(MANIFEST)
		@ $(SETUP) $@ --formats=gztar
		@ rm -f $(MANIFEST)

bdist:;		@ $(SETUP) $@ --formats=wininst

release:;	@ echo "exclude $(EXCLUDE)" > $(MANIFEST)
		@ $(SETUP) sdist --formats=gztar,zip bdist_egg upload
		@ rm -f $(MANIFEST)

tags:;		find . -name '*.py' | xargs etags

clean:;		rm -rf $(MANIFEST) build dist *.egg-info
