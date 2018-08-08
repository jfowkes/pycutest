Example Usage
=============

The following code presents a simple use of PyCUTEst to minimize `Rosenbrock's function <https://en.wikipedia.org/wiki/Rosenbrock_function>`_ in 2D (problem :code:`ROSENBR`) using Newton's method.

.. code-block:: python

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

For this problem, Newton's method finds the unique local and global minimum :code:`f(1,1)=0` quickly:

.. code-block:: none

    Rosenbrock function in 2D
    Iteration 0: objective value is 24.2 with norm of gradient 232.868 at x = [-1.2  1. ]
    Iteration 1: objective value is 4.73188 with norm of gradient 4.63943 at x = [-1.1752809   1.38067416]
    Iteration 2: objective value is 1411.85 with norm of gradient 1370.79 at x = [ 0.76311487 -3.17503385]
    Iteration 3: objective value is 0.0559655 with norm of gradient 0.47311 at x = [0.76342968 0.58282478]
    Iteration 4: objective value is 0.313189 with norm of gradient 25.0274 at x = [0.99999531 0.94402732]
    Iteration 5: objective value is 1.85274e-11 with norm of gradient 8.60863e-06 at x = [0.9999957  0.99999139]
    Iteration 6: objective value is 3.43265e-20 with norm of gradient 8.28571e-09 at x = [1. 1.]
    Found minimum x = [1. 1.] after 7 iterations
    Done

