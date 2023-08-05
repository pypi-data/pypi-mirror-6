=========================
SitRep - Situation Report
=========================

**SitRep** is a console-based snapshot of Linux system resources written in Python.

.. image:: https://raw.github.com/vonbrownie/sitrep/master/docs/images/sitrep-screenshot.png

Requirements
============

* ``python2`` (tested with version 2.7)
* ``netifaces``
* ``psutil``
* ``requests``
* ``setuptools``

Installation
============

PyPI
----

SitRep is on `PyPI`_. To install, simply use `pip`_:

.. code-block:: console

    $ pip install sitrep

To upgrade SitRep to the latest version:

.. code-block:: console

    $ pip install --upgrade sitrep

Source
------

To install SitRep from source:

.. code-block:: console

    $ wget -c https://github.com/vonbrownie/sitrep/releases/download/v0.9.1/sitrep-0.9.2.tar.gz
    $ tar -xvzf sitrep-0.9.2.tar.gz
    $ cd sitrep-0.9.2
    $ sudo python setup.py install --record rinstall.txt

Adding the ``--record rinstall.txt`` option generates an install log named
``rinstall.txt`` that can later be used to track down and uninstall files. See
``python setup.py install --help`` for more options.

*Note:* Python headers are required to install psutil. For example, on 
Debian you need to install first the ``python-dev`` package.

Usage
=====

Just run:

.. code-block:: console

    $ sitrep

Author
======

| Daniel Wayne Armstrong (aka) VonBrownie
| http://www.circuidipity.com
| https://twitter.com/circuidipity
| daniel@circuidipity.com

License
=======

GPLv2. See ``LICENSE`` for more details.

.. _PyPI: https://pypi.python.org/pypi
.. _pip: http://www.pip-installer.org/
