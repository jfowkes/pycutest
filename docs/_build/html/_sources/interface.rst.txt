Problem Interface
=================

Having built a problem, PyCUTEst returns an object of class :code:`CUTEstProblem`.
For fixed variables, its behaviour can be set with the :code:`drop_fixed_variables` flag for :code:`import_problem()`.
This class has the following attributes:

* :code:`problem.name`: CUTEst problem name (string)
* :code:`problem.n`: number of variables (equal to :code:`problem.n_free` if :code:`drop_fixed_variables=True`, otherwise :code:`problem.n_full`)
* :code:`problem.m`: number of constraints
* :code:`problem.x0`: starting point for optimization routine (NumPy array of shape :code:`(problem.n,)`)
* :code:`problem.sifParams`: dict of parameters passed to sifdecode
* :code:`problem.sifOptions`: list of extra options passed to sifdecode
* :code:`problem.vartype`: array of variable types (NumPy array size n, entry :code:`vartype[i]` indicates that x[i] is real(0), boolean(1), or integer(2))
* :code:`problem.nnzh`: number of nonzero entries in upper triangular part of objective Hessian (for all variables, including fixed)
* :code:`problem.nonlinear_vars_first`: flag if all nonlinear variables are listed before linear variables
* :code:`problem.bl`: array of lower bounds on input (unconstrained -> -1e20), as NumPy array of shape :code:`(problem.n,)`
* :code:`problem.bu`: array of upper bounds on input (unconstrained -> 1e20), as NumPy array of shape :code:`(problem.n,)`
* :code:`problem.n_full`: total number of variables in CUTEst problem (:code:`n_free + n_fixed`)
* :code:`problem.n_free`: number of free variables
* :code:`problem.n_fixed`: number of fixed variables

For constrained problems, we also have (these are all set to :code:`None` for unconstrained problems):

* :code:`problem.eq_cons_first`: flag if equality constraints are listed before inequality constraints
* :code:`problem.linear_cons_first`: flag if linear constraints are listed before nonlinear constraints
* :code:`problem.nnzj`: number of nonzero entries in constraint Jacobian (for all variables, including fixed)
* :code:`problem.v0`: starting point for Lagrange multipliers (NumPy array of shape :code:`(problem.m,)`)
* :code:`problem.cl`: lower bounds on constraints, as NumPy array of shape :code:`(problem.m,)`
* :code:`problem.cu`: upper bounds on constraints, as NumPy array of shape :code:`(problem.m,)`
* :code:`problem.is_eq_cons`: NumPy array of Boolean flags indicating if i-th constraint is equality or not (i.e. inequality)
* :code:`problem.is_linear_cons`: NumPy array of Boolean flags indicating if i-th constraint is linear or not (i.e. nonlinear)

The functions available are:

* :code:`problem.objcons()`: evaluate objective and constraints
* :code:`problem.obj()`: evaluate objective (and optionally its gradient)
* :code:`problem.cons()`: evaluate constraint(s) and optionally their Jacobian/its gradient
* :code:`problem.lagjac()`: evaluate gradient of objective/Lagrangian and Jacobian of constraints
* :code:`problem.jprod()`: evaluate constraint Jacobian-vector product
* :code:`problem.hess()`: evaluate Hessian of objective or Lagrangian
* :code:`problem.ihess()`: evaluate Hessian of objective or a specific constraint
* :code:`problem.hprod()`: evaluate Hessian-vector product (for objective or Lagrangian)
* :code:`problem.gradhess()`: evaluate gradient of objective/Lagrangian, Jacobian of constraints and Hessian of objective/Lagrangian
* :code:`problem.report()`: return a dictionary of statistics (number of objective/gradient evaluations, etc.)

For large-scale problems, you may want to get vectors/matrices as sparse matrices. We have the following functions which return sparse matrices:

* :code:`problem.scons()`: sparse alternative to :code:`problem.cons()`
* :code:`problem.slagjac()`: sparse alternative to :code:`problem.lagjac()`
* :code:`problem.sphess()`: sparse alternative to :code:`problem.hess()`
* :code:`problem.isphess()`: sparse alternative to :code:`problem.ihess()`
* :code:`problem.gradsphess()`: sparse alternative to :code:`problem.gradhess()`

Full details of each function are given below.

Full function documentation
---------------------------

.. autoclass:: pycutest.CUTEstProblem
   :members: objcons, obj, cons, lagjac, jprod, hess, ihess, hprod, gradhess, scons, slagjac, sphess, isphess, gradsphess, report

.. name, n, m, x0, sifParams, sifOptions, vartype, nnzh, nonlinear_vars_first, bl, bu, n_full, n_free, n_fixed, eq_cons_first, linear_cons_first, nnzj, v0, cl, cu, is_eq_cons, is_linear_cons,