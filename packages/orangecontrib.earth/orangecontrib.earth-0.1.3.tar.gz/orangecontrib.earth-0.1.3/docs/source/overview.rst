========
Overview
========


:mod:`orangecontrib.earth` provides a an implementation of
`Multivariate adaptive regression splines (MARS)`_ for the `Orange`_
machine learning library. This implementation is based on the C code from
`R package earth`_ by Stephen Milborrow.


.. _`Multivariate adaptive regression splines (MARS)`: http://en.wikipedia.org/wiki/Multivariate_adaptive_regression_splines

.. _`R package earth`: http://cran.r-project.org/web/packages/earth/index.html

.. _`Orange`: http://orange.biolab.si


Prerequisites
-------------

In order to use `orangecontrib.earth` you need to have already installed
`Orange` (version 2.7 or latest).

If you are installing from source you will also need the a working
C compiler tool-chain.

* On Windows install the free `Microsoft Visual C++ 2008 Express
  <http://www.microsoft.com/express>`_ (`direct download link
  <http://go.microsoft.com/fwlink/?linkid=244366>`_)

* On Linux use you distribution's package management tools to install gcc

* On Mac OSX install the `XCode developer tools
  <http://developer.apple.com/xcode>`_


Installing
----------

You can install it using pip or easy_install::

   pip install orangecontrib.earth

or::

   easy_install orangecontrib.earth

