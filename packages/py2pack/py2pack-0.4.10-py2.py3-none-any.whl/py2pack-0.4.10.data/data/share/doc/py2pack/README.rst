Py2pack: Generate distribution packages from PyPI
=================================================

.. image:: https://travis-ci.org/saschpe/py2pack.png?branch=master
        :target: https://travis-ci.org/saschpe/py2pack

.. image:: https://pypip.in/d/py2pack/badge.png
        :target: https://pypi.python.org/pypi/py2pack

.. image:: https://pypip.in/v/py2pack/badge.png
        :target: https://pypi.python.org/pypi/py2pack

This script allows to generate RPM spec or DEB dsc files from Python modules.
It allows to list Python modules or search for them on the Python Package Index
(PyPI). Conveniently, it can fetch tarballs and changelogs making it an
universal tool to package Python modules.


Installation
------------

To install py2pack from the `Python Package Index`_, simply:

.. code-block:: bash

    $ pip install py2pack

Or, if you absolutely must:

.. code-block:: bash

    $ easy_install py2pack

But, you really shouldn't do that. Lastly, you can check your distro of choice
if they provide packages. For openSUSE, you can find packages in the `Open
Build Service`_ for all releases. If you happen to use openSUSE:Factory (the
rolling release / development version), simply:

.. code-block:: bash

    $ sudo zypper install python-py2pack


Usage
-----

Lets suppose you want to package zope.interface_ and you don't know how it is named
exactly. First of all, you can search for it and download the source tarball if
you found the correct module:

.. code-block:: bash

    $ py2pack search zope.interface
    searching for module zope.interface...
    found zope.interface-3.6.1
    $ py2pack fetch zope.interface
    downloading package zope.interface-3.6.1...
    from http://pypi.python.org/packages/source/z/zope.interface/zope.interface-3.6.1.tar.gz


As a next step you may want to generate a package recipe for your distribution.
For RPM_-based distributions (let's use openSUSE_ as an example), you want to
generate a spec file (named 'python-zope.interface.spec'):

.. code-block:: bash 

    $ py2pack generate zope.interface -t opensuse.spec -f python-zope.interface.spec

The source tarball and the package recipe is all you need to generate the RPM_
(or DEB_) file. This final step may depend on which distribution you use. Again,
for openSUSE_ (and by using the `Open Build Service`_), the complete recipe is:

.. code-block:: bash 

    $ osc mkpac python-zope.interface
    $ cd python-zope.interface
    $ py2pack fetch zope.interface
    $ py2pack generate zope.interface -f python-zope.interface.spec
    $ osc build
    ...

Depending on the module, you may have to adapt the resulting spec file slightly.
To get further help about py2pack usage, issue the following command:

.. code-block:: bash 

    $ py2pack help


Hacking and contributing
------------------------

You can test py2pack from your git checkout by executing the py2pack module:

.. code-block:: bash

    $ python -m py2pack

Fork `the repository`_ on Github to start making your changes to the **master**
branch (or branch off of it). Don't forget to write a test for fixed issues or
implemented features whenever appropriate. You can invoke the testsuite from
the repository root directory via:

.. code-block:: bash

    $ python setup.py test

Or by running `nose`_ directly:

.. code-block:: bash

    $ nosetests

Both assume you have the test dependencies installed (available on PYTHONPATH)
on your system. If that doesn't work for you, you can create a `virtual
environment`_ instead:

.. code-block:: bash

    $ virtualenv .venv
    $ source .venv/bin/activate
    (.venv)$ pip install -r test-requirements.txt
    (.venv)$ nosetests

Lastly, if using virtualenv is too tedious or you want to test different
configurations (py27, py33, pep8), you can also use `tox`_:

.. code-block:: bash

    $ tox


 :copyright: (c) 2013 Sascha Peilicke.
 :license: GPLv2, see LICENSE for more details.


.. _argparse: http://pypi.python.org/pypi/argparse
.. _Jinja2: http://pypi.python.org/pypi/Jinja2 
.. _zope.interface: http://pypi.python.org/pypi/zope.interface/
.. _openSUSE: http://www.opensuse.org/en/
.. _RPM: http://en.wikipedia.org/wiki/RPM_Package_Manager
.. _DEB: http://en.wikipedia.org/wiki/Deb_(file_format)
.. _`Python Package Index`: https://pypi.python.org/pypi/rapport
.. _`Open Build Service`: https://build.opensuse.org/package/show?package=rapport&project=devel:languages:python
.. _`the repository`: https://github.com/saschpe/py2pack
.. _`nose`: https://nose.readthedocs.org
.. _`virtual environment`: http://www.virtualenv.org
.. _`tox`: http://testrun.org/tox


.. image:: https://d2weczhvl823v0.cloudfront.net/saschpe/py2pack/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

