""" Test all CUTEst functions (except the sparse ones) """
# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
import pycutest
import sys

# Nick's "all in it" test problem (intended to verify that changes to LANCELOT are safe).
from .allinitc import *
probname = 'ALLINITC'

# Load CUTEst problem
ct = pycutest.import_problem(probname)

# Return problem info
info = ct.getinfo()
print(info['name'])
print('info =', info)

# No. variables and constraints
n = info['n']
print('n =', n)
m = info['m']
print('m =', m)

# Lower and upper bounds
lb = ct.getinfo()['bl']
ub = ct.getinfo()['bu']
print('lb =', lb)
print('ub =', ub)

# Return the names of problem's variables.
varnames = ct.varnames()
print('varnames:', varnames)

# Return the names of problem's constraints.
connames = ct.connames()
print('connames:', connames)

# Set x
x = np.ones(n)
print('x =', x)

# Define approximate equality
def equal(a,b):
	assert np.all(a-b <= 1e-10)

# Return the value of objective and constraints at x
(f, c) = ct.objcons(x)
print('f(x) =', f)
print('c(x) =', c)
equal(f, f(x))
equal(c, c(x))

# Return the value of objective and its gradient at x
gradFlag = True # return gradient
(f, g) = ct.obj(x, gradFlag)
print('f(x) =', f)
print('g(x) =', g)
equal(f, f(x))
equal(g, g(x))

# Return the value of constraints and the Jacobian of constraints at x
# constraints
c = ct.cons(x)                 
print('c(x) =', c)
equal(c, c(x))
# i-th constraint
i = 0
ci = ct.cons(x, False, i)      
print('c_i(x) =', ci)
equal(ci, c(x)[i])
# Jacobian of constraints
(c, J) = ct.cons(x, True)      
print('c(x) =', c)
print('J(x) =', J)
equal(c, c(x))
equal(J, J(x))
# i-th constraint and its gradient
(ci, Ji) = ct.cons(x, True, i) 
equal(ci, c(x)[i])
equal(Ji, J(x)[i,:])

# Return the gradient of the objective or Lagrangian, and the Jacobian of constraints at x. 
# The gradient is the gradient with respect to the problem's variables (has n components)
# objective gradient and the Jacobian of constraints
(g, J) = ct.lagjac(x)
print('g(x) =', g)
print('J(x) =', J)
equal(g, g(x))
equal(J, J(x))
# Lagrangian gradient and the Jacobian of constraints
v = np.ones(m)
(gL, J) = ct.lagjac(x, v)
print('gL(x) =', gL)
print('J(x) =', J)
equal(gL, gL(x,v))
equal(J, J(x))

# Return the product of constraints Jacobian at x with vector p
# computes Jacobian at x before product calculation
p = np.ones(m)
transpose = True # transpose Jacobian
r = ct.jprod(transpose, p, x)
print('J(x)^Tp =', r)
equal(r, J(x).T.dot(p))
# uses last computed Jacobian
r = ct.jprod(transpose, p)
print('J(x)^Tp =', r)
equal(r, J(x).T.dot(p))

# Return the Hessian of the objective (for unconstrained problems) or the
# Hessian of the Lagrangian (for constrained problems) at x
# Hessian of objective at x for unconstrained problems
#H = ct.hess(x)
#print('H(x) =', H)
#equal(H, H(x))
# Hessian of Lagrangian at (x, v) for constrained problems
v = np.ones(m)
HL = ct.hess(x, v)
print('HL(x) =', HL)
equal(HL, HL(x,v))

# Return the Hessian of the objective or the Hessian of i-th constraint at x
# Hessian of the objective 
H = ct.ihess(x)
print('H(x) =', H)
equal(H, H(x))
# Hessian of i-th constraint
i = 0
Hi = ct.ihess(x, i)
print('H_i(x) =', Hi)
equal(Hi, T(x)[i,:,:])

# Return the product of Hessian at x and vector p.
# The Hessian is either the Hessian of objective or the Hessian of Lagrangian
# use Hessian of Lagrangian at x (constrained problem)
p = np.ones(n)
v = np.ones(m)
r = ct.hprod(p, x, v)
print('HL(x)p =', r)
equal(r, HL(x,v).dot(p))
# use Hessian of objective at x (unconstrained problem)
#p = np.ones(n)
#r = ct.hprod(p, x)
#print('H(x)p =', r)
#equal(r, H(x).dot(p))
# use last computed Hessian
r = ct.hprod(p)
print('HL(x)p =', r)
equal(r, HL(x,v).dot(p))

# Return the Hessian of the Lagrangian, the Jacobian of constraints, and the
# gradient of the objective or the gradient of the Lagrangian at x
# for unconstrained problems
#(g, H) = ct.gradhess(x)
#print('g(x) =', g(x))
#print('H(x) =', H(x))
# for constrained problems
v = np.ones(m)
gradl = True # return gradient of the Lagrangian
(gL, J, HL) = ct.gradhess(x, v, gradl)
print('gL(x) =', g)
print('J(x) =', J)
print('HL(x) =', H)
equal(gL, gL(x,v))
equal(J, J(x))
equal(HL, HL(x,v))

# Report usage statistics
stats = ct.report()
print('stats =', stats)
