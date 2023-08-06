# -*- makefile -*-
# Top-level Makefile for building the notmm toolkit.
# Copyright (C) 2007-2011 Etienne Robillard <erob@gthcfoundation.org> 
# All rights reserved.

SHELL:= /bin/sh
TOPDIR= .
CURDIR= $(TOPDIR)
PREFIX= /usr/local
OBJDIR= $(TOPDIR)/build
LIBDIR= $(TOPDIR)/lib
DOCDIR= $(TOPDIR)/docs
DISTDIR= $(TOPDIR)/dist
SRCDIR= $(LIBDIR)
#DESTDIR= $(PREFIX)
#LANG=C;

# Debian stuff; Keep this if you're a maintainer and want to
# build a deb archive.
# DEBIANROOT= $(TOPDIR)/debian
#FAKEROOT= $(DEBIANROOT)/$(PACKAGE_NAME)

### Module Options ###
# Documentation building and install
ENABLE_DOCS?="YES" # Set to "NO" to disable building docs

WITH_DOXYGEN?="YES"
WITH_SPHINX?="YES"

#HTML documentation will be installed into this dir
DOCPREFIX?=/usr/local/share/doc/notmm

#Sphinx will install HTML files into this dir
DOCROOT?=$(TOPDIR)/docs/build/html
ifndef WITHOUT_DOXYGEN
    DOXYGEN_DESTDIR="${DOCPREFIX}/doxygen"
    DOXYGEN_SRCDIR="${TOPDIR}/doxygen" # XXX: should be ${DOCDIR}/build/doxygen
endif

# Define this to build custom WSGI controllers with
# Cython. (experimental)
WITH_CYTHON?="YES"

WITH_OPTIMIZED_CFLAGS?="YES"
BASE_CFLAGS?=-2

ifdef WITH_OPTIMIZED_CFLAGS
    CYTHON_CFLAGS?=${BASE_CFLAGS} --no-docstrings
else
    CYTHON_CFLAGS?=
endif    

# Define this to build HTML pages for C modules
# WITH_CYTHON_HTMLDOC?="YES"

# Define this to build the schevo.so module
WITH_SCHEVO?="YES"

# Define this if you want to build the elixir.so module (experimental)
WITH_ELIXIR?="YES"

# Define this if you want to build the auth.so module (experimental)
WITH_LIBAUTHKIT?="YES"

#Allow building notmm with LLVM/Clang in the future 
#WITH_LLVM?="YES"
#WITH_CLANG?="YES"

# Enable MoinMoin support 
WITH_MOINMOIN?="YES"

# Enable BlogEngine support
WITH_BLOGENGINE?="YES"

# Enable experimental I18N support
WITH_I18N?="YES"


#No support yet for Python3000 aka GoogleSwallow
ifdef WITH_CYTHON
    CYTHON_MODULES:=\
	lib/notmm/controllers/wsgi.pyx \
	lib/notmm/controllers/session.pyx 
ifdef WITH_SCHEVO        
    CYTHON_MODULES+=lib/notmm/controllers/schevo.pyx 
endif
ifdef WITH_LIBAUTHKIT
    CYTHON_MODULES+=lib/notmm/controllers/auth.pyx 
endif        
ifdef WITH_ELIXIR # this implies WITH_SQLALCHEMY="YES"
    CYTHON_MODULES+=lib/notmm/controllers/elixir.pyx
endif
ifdef WITH_I18N
    CYTHON_MODULES+=lib/notmm/controllers/i18n.pyx
endif    

ifdef WITH_CYTHON_HTMLDOC
    CFLAGS+=-a   
endif

ifdef WITH_LLVM
    CC=llvm-gcc
endif    


CFLAGS:= $(CYTHON_CFLAGS) $(BASE_CFLAGS)
MODULES:= $(CYTHON_MODULES)
else
MODULES:= $(error "can\'t build without Cython support!")
endif

