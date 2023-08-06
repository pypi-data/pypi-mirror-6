.. _Python: http://www.python.org/
.. _funcy: http://pypi.python.org/pypi/funcy
.. _py: http://pypi.python.org/pypi/py
.. _Griffith University: http://www.griffith.edu.au/
.. _TerraNova: https://terranova.org.au/
.. _Climate Change and Adaptation Visualization: http://ccav.terranova.org.au/
.. _Project Website: http://bitbucket.org/prologic/streamio
.. _PyPi Page: http://pypi.python.org/pypi/streamio
.. _Read the Docs: http://streamio.readthedocs.org/en/latest/
.. _Downloads Page: https://bitbucket.org/prologic/streamio/downloads
.. _API: http://streamio.readthedocs.org/en/latest/api/


streamio is a simple library of functions designed to read, write and sort large files using iterators so that the operations will successfully complete
on systems with limited RAM. This library has been used extensively at `Griffith University`_ whilst developing the `TerraNova`_
`Climate Change and Adaptation Visualization`_ tool(s) and processing large volumes of data. streamio is written in `Python`_ and has extensive documentation
and unit tests with 100% coverage.

See the `API`_ for a list of the available functions.

- Visit the `Project Website`_
- `Read the Docs`_
- Download it from the `Downloads Page`_

.. image:: https://pypip.in/v/streamio/badge.png
   :target: https://crate.io/packages/streamio/
   :alt: Latest PyPI version

.. image:: https://pypip.in/d/streamio/badge.png
   :target: https://crate.io/packages/streamio/
   :alt: Number of PyPI downloads

.. image:: https://jenkins.shiningpanda-ci.com/prologic/job/streamio/badge/icon
   :target: https://jenkins.shiningpanda-ci.com/prologic/job/streamio/
   :alt: Build Status

.. image:: https://requires.io/bitbucket/prologic/streamio/requirements.png?branch=default
   :target: https://requires.io/bitbucket/prologic/streamio/requirements/?branch=default
   :alt: Requirements Status


Examples
--------


Read a large text file iteratively:

.. code-block:: python
    
    from streamio import stream
    f = stream("large_file.txt")
    

Read a large CSV file iteratively:

.. code-block:: python
    
    from streamio import jsonstream
    f = stream("large_file.json")
    

Merge-sort a large JSON file with the key ``itemgetter("value")``:

.. code-block:: python
    
    from operator import itemgetter
    from streamio import mergesort
    f = mergesort("large_file.json", key=itemgetter("value"))
    

Requirements
------------

- `funcy`_
- `py`_

streamio also comes with documentation and a full comprehensive unit test suite which require the following:

To build the docs:

- `sphinx <https://pypi.python.org/pypi/Sphinx>`_

To run the unit tests:

- `pytest <https://pypi.python.org/pypi/pytest>`_


Installation
------------

The simplest and recommended way to install streamio is with pip.
You may install the latest stable release from PyPI with pip::

    > pip install streamio

If you do not have pip, you may use easy_install::

    > easy_install streamio

Alternatively, you may download the source package from the
`PyPI Page`_ or the `Downloads page`_ on the `Project Website`_;
extract it and install using::

    > python setup.py install

You can also install the
`latest-development version <https://bitbucket.org/prologic/streamio/get/tip.tar.gz#egg=streamio-dev>`_ by using ``pip`` or ``easy_install``::
    
    > pip install streamio==dev

or::
    
    > easy_install streamio==dev


For further information see the `streamio documentation <http://streamio.readthedocs.org/>`_.


Supported Platforms
-------------------

- Linux, FreeBSD, Mac OS X
- Python 2.7
- PyPy 2.2

**Windows**: We acknowledge that Windows exists and make reasonable efforts
             to maintain compatibility. Unfortunately we cannot guarantee
             support at this time.
