# Makefile for unit tests.

NOSE = nosetests $(ARGS)

COVER = --with-coverage --cover-package ditz --cover-erase	\
--cover-branches --cover-html

PROF = --with-profile --profile-sort=time

.PHONY: cover

all: test

test:; $(NOSE) $(TEST)

diff:; diff -r example example-copy

cover:; $(NOSE) $(COVER) $(TEST)

prof:; $(NOSE) $(PROF) $(TEST)

clean:; rm -rf .coverage cover database example-* *.ini
