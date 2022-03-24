---
title: '`PyCUTEst`: an open source `Python` package of optimization test problems'
tags:
  - Python
  - optimization
authors:
  - name: Árpád Bűrmen
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
    index: 3
date: March 2022
bibliography: paper.bib
---
# Summary

Solving mathematical optimization problems is a critical task for many disciplines, ranging from cutting-edge scientific research to the management of financial portfolios.
Due to the inherent complexity of such problems, a plethora of different algorithms and software have been developed for solving them, and this necessitated a standard collection of test problems on which optimization algorithms and software can be evaluated.
[`PyCUTEst`](https://github.com/jfowkes/pycutest) provides efficient access to the extensive `CUTEst` [@cutest] library of
nonlinear optimization test problems, long a standard test set for nonlinear optimization. In particular, `PyCUTEst`:

* assists numerical algorithm and software developers in testing new ideas against a state-of-the-art collection
of test problems that span small- and large-scale, constrained and unconstrained, nonlinear optimization problems.

* allows scientists and other users of optimization software to compare candidate algorithms and software on standard test problems, helping them select the tools best suited to their needs.

* is easy to install via `pip` and our detailed [documentation](https://jfowkes.github.io/pycutest/) provides instructions on
how users can easily install the underlying `CUTEst` test collection.

In short, our aim is that `PyCUTEst` will make it easier for users to test new and existing optimization algorithms and software in Python. With over 12,000 downloads we firmly believe that `PyCUTEst` is well on the way to achieving this aim.

# State of the field

The `CUTEst` [@cutest] library is a widely used collection of nonlinear optimization test problems, based on the original
`CUTE` [@cute] and `CUTEr` [@cuter] packages.
It has a collection of over 1,500 problems, many of which are parametrized to allow for variable dimensions through user-selectable parameters.
However, despite the popularity of `CUTEst`, it is currently only accessible through Fortran, C or MATLAB interfaces
provided with the main package, or through the Julia interface `CUTEst.jl` [@cutestjl].
In particular, it is not possible to use `CUTEst` in Python, even though Python is widely used in numerical
computing and has a large ecosystem of open source software for nonlinear optimization.

The other widely used packages that encode optimization test problems are the modelling languages `AMPL` [@ampl]
and `GAMS` [@gams].
Although both provide Python interfaces, and in fact many `CUTEst` problems have been translated into `AMPL` [@cuteampl],
they are proprietary packages.
An open source alternative to `AMPL` and `GAMS` is the Julia package `JuMP` [@jump].

# Statement of need

`PyCUTEst` gives Python users access to the full `CUTEst` [@cutest] collection of optimization test problems via a simple interface for
compiling problems (that automatically generates a C interface to the underlying Fortran package).
To the best of our knowledge, this is the only available Python package for accessing the `CUTEst` library that is stable and maintained.

The main benefits of the `PyCUTEst` package are:

* Enabling the use of the `CUTEst` test collection by the sizeable community of Python optimization software developers and users.

* Allowing simple benchmarking of optimization algorithms and software in Python against a widely used standard collection of test problems.

Our aim is for `PyCUTEst` to make it easier for both optimization users and software developers to develop and test new and existing algorithms and software in Python. Since its inception just under four years ago, `PyCUTEst` has had over 12,000 downloads, and we believe is well on the way to achieving this aim.

# Acknowledgements

We would like to thank Nick Gould for his helpful advice when we were developing `PyCUTEst` and Coralia Cartis for suggesting that we make `PyCUTEst` more widely available.

# References
