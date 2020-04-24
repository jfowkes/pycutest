.. PyCUTEst documentation master file, created by
   sphinx-quickstart on Wed Aug  8 11:07:30 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyCUTEst
========
Python interface to the CUTEst optimization test environment
--------------------------------------------------------------

**Release:** |version|

**Date:** 22 April 2020

**Author:** `Jaroslav Fowkes <jaroslav.fowkes@maths.ox.ac.uk@maths.ox.ac.uk>`_ and `Lindon Roberts <lindon.roberts@maths.ox.ac.uk>`_

PyCUTEst is a Python interface to `CUTEst <https://github.com/ralna/CUTEst>`_, a Fortran package for testing optimization software [1]_. It is based on the interface originally developed for CUTEr by `Prof. Arpad Buermen <http://www.fe.uni-lj.si/en/the_faculty/staff/alphabetically/55/>`_ [2]_. Currently it supports Mac and Linux only, although on Windows 10 it can be used through the `Windows Subsystem for Linux <https://docs.microsoft.com/en-us/windows/wsl/faq>`_, following the Linux installation instructions.

In essence, this package gives convenient access to a large collection of nonlinear optimization test problems.

PyCUTEst is released under the GNU General Public License.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   building
   interface
   example
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
