# -*- makefile -*-
#
# Copyright (c) 2008,2009 Etienne Robillard <robillard.etienne@gmail.com>
# All rights reserved.

SHELL:= /bin/sh
CURDIR:= .
TOPDIR:=$(CURDIR)

#DJANGO_HOME?= /usr/local/share/django/django-r13404
ENV?= /usr/bin/env
PYTHON?= /usr/local/bin/python
PYTHONFLAGS?= # -W ignore
PYTHONPATH?= $DJANGO_HOME
RM?= /bin/rm 
FIND?= find
TRUE?= true
MAKE?= gmake

ifdef WITH_PYTHON
 PYTHON=$(WITH_PYTHON)
endif

#List of options to override SimpleTestRunner invocation
OPTIONS?=

all: runtest
clean:
	$(FIND) $(CURDIR) -type f -name "*.py[co]" -exec $(RM) -rf '{}' ';' || $(TRUE)
runtest: clean
	$(PYTHON) $(PYTHONFLAGS) $(CURDIR)/run.py ${OPTIONS} || $(TRUE)

PHONY: all clean runtest
