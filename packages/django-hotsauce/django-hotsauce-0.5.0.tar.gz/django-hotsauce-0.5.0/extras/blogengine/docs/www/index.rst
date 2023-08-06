BlogEngine 1.0
==============

* `About`_
* `Current Features`_
* `Installation`_
* `Support`_
* `License`_


About
-----

BlogEngine is a lightweight Blogging library written
in Python. 

Current Features
----------------

* Easy Non-SQL schema migration and maintenance using the Schevo ORM.
* Compatible with Django and WSGI (AuthKit, Paste, Pylons, etc).
* Tags 
* Categories
* Comments and comments previews.
* Comments moderation.
* Users authentication and custom permission system (as provided by AuthKit)
* Integration with JQuery and `JQuery UI <http://jqueryui.com/>`_. 

Installation
------------

To install the latest version as root in ``/usr/local/``, type ::

 $ hg clone http://joelia.gthc.org/BlogEngine/trunk blogengine-trunk
 $ cd blogengine-trunk
 $ hg up -r tip
 $ sudo python setup.py install --prefix=/usr/local

Support
-------

Send bug reports to erob@gthcfoundation.org.

License
-------

Copyright (C) 2009-2010 Etienne Robillard erob@gthcfoundation.org

All rights reserved.

Redistribution and use in source and binary forms, with 
or without modification(s), are permitted provided that 
the following conditions are met:

1. Redistributions in source and binary forms must retain the above 
   copyright notice, this list of conditions and the following disclaimer.

2. In addition, neither the names of "BlogEngine", "notmm", nor "Etienne Robillard",  
   may be used to endorse, promote, distribute, or sell products derived
   from this software without specific and prior written consent.

THIS SOFTWARE IS PROVIDED BY ETIENNE ROBILLARD AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ETIENNE ROBILLARD OR CONTRIBUTORS 
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, 
OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
THE POSSIBILITY OF SUCH DAMAGE.
 
