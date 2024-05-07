Version History
===============
This section lists the different versions of PyCUTEst and the updates between them.

Version 1.7.0 (7 May 2024)
--------------------------
* New sobj function to evaluate the objective and sparse gradient
* New sgrad function to evaluate the sparse gradient only
* Document the need to install Python headers on Ubuntu

Version 1.6.2 (9 Apr 2024)
--------------------------
* Migrate from setup.py to pyproject.toml

Version 1.6.1 (8 Mar 2024)
--------------------------
* Add setuptools requirement to setup.py

Version 1.6.0 (24 Jan 2024)
---------------------------
* New grad function to evaluate the gradient only
* New lag function to evaluate the Lagrangian

Version 1.5.1 (8 Aug 2023)
--------------------------
* Fix invalid sparse dimensions while dropping fixed variables
* Rename equality to fixed constraints for clarity
* Restore current working directory on failure
* Fix conversion of 1x1 NumPy arrays to scalars

Version 1.5.0 (22 Feb 2023)
---------------------------
* Fix memory leak in C interface (cache-breaking change)
* Modernise C interface (cache-breaking change)
* Drop Python 2.7 support as it is EOL
* Fix installs on non-default homebrew paths
* Use homebrew prefix for fallback paths on macOS
* Switch to semantic versioning

Version 1.4 (24 Oct 2022)
-------------------------
* Add guidelines for seeking support
* Improve documentation

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
