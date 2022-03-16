---
title: '`PyCUTEst`: an open source `Python` package of optimization test problems'
tags:
  - Python
  - optimization
authors:
  - name: Arpad Bürmen
    affiliation: 1
  - name: Jaroslav Fowkes
    affiliation: 2
  - name: Lindon Roberts
    affiliation: 3
affiliations:
  - name: Faculty of Electrical Engineering, University of Ljubljana, Tržaška cesta 25, SI-1000 Ljubljana, Slovenia 
    index: 1
  - name: Science and Technology Facilities Council, Rutherford Appleton Laboratory, Harwell Campus, Didcot, Oxfordshire, OX11 0QX, UK
    index: 2
  - name: Mathematical Sciences Institute, Building 145, Science Road, Australian National University, Canberra ACT 2601, Australia
    index: 2
date: March 2022
bibliography: paper.bib
---
# Summary

Solving mathematical optimization problems is a critical task for many areas of study.
Because of the complexity of such problems, a plethora of algorithms and software exists for solving such problems.
[`PyCUTEst`](https://github.com/jfowkes/pycutest) provides efficient access to the `CUTEst` [@cutest] library of 
nonlinear optimization test problems.

This assists numerical algorithm and software developers to test new ideas against a state-of-the-art and collection 
of test problems which span small- and large-scale, constrained and unconstrained nonlinear optimization problems.

`PyCUTEst` also allows scientists and other users of optimization software to compare potential software and algorithms
against these test problems, helping them to select the tools most suited to their needs.

`PyCUTEst` is easy to install via `pip` and our [documentation](https://jfowkes.github.io/pycutest/) gives details on 
how users can install the underlying dependencies. 

# State of the field

The CUTEst [@cutest] library is a widely used collection of nonlinear optimization test problems, based on the original
CUTE [@cute] and CUTEr [@cuter] packages.
It has a collection of over 1500 problems, many of which are parametrized to allow for variable dimensions, etc.
However, despite the popularity of this package, it is currently only accessible through Fortran or MATLAB interfaces 
provided in the main package, or a new Julia interface [@cutestjl].
In particular, there is no way to use CUTEst through Python, even though Python is widely used in numerical 
computation and has a large ecosystem of open source software for nonlinear optimization.

The other most popular tools for encoding optimization test problems are the modelling languages AMPL [@ampl] 
and GAMS [@gams]. 
Although both provide Python interfaces, and in fact many CUTEst problems have been translated into AMPL [@cuteampl],
they are proprietary packages. 
One open source alternative to AMPL and GAMS is the Julia package JuMP [@jump].

# Statement of need

PyCUTEst allows Python users access to the full CUTEst package of test problems via a simple interface for 
compiling problems (which automatically generates a C interface to the underlying Fortran package).
To our knowledge, this is the only available Python package for accessing the CUTEst library.

The main benefits of this package are:
* Enabling the use of CUTEst to the sizeable community of Python optimization software developers and users.
* Allowing simple benchmarking of optimization algorithms against a widely use standard collection of problems.

# Acknowledgements

TBC

# References