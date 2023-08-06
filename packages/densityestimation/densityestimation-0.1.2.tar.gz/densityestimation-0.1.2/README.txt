==================
Density Estimation
==================

This package provides functions for three specific types of density estimators.  
You might find it most useful for tasks involving plotting kernel density estimates, 
histograms and nearest-neighbor density estimates.

Typical intallation often looks like this::

    !pip install densityestimation


Dependencies
============

* Numpy

* Matplotlib


Examples
========

| import numpy as np
| sample = np.random.normal(0,1,1000)
| kde(sample) 
|
| import numpy as np
| sample = np.random.normal(0,1,1000)
| hist(sample)
|
| import numpy as np
| sample = np.random.normal(0,1,1000)
| nnde(sample)


Contributors
=============

We would like to thank our professor, Brian Chapman, for guiding us
through our first ever endeavors involving Python.  It is because of
you, this class and this project that density estimation in Python
will never be the same, or at least in our eyes.