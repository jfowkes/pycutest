# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

import cutestmgr
import sys

if len(sys.argv) > 1:
    name = sys.argv[1]
else:
    name = 'COOLHANS'

if not cutestmgr.isCached(name):
    cutestmgr.prepareProblem(name)
rb = cutestmgr.importProblem(name)

info = rb.getinfo()
print(info['name'])

x0 = info['x']
print('x0 = ', x0)

n = info['n']
print('n = ', n)

m = info['m']
print('m = ', m)

lb = rb.getinfo()['bl']
ub = rb.getinfo()['bu']
print('lb = ', lb)
print('ub = ', ub)

r_x0, J_x0 = rb.cons(x0, True)
print('r(x0) = ', r_x0)
print('J(x0) = ', J_x0)

gradf_x0 = rb.jprod(True, r_x0)
print('g(x0) = ', gradf_x0)
print('g(x0) = ', J_x0.T.dot(r_x0))
