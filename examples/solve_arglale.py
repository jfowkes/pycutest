"""
PyCUTEst example: minimize 10D ALRGLALE problem using the Gauss-Newton algorithm.

Jaroslav Fowkes and Lindon Roberts, 2022.
"""

# Ensure compatibility with Python 2
from __future__ import print_function
import numpy as np
import pycutest

# Nonlinear least-squares problem in 10 dimensions with 20 residuals
p = pycutest.import_problem('ARGLALE', sifParams={'N':10, 'M':20})

print("ARGLALE problem in %gD with %g residuals" % (p.n, p.m))

iters = 0

x = p.x0
r, J = p.cons(x, gradient=True)  # residual and Jacobian
f = 0.5 * np.dot(r, r)  # objective
g = J.T.dot(r)  # gradient
H = J.T.dot(J)  # Gauss-Newton Hessian approximation

while iters < 100 and np.linalg.norm(g) > 1e-10:
    print("Iteration %g: objective value is %g with norm of gradient %g at x = %s" % (iters, f, np.linalg.norm(g), str(x)))
    s = np.linalg.solve(H, -g)  # Gauss-Newton step
    x = x + s  # used fixed step length
    r, J = p.cons(x, gradient=True)
    f = 0.5 * np.dot(r, r)
    g = J.T.dot(r)
    H = J.T.dot(J)
    iters += 1

print("Found minimum x = %s after %g iterations" % (str(x), iters))
print("Done")
