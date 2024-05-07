.. PyCUTEst documentation master file, created by
   sphinx-quickstart on Wed Aug  8 11:07:30 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyCUTEst
========
Python interface to the CUTEst optimization test environment
------------------------------------------------------------

**Release:** |version|

**Date:** 7 May 2024

**Author:** `Jaroslav Fowkes <jaroslav.fowkes@maths.ox.ac.uk>`_ and `Lindon Roberts <https://lindonroberts.github.io/>`_

PyCUTEst is a Python interface to `CUTEst <https://github.com/ralna/CUTEst>`_, a Fortran package for testing optimization software [1]_. It is based on the interface originally developed for CUTEr by `Prof. Arpad Buermen <http://www.fe.uni-lj.si/en/the_faculty/staff/alphabetically/55/>`_ [2]_. Currently it supports Mac and Linux only, although on Windows 10 (and later) it can be used through the `Windows Subsystem for Linux <https://docs.microsoft.com/en-us/windows/wsl/>`_, following the Linux installation instructions.

In essence, this package gives convenient access to a large collection of nonlinear optimization test problems.

PyCUTEst is released under the GNU General Public License.

The aim of PyCUTEst
-------------------
PyCUTEst gives Python users access to the full `CUTEst <https://github.com/ralna/CUTEst>`_ collection of optimization test problems via a simple interface for compiling problems (that automatically generates a C interface to the underlying Fortran package).

The main benefits of the PyCUTEst package are:

* Enabling the use of the CUTEst test collection by the sizeable community of Python optimization software developers and users.

* Allowing simple benchmarking of optimization algorithms and software in Python against a widely used standard collection of test problems.

Our aim is for PyCUTEst to make it easier for both optimization users and software developers to develop and test new and existing algorithms and software in Python.

Citing PyCUTEst
---------------
To cite PyCUTEst, please use the following reference:

`J. Fowkes, L. Roberts, and Á. Bűrmen, (2022). PyCUTEst: an open source Python package of optimization test problems. Journal of Open Source Software, 7(78), 4377, https://doi.org/10.21105/joss.04377`

In BibTeX, the citation is:

.. code-block::

    @article{PyCUTEst2022,
        doi = {10.21105/joss.04377},
        url = {https://doi.org/10.21105/joss.04377},
        year = {2022},
        publisher = {The Open Journal},
        volume = {7},
        number = {78},
        pages = {4377},
        author = {Jaroslav Fowkes and Lindon Roberts and Árpád Bűrmen},
        title = {PyCUTEst: an open source Python package of optimization test problems},
        journal = {Journal of Open Source Software}
    }


.. toctree::
   :maxdepth: 2
   :caption: Contents

   install
   building
   interface
   example
   support
   contributing
   history

* :ref:`genindex`

.. * :ref:`modindex`
   * :ref:`search`

References
----------

.. [1]
   Gould, N. I. M., Orban, D. and Toint, P. L. (2015) CUTEst: a Constrained and Unconstrained Testing Environment with safe threads for mathematical optimization, *Computational Optimization and Applications*, vol. 60, no. 3, pp. 545-557. https://doi.org/10.1007/s10589-014-9687-3

.. [2]
   Buermen, A. Python interface to CUTEr test problems for optimization. http://fides.fe.uni-lj.si/~arpadb/software-pycuter.html
