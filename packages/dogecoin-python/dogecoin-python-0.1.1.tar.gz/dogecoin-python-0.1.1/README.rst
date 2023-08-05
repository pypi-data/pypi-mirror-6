dogecoin-python is a fork of bitcoin-python : https://github.com/laanwj/bitcoin-python

It is a set of Python libraries that allows easy access to the
dogecoin peer-to-peer cryptocurrency client API.


Documentation
===========================

The orignal documentation for bitcoin-python can be found here :

http://laanwj.github.com/bitcoin-python/doc/

The dogecoin-pyton documentation can be found in the source archive. It is built using Sphinx.

Installation instructions
===========================

dogecoin-python uses setuptools for the install script. There are no dependencies apart from Python itself.

::

  $ python setup.py build
  $ python setup.py install


TODO
======
These things still have to be added:

- SSL support (including certificate verification) for managing remote dogecoin daemons.

