========================================
:mod:`orangecontrib.earth` API reference
========================================

.. module:: orangecontrib.earth

Learner/Classifier
------------------

The :class:`EarthLearner` and :class:`EarthClassifier` provide the
standard Orange learner/classifier pair for model induction/prediction.

.. autoclass:: EarthLearner
   :show-inheritance:
   :members:
   :special-members: __call__


.. autoclass:: EarthClassifier
   :show-inheritance:
   :members:
   :special-members: __call__


.. seealso:: :mod:`Orange.classification`


Example::

    >>> import Orange, orangecontrib.earth
    >>> data = Orange.data.Table("housing")
    >>> c = orangecontrib.earth.EarthLearner(data, degree=2, terms=10)
    >>> print c
    MEDV =
       23.587
       +11.896 * max(0, RM - 6.431)
       +1.142 * max(0, 6.431 - RM)
       -0.612 * max(0, LSTAT - 6.120)
       -228.795 * max(0, NOX - 0.647) * max(0, RM - 6.431)
       +0.023 * max(0, TAX - 307.000) * max(0, 6.120 - LSTAT)
       +0.029 * max(0, 307.000 - TAX) * max(0, 6.120 - LSTAT)


Feature scoring
---------------

.. autoclass:: ScoreEarthImportance
   :show-inheritance:
   :members:
   :special-members: __call__


.. seealso:: :mod:`Orange.feature.scoring`


Utility functions
-----------------

.. autofunction:: gcv

.. autofunction:: plot_evimp

.. autofunction:: bagged_evimp
