=======
Install
=======

:Last modified: 2010-09-20
:Author: Etienne Robillard <erob@gthcfoundation.org>
:Version: 0.4.2

The notmm-python bindings can be installed normally using the Setuptools
extension. If ``setuptools`` is not installed, you can run ``ez_setup.py`` to 
download and install the `current release (0.6c11) <http://pypi.python.org/pypi/setuptools/>`_.

You can also verify if ``setuptools`` is installed and working properly 
using the following one-liner: ::

    % python -c 'import setuptools'

To install non-interactively third-party python bindings required to properly
build notmm, use the ``bootstrap`` script and the name of the Python
interpreter to use for the whole install process. 

For example, to develop a WSGI application with Python 2.7, one could do: ::

    % ./bootstrap python2.7

To complete the install using ``llvm-gcc`` as the host compiler: ::

    % export CC=llvm-gcc
    % export LD=llvm-ld
    % make depend
    % sudo make install

(Note that you should use GNU make and not /usr/bin/make if you're
using a *BSD system. On Linux, gmake should be aliased as /usr/bin/make.)

The old way: ::

    % python setup.py build 
    % python setup.py install --prefix=/usr/local

To develop locally, you can use the "develop" command provided by
setuptools to install a symlink to the source directory: ::

    % sudo make develop

To build the documentation, Sphinx and Doxygen are needed. Sphinx
is used to build the standard documentation and Doxygen for the API
documentation: ::

    % sudo make doxygen          # generate the API docs
    % make -f docs/Makefile html # generate the HTML docs (work-in-progress)