CYTHON?= cython
ENV?= /usr/bin/env
ECHO?= /bin/echo
DOXYGEN?= /usr/local/bin/doxygen
FIND?= /usr/bin/find
GREP?= grep -E
HG?= hg
INSTALL?= install
MAKE?= make
MD5SUM?= md5sum
MKDIR?= mkdir
PYTHON?= /usr/local/bin/python
PYLINT?= pylint
PYLINTFLAGS?= --init-import=y
RM?= /bin/rm
SUDO?= sudo
TRUE?= true
WHICH?= which
XARGS?= xargs

distfiles=$(ls "$DISTDIR/*.*")

all: build 

build: clean
	env CC=$(CC) $(PYTHON) setup.py build
clean:
#-fakeroot $(MAKE) -f $(DEBIANROOT)/rules clean
	$(RM) -rf $(OBJDIR) MANIFEST $(DOXYGEN_BUILDDIR) *-stamp*
	$(RM) -rf $(DOCDIR)/build
changelog:
	$(HG) log > CHANGES
check:
	$(ECHO) 'Sorry, "make check" is not implemented yet.'
depend: clean
	$(CYTHON) $(CFLAGS) $(MODULES) || $(TRUE)
develop: depend
	$(PYTHON) setup.py develop
distclean: clean
	$(FIND) $(TOPDIR) -type f -name "*.py[co]" -exec $(RM) -f '{}' ';' || $(TRUE)
	$(FIND) $(TOPDIR) -type f -name "*.sw[po]" -exec $(RM) -f '{}' ';' || $(TRUE)
	$(FIND) $(TOPDIR) -type f -name "1" -exec $(RM) -f '{}' ';' || $(TRUE)
doxygen: distclean
	$(DOXYGEN) $(TOPDIR)/docs/Doxyfile
help:
	$(PYTHON) setup.py --help
install: build
	$(PYTHON) setup.py install --prefix=$(PREFIX) $(COMPILE)
installdocs: builddocs
##@echo "===> Creating new documentation set..."
##$(MKDIR) ${DOCPREFIX} 
ifdef WITH_SPHINX
	@echo "===> Installing Sphinx-generated HTML documentation..."
	for f in `dir $(DOCROOT)`; do \
	 $(INSTALL) -v -C "$(DOCROOT)/$$f" "${DOCPREFIX}/$$f" || $(TRUE); \
	done; 
	@echo "===> API documentation installed to $(DOCPREFIX)."
endif
builddocs: html
ifndef WITHOUT_DOXYGEN
	@echo "===> Building API documentation (Doxygen)"
	$(MAKE) doxygen && DOCBUILDSTATE=1
endif
#By default HTML documentation should always be rebuilt
installdocs: builddocs
ifeq (DOCBUILDSTATE, 1)
	for f in `dir $(DOXYGEN_SRCDIR)`; do \
	 $(INSTALL) -v -C "$(DOXYGEN_SRCDIR)/$$f" "$(DOXYGEN_DESTDIR)/$$f" || $(TRUE); \
	done;
endif
html:
	$(MAKE) -C ${DOCDIR} -f Makefile html
###administrative commands, for maintainers or
###core developers only (ie: distro package builders) 
manifest:
	$(HG) -q manifest > MANIFEST
md5:
	@for f in "${distfiles}"; do \
		$(MD5SUM) $$f >> CHECKSUMS.txt || $(TRUE);\
	@done;  	
bdist_egg:
	$(PYTHON) setup.py bdist --formats=egg
bdist_zip:
	$(PYTHON) setup.py bdist --formats=zip
bdist_rpm:
	$(PYTHON) setup.py bdist --formats=rpm
bdist_deb: sdist
	dpkg-buildpackage -i -I -rfakeroot || $(TRUE)
sdist: distclean manifest changelog
	$(PYTHON) setup.py sdist $(COMPILE)
test: check
	$(MAKE) -C tests -f Makefile 
lint:
	$(PYLINT) $(PYLINTFLAGS) $(SRCDIR)/notmm 
update:
	$(HG) up -r tip
version:
	$(PYTHON) setup.py --version

