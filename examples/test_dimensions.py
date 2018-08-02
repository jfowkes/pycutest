#!/usr/bin/env python3

"""
Test interface for parameter-dependent problems
"""

# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

import pycutest
import numpy as np

# name = 'ARGLALE'
# params = {'N': 10}
# params = {'N': 50}

name = 'SEMICON2'
# params = {'N':10, 'LN':9}
params = {'N':100, 'LN':90}

rb = pycutest.import_problem(name, sifParams=params)

info = rb.getinfo()
print(info['name'], info['sifparams'])

x0 = info['x']
# print('x0 = ', x0)

n = info['n']
print('n = ', n)

r0, J0 = rb.cons(x0, True)
g0 = np.dot(J0.T, r0)
print('f(x0) = ', np.dot(r0, r0))
print('||gradf(x0)|| = ', np.linalg.norm(g0))
print("Done")
