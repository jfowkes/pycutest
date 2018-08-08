"""
PyCUTEst example: minimize 2D Rosenbrock function using Newton's method.

Jaroslav Fowkes and Lindon Roberts, 2018.
"""

# Ensure compatibility with Python 2
from __future__ import print_function
import numpy as np
import pycutest

p = pycutest.import_problem('ROSENBR')

print("Rosenbrock function in %gD" % p.n)

iters = 0

x = p.x0
f, g = p.obj(x, gradient=True)  # objective and gradient
H = p.hess(x)  # Hessian

while iters < 100 and np.linalg.norm(g) > 1e-10:
    print("Iteration %g: objective value is %g with norm of gradient %g at x = %s" % (iters, f, np.linalg.norm(g), str(x)))
    s = np.linalg.solve(H, -g)  # Newton step
    x = x + s  # used fixed step length
    f, g = p.obj(x, gradient=True)
    H = p.hess(x)
    iters += 1

print("Found minimum x = %s after %g iterations" % (str(x), iters))
print("Done")
