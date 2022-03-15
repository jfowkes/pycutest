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

List of existing tools:
* Underlying CUTE/CUTEr/CUTEst packages (have everything but not easily accessible)
* AMPL
* GAMS
* JuMP

# Statement of need
Key ideas:
* Simplification of algorithm development and testing
* Allows benchmarking of solvers for specific test cases
* CUTEst only high-level interface until now is Matlab (not open source)
* Significant Python optimization community

# Acknowledgements

TBC

# References