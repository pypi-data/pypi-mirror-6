=============================
Opps - OPen Publishing System
=============================

An *Open Source Content Management* for the **magazine** websites and **high-traffic**, using the Django Framework.

.. image:: https://travis-ci.org/opps/opps.png?branch=master
    :target: https://travis-ci.org/opps/opps
    :alt: Build Status - Travis CI

.. image:: https://pypip.in/v/opps/badge.png
    :target: https://crate.io/packages/opps/
    :alt: Pypi version

.. image:: https://pypip.in/d/opps/badge.png
    :target: https://crate.io/packages/opps/
    :alt: Pypi downloads


.. contents:: Topics


.. include:: ../../CONTRIBUTING.rst


Contacts
========

The place to create issues is `opps's github issues <https://github.com/opps/opps/issues>`_. The more information you send about an issue, the greater the chance it will get fixed fast.

If you are not sure about something, have a doubt or feedback, or just want to ask for a feature, feel free to join `our mailing list <http://groups.google.com/group/opps-developers>`_, or, if you're on FreeNode (IRC), you can join the chat `#opps <http://webchat.freenode.net/?channels=opps>`_.


Run example
===========

Download and install Opps

.. code-block:: bash

    git clone https://github.com/opps/opps.git
    cd opps
    python setup.py develop

Now you can start a new Opps project

.. code-block:: bash

    opps-admin.py startproject PROJECT_NAME
    cd PROJECT_NAME
    python manage.py syncdb --noinput
    python manage.py migrate
    python manage.py collectstatic --noinput
    python manage.py runserver


Tests
=====

To run the test you must have an Redis instance running locally on the 6379 port (default one). Then, just type the following

.. code-block:: bash

    make test
    
To run tests in multiple python versions, first install tox and then run the tox command:

.. code-block:: bash

    pip install tox
    tox


VirtualBox
----------

.. code-block:: bash

    vagrant box add opps http://mirror.oppsproject.org/opps.box
    vagrant up
    vagrant ssh
    workon opps
    cd /home/vagrant/opps/example/
    python manage.py runserver 0.0.0.0:8000


Sponsor
=======

* `YACOWS <http://yacows.com.br/>`_
* `Digital Ocean <http://digitalocean.com/>`_


License
=======

*opps* is licensed under the `MIT License <http://opensource.org/licenses/MIT>`_

Copyright (c) 2013 Opps Project. and other contributors

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


.. image:: https://d2weczhvl823v0.cloudfront.net/opps/opps/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free
