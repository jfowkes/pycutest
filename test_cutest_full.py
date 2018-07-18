""" Test all CUTEst functions (except the sparse ones) """
# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np

import cutestmgr
import sys

# Nick's "all in it" test problem (intended to verify that changes to LANCELOT are safe).
probname = 'ALLINITC'

if not cutestmgr.isCached(probname):
    cutestmgr.prepareProblem(probname)
rb = cutestmgr.importProblem(probname)

# Return problem info
info = rb.getinfo()
print(info['name'])
print('info =', info)

# Set x to x0
x = info['x']
print('x0 =', x)

# No. variables and constraints
n = info['n']
print('n =', n)
m = info['m']
print('m =', m)

# Lower and upper bounds
lb = rb.getinfo()['bl']
ub = rb.getinfo()['bu']
print('lb =', lb)
print('ub =', ub)

# Return the names of problem's variables.
varnames = rb.varnames()
print('varnames:', varnames)

# Return the names of problem's constraints.
connames = rb.connames()
print('connames:', connames)

# Return the value of objective and constraints at x
(f, c) = rb.objcons(x)
print('f(x) =', f)
print('c(x) =', c)

# Return the value of objective and its gradient at x
gradFlag = True # return gradient
(f, g) = rb.obj(x, gradFlag)
print('f(x) =', f)
print('g(x) =', g)

# Return the value of constraints and the Jacobian of constraints at x
# constraints
c = rb.cons(x)                 
print('c(x) =', c)
# i-th constraint
i = 0
ci = rb.cons(x, False, i)      
print('c_i(x) =', ci)
# Jacobian of constraints
(c, J) = rb.cons(x, True)      
print('c(x) =', c)
print('J(x) =', J)
# i-th constraint and its gradient
(ci, Ji) = rb.cons(x, True, i) 
print('c_i(x) =', ci)
print('J_i(x) =', Ji)

# Return the gradient of the objective or Lagrangian, and the Jacobian of constraints at x. 
# The gradient is the gradient with respect to the problem's variables (has n components)
# objective gradient and the Jacobian of constraints
(g, J) = rb.lagjac(x)
print('g(x) =', g)
print('J(x) =', J)
# Lagrangian gradient and the Jacobian of constraints
v = np.ones(m)
(Lg, J) = rb.lagjac(x, v)
print('Lg(x) =', Lg)
print('J(x) =', J)

# Return the product of constraints Jacobian at x with vector p
# computes Jacobian at x before product calculation
p = np.ones(m)
transpose = True # transpose Jacobian
r = rb.jprod(transpose, p, x)
print('J(x)^Tp =', r)
# uses last computed Jacobian
r = rb.jprod(transpose, p)
print('J(x)^Tp =', r)

# Return the Hessian of the objective (for unconstrained problems) or the
# Hessian of the Lagrangian (for constrained problems) at x
# Hessian of objective at x for unconstrained problems
#H = rb.hess(x)
#print('H(x) =', H)
# Hessian of Lagrangian at (x, v) for constrained problems
v = np.ones(m)
H = rb.hess(x, v)
print('H(x) =', H)

# Return the Hessian of the objective or the Hessian of i-th constraint at x
# Hessian of the objective 
H = rb.ihess(x)
print('H(x) =', H)
# Hessian of i-th constraint
i = 0
Hi = rb.ihess(x, i)
print('H_i(x) =', Hi)

# Return the product of Hessian at x and vector p.
# The Hessian is either the Hessian of objective or the Hessian of Lagrangian
# use Hessian of Lagrangian at x (constrained problem)
p = np.ones(n)
v = np.ones(m)
r = rb.hprod(p, x, v)
print('H(x)p =', r)
# use Hessian of objective at x (unconstrained problem)
#p = np.ones(n)
#r = rb.hprod(p, x)
#print('H(x)p =', r)
# use last computed Hessian
r = rb.hprod(p)
print('H(x)p =', r)

# Return the Hessian of the Lagrangian, the Jacobian of constraints, and the
# gradient of the objective or the gradient of the Lagrangian at x
# for unconstrained problems
#(g, H) = rb.gradhess(x)
#print('g(x) =', g)
#print('H(x) =', H)
# for constrained problems
v = np.ones(m)
gradl = True # return gradient of the Lagrangian
(g, J, H) = rb.gradhess(x, v, gradl)
print('g(x) =', g)
print('J(x) =', J)
print('H(x) =', H)

# Report usage statistics
stats = rb.report()
print('stats =', stats)

