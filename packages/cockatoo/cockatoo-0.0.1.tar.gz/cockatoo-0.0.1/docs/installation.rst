Installing
======================
.. highlight:: bash

**cockatoo** is in the `Python Package Index <http://pypi.python.org/pypi/cockatoo/>`_.

Requirements
-------------------

cockatoo requires `RDKit <http://rdkit.org/>`_. Debian/Ubuntu users can install RDKit via apt-get::

  $ sudo apt-get install python-rdkit librdkit1 rdkit-data

For more information see `Building RDKit from source`_.

Installing with pip
-------------------

To install cockatoo via `pip <http://pypi.python.org/pypi/pip>`_::

  $ pip install cockatoo

Installing from source
-----------------------

To install cockatoo from source checkout the latest code from `github <https://github.com/ubccr/cockatoo>`_::

  $ git clone git://github.com/ubccr/cockatoo.git cockatoo
  $ cd cockatoo
  $ python setup.py install

Building RDKit from source
--------------------------

To build RDKit from source, first install the required devel packages for your distro::

  $ sudo apt-get install libboost-dev cmake python-dev

Install numpy::

  $ sudo apt-get python-numpy
  --or--
  $ sudo pip install numpy

Checkout latest source from github::

  $ git clone https://github.com/rdkit/rdkit.git rdkit
  $ cd rdkit
  $ export RDBASE=`pwd`
  $ export PYTHONPATH=$RDBASE:$PYTHONPATH
  $ export LD_LIBRARY_PATH=$RDBASE/lib:$LD_LIBRARY_PATH
  $ mkdir build
  $ cd build
  $ cmake ..
  $ make
  $ make install
  $ python setup.py install --user

For more information on building RDKit from source see the `manual <https://github.com/rdkit/rdkit/raw/master/Docs/Book/RDKit.pdf>`_.
