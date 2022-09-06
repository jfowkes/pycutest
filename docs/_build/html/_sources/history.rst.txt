Version History
===============
This section lists the different versions of PyCUTEst and the updates between them.

Version 1.3 (6 Sep 2022)
------------------------
* Use human-readable problem properties (breaking change)
* Check v is/isn't None for hess and sphess
* Add types to problem method docstrings
* Add guidelines for contributors
* Simplify CUTEst installation
* Add CUTEst docker install option
* Improve documentation

Version 1.2 (21 Feb 2022)
-------------------------
* Use setuptools instead of distutils
* Remove deprecated NumPy calls
* Improve macOS support
* Update documentation

Version 1.1 (14 Feb 2022)
-------------------------
* Automatically add PYCUTEST_CACHE to PYTHONPATH at runtime (simplifies installation)

Version 1.0 (22 Apr 2020)
-------------------------
* Handle non-letter characters in SIF parameter names
* Fix unclosed file warnings
* Automatically check if PYCUTEST_CACHE variable is in system path

Version 0.2 (6 Jun 2019)
------------------------
* Throw RuntimeError if invalid sif parameters provided
* Recognise local gfortran installation for Mac
* Update required NumPy and SciPy versions for Python 2.7

Version 0.1 (6 Sep 2018)
------------------------
* Initial release of PyCUTEst
