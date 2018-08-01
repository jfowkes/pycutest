# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
import pycutest

# p = pycutest.import_problem('ROSENBR')
p = pycutest.import_problem('ARGLALE', sifParams={'N':10, 'M':20})
# p = pycutest.import_problem('ALLINITC')

# Return problem info
print(p)
print("Name =", p.name)
print("# variables =", p.n)
print("# constraints =", p.m)
print("Lower bound =", p.bl)
print("Upper bound =", p.bu)
# print("Variable names =", p.varnames())
# print("Constraint names =", p.connames())
print("x0 =", p.x0)

# Define approximate equality
def equal(a,b):
    assert np.all(a-b <= 1e-10)

# Return the value of objective and constraints at x
f, c = p.objcons(p.x0)
print('f(x0) =', f)
print('c(x0) =', c)

if p.name == 'ARGLALE':
    r_x0, J_x0 = p.cons(p.x0, gradient=True)
    print('r(x0) =', r_x0)
    print('J(x0) =', J_x0)

    gradf_x0 = p.jprod(r_x0, transpose=True)
    print('g(x0) =', gradf_x0)
    gradf_x0 = p.jprod(r_x0, transpose=True, x=p.x0)
    print('g(x0) =', gradf_x0)
    print('g(x0) =', J_x0.T.dot(r_x0))

print('Done')