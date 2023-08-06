==================================================================
Evaluation methods for verification systems under spoofing attacks
==================================================================

This package provides methods for evaluation of biometric verification systems under spoofing attacks. The evaluation is based on the Expected Performance and Spoofability Curve (EPSC). Using this package, you can compute thresholds based on EPSC, compute various error rates and plot various curves related to EPSC. 

Besides providing methods for plotting EPSC within your own scripts, this package brings several scripts that you can use to evaluate your own verification system from several perspectives. For example, you can: 
  - evaluate the threshold of a classification system on the development set
  - apply the threshold on an evaluation or any other set to compute different error rates
  - plot score distributions
  - plot different performance curves (DET, EPC and EPSC)

Furthermore, you can generate hypothetical data and use them to exemplify the above mentioned functionalities.

Finally, several scripts enable you to evaluate 4 state-of-the-art face verification systems, before and after they are fused with an anti-spoofing system for better robustness to spoofing. The scripts enable you to plot the relevant curves of the systems together and compare them.

Please refer to the documentation for a full Reference Manual and User Guide.

Installation
------------

There are 2 options you can follow to get this package installed and
operational on your computer: you can use automatic installers like `pip
<http://pypi.python.org/pypi/pip/>`_ (or `easy_install
<http://pypi.python.org/pypi/setuptools>`_) or manually download, unpack and
use `zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_ to create a
virtual work environment just for this package.

Using an automatic installer
============================

Using ``pip`` is the easiest (shell commands are marked with a ``$`` signal)::

  $ pip install antispoofing.utils

You can also do the same with ``easy_install``::

  $ easy_install antispoofing.utils

This will download and install this package plus any other required
dependencies. It will also verify if the version of Bob you have installed
is compatible.

This scheme works well with virtual environments by `virtualenv
<http://pypi.python.org/pypi/virtualenv>`_ or if you have root access to your
machine. Otherwise, we recommend you use the next option.

Using ``zc.buildout``
=====================

Download the latest version of this package from `PyPI
<http://pypi.python.org/pypi/antispoofing.utils>`_ and unpack it in your
working area. The installation of the toolkit itself uses `buildout
<http://www.buildout.org/>`_. You don't need to understand its inner workings
to use this package. Here is a recipe to get you started::
  
  $ python bootstrap.py 
  $ ./bin/buildout

These 2 commands should download and install all non-installed dependencies and
get you a fully operational test and development environment.

.. note::

  The python shell used in the first line of the previous command set
  determines the python interpreter that will be used for all scripts developed
  inside this package. Because this package makes use of `Bob
  <http://idiap.github.com/bob>`_, you must make sure that the ``bootstrap.py``
  script is called with the **same** interpreter used to build Bob, or
  unexpected problems might occur.

  If Bob is installed by the administrator of your system, it is safe to
  consider it uses the default python interpreter. In this case, the above 3
  command lines should work as expected. If you have Bob installed somewhere
  else on a private directory, edit the file ``buildout.cfg`` **before**
  running ``./bin/buildout``. Find the section named ``external`` and edit the
  line ``egg-directories`` to point to the ``lib`` directory of the Bob
  installation you want to use. For example::

    [external]
    recipe = xbob.buildout:external
    egg-directories=/Users/crazyfox/work/bob/build/lib

Problems
--------

In case of problems, please contact ivana.chingovska@idiap.ch
