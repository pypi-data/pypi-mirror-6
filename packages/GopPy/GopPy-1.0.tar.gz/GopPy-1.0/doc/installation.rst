Installation
============

This section lists the dependencies of GopPy and provides installation
instructions. The installation is quite easy as GopPy is a pure Python package.

Requirements
------------

GopPy supports Python 2.6, 2.7, 3.2, and 3.3. Later versions will be likely to
work, too. In addition, the following package will be needed:

* `NumPy <http://www.numpy.org/>`_

If you want to run the unit tests, you will additionally need:

* `nose <https://nose.readthedocs.org/en/latest/>`_
* `PyHamcrest <https://pypi.python.org/pypi/PyHamcrest>`_

If you want to build the documentation, you will need:

* `Sphinx <http://sphinx-doc.org/>`_
* `numpydoc <https://pypi.python.org/pypi/numpydoc>`_
* `matplotlib <http://matplotlib.org/>`_

Install with pip
----------------

You can install GopPy easily with pip::

    pip install goppy

Install from Source
-------------------

It is also possible to `download the latest source distribution from PyPI
<https://pypi.python.org/pypi/GopPy/>`_, extract it and run::

    python setup.py install
