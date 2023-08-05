===================================================
The FAR-FRR confidence interval of the DET curve for Bob
===================================================

This example demonstrates how to extend Bob by providing a new performance measurement for measuring the confidence interval of the DET curve.

Originally described in the paper:
  Poh, N.; Martin, A.; Bengio, S., "Performance Generalization in Biometric Authentication Using Joint User-Specific and Sample Bootstraps," Pattern Analysis and Machine Intelligence, IEEE Transactions on , vol.29, no.3, pp.492,498, March 2007

Installation
============

First, you have to install `bob <http://www.idiap.ch/software/bob>`_ following the instructions
`there <http://www.idiap.ch/software/bob/docs/releases/last/sphinx/html/Installation.html>`_.

.. note:: 

  If you are reading this page through our GitHub portal and not through PyPI,
  note **the development tip of the package may not be stable** or become
  unstable in a matter of moments.

  Go to `http://pypi.python.org/pypi/xbob.measure.Bootstraps
  <http://pypi.python.org/pypi/xbob.>`_ to download the latest
  stable version of this package.

There are two options you can follow to get this package installed and 
operational on your computer: you can use automatic installers like `pip
<http://pypi.python.org/pypi/pip/>`_ (or `easy_install
<http://pypi.python.org/pypi/setuptools>`_) or manually download, unpack and 
use `zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_ to create a
virtual work environment just for this package. In both cases, the two 
dependences listed above will be automatically downloaded and installed.

Using an automatic installer
----------------------------

Using ``pip`` is the easiest (shell commands are marked with a ``$`` signal)::

  $ pip install xbob.measure.Bootstraps

You can also do the same with ``easy_install``::

  $ easy_install xbob.measure.Bootstraps

This will download and install this package plus any other required
dependencies. It will also verify if the version of Bob you have installed
is compatible.

This scheme works well with virtual environments by `virtualenv
<http://pypi.python.org/pypi/virtualenv>`_ or if you have root access to your
machine. Otherwise, we recommend you use the next option.

Using ``zc.buildout``
---------------------

Download the latest version of this package from `PyPI
<http://pypi.python.org/pypi/xbob.measure.Bootstraps>`_ and unpack it in your
working area. The installation of the toolkit itself uses `buildout
<http://www.buildout.org/>`_. You don't need to understand its inner workings
to use this package. Here is a recipe to get you started::
  
  $ python bootstrap.py 
  $ ./bin/buildout

These two commands should download and install all non-installed dependencies and 
get you a fully operational test and development environment.

.. note::

  The python shell used in the first line of the previous command set
  determines the python interpreter that will be used for all scripts developed
  inside this package. Because this package makes use of `Bob`_, you must make sure that the ``bootstrap.py``
  script is called with the **same** interpreter used to build Bob, or
  unexpected problems might occur.

  If Bob is installed by the administrator of your system, it is safe to
  consider it uses the default python interpreter. In this case, the above 3
  command lines should work as expected. If you have Bob installed somewhere
  else on a private directory, edit the file ``buildout.cfg`` **before**
  running ``./bin/buildout``. Find the section named ``buildout`` and edit or
  add the line ``prefixes`` to point to the directory where Bob is installed or
  built. For example::

    [buildout]
    ...
    prefixes=/Users/crazyfox/work/bob/build


User Guide
==========

It is assumed you have followed the installation instructions for the package
and got this package installed.

Below, we provide an example of how to appy jointbootstraps to plot the confidence curve, from 
the python universe::

  >>> import Bootstraps
  # predefine a list of confidence rates
  >>> confidence=[.25, 0.5, .75]
  >>> n_user_bstrp=30
  >>> n_sample_bstrp=3
  #Read The four column file needs to be in the same format as described in the five_column function,
  and the "test label" (column 4) has to contain the test/probe file name.  please refer the functions of bob.measure.load.cmc_four_column, bob.measure.load.cmc_five_column to load or generate the "cmc scores".
  >>> Bootstraps.JointBootstraps_plot(cmc_scores,confidence,n_user_bstrp,n_sample_bstrp=3)
  #Plot the DET curve
  >>> pos_scores=[]
  >>> neg_scores=[]
  >>> for Id in range(0,len(cmc_scores)):
  >>>   pos_scores=numpy.append(pos_scores, cmc_scores[Id][1])
  >>>   neg_scores=numpy.append(neg_scores, cmc_scores[Id][0])
  >>> bob.measure.plot.det(neg_scores,pos_scores,100)
  >>> bob.measure.plot.det_axis([.05, 60, .05, 60])
  >>> pyplot.xlabel("False Acceptance Rate")
  >>> pyplot.ylabel("False Rejection Rate")
  >>> pyplot.title("The FAR-FRR confidence interval of the DET curve")
  >>> pyplot.grid()
  >>> pyplot.savefig("Confidence_DET.png")
  >>> pyplot.close()

