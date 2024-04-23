Problem Interface
=================

Having built a problem, PyCUTEst returns an instance of class :code:`CUTEstProblem`
(for fixed variables, its behaviour can be set with the :code:`drop_fixed_variables` flag for :code:`import_problem()`).

Problem Methods
---------------

The methods available for each :code:`CUTEstProblem` instance are:

* `obj(x[, gradient]) <methods/pycutest.CUTEstProblem.obj.html>`_: evaluate objective (and optionally its gradient)
* `grad(x[, index]) <methods/pycutest.CUTEstProblem.grad.html>`_: evaluate objective gradient or specific constraint gradient
* `objcons(x) <methods/pycutest.CUTEstProblem.objcons.html>`_: evaluate objective and constraints
* `cons(x[, index, gradient]) <methods/pycutest.CUTEstProblem.cons.html>`_: evaluate constraint(s) and optionally their Jacobian/its gradient
* `lag(x, v[, gradient]) <methods/pycutest.CUTEstProblem.lag.html>`_: evaluate Lagrangian function value and optionally its gradient
* `lagjac(x[, v]) <methods/pycutest.CUTEstProblem.lagjac.html>`_: evaluate gradient of objective/Lagrangian and Jacobian of constraints
* `jprod(p[, transpose, x]) <methods/pycutest.CUTEstProblem.jprod.html>`_: evaluate constraint Jacobian-vector product
* `hess(x[, v]) <methods/pycutest.CUTEstProblem.hess.html>`_: evaluate Hessian of objective or Lagrangian
* `ihess(x[, cons_index]) <methods/pycutest.CUTEstProblem.ihess.html>`_: evaluate Hessian of objective or a specific constraint
* `hprod(p[, x, v]) <methods/pycutest.CUTEstProblem.hprod.html>`_: evaluate Hessian-vector product (for objective or Lagrangian)
* `gradhess(x[, v, gradient_of_lagrangian]) <methods/pycutest.CUTEstProblem.gradhess.html>`_: evaluate gradient of objective/Lagrangian, Jacobian of constraints and Hessian of objective/Lagrangian
* `report() <methods/pycutest.CUTEstProblem.report.html>`_: return a dictionary of statistics (number of objective/gradient evaluations, etc.)

For large-scale problems, you may want to get vectors/matrices as sparse matrices. We have the following methods which return sparse matrices:

* `sobj(x[, gradient]) <methods/pycutest.CUTEstProblem.sobj.html>`_: (sparse) evaluate objective (and optionally its gradient)
* `sgrad(x[, index]) <methods/pycutest.CUTEstProblem.sgrad.html>`_: (sparse) evaluate objective gradient or specific constraint gradient
* `scons(x[, index, gradient]) <methods/pycutest.CUTEstProblem.scons.html>`_: (sparse) evaluate constraint(s) and optionally their Jacobian/its gradient
* `slagjac(x[, v]) <methods/pycutest.CUTEstProblem.slagjac.html>`_: (sparse) evaluate gradient of objective/Lagrangian and Jacobian of constraints
* `sphess(x[, v]) <methods/pycutest.CUTEstProblem.sphess.html>`_: (sparse) evaluate Hessian of objective or Lagrangian
* `isphess(x[, cons_index]) <methods/pycutest.CUTEstProblem.isphess.html>`_: (sparse) evaluate Hessian of objective or a specific constraint 
* `gradsphess(x[, v, gradient_of_lagrangian]) <methods/pycutest.CUTEstProblem.gradsphess.html>`_: (sparse) evaluate gradient of objective/Lagrangian, Jacobian of constraints and Hessian of objective/Lagrangian 

Full documentation for each method above is given by clicking on it.

Problem Attributes
------------------

Each :code:`CUTEstProblem` instance has the following attributes:

* :code:`name`: CUTEst problem name (string)
* :code:`n`: number of variables (equal to :code:`n_free` if :code:`drop_fixed_variables=True`, otherwise :code:`n_full`)
* :code:`m`: number of constraints
* :code:`x0`: starting point for optimization routine (NumPy array of shape :code:`(n,)`)
* :code:`sifParams`: dict of parameters passed to sifdecode
* :code:`sifOptions`: list of extra options passed to sifdecode
* :code:`vartype`: array of variable types (NumPy array size n, entry :code:`vartype[i]` indicates that x[i] is real(0), boolean(1), or integer(2))
* :code:`nnzh`: number of nonzero entries in upper triangular part of objective Hessian (for all variables, including fixed)
* :code:`nonlinear_vars_first`: flag if all nonlinear variables are listed before linear variables
* :code:`bl`: array of lower bounds on input (unconstrained -> -1e20), as NumPy array of shape :code:`(n,)`
* :code:`bu`: array of upper bounds on input (unconstrained -> 1e20), as NumPy array of shape :code:`(n,)`
* :code:`n_full`: total number of variables in CUTEst problem (:code:`n_free + n_fixed`)
* :code:`n_free`: number of free variables
* :code:`n_fixed`: number of fixed variables

For constrained problems, we also have (these are all set to :code:`None` for unconstrained problems):

* :code:`eq_cons_first`: flag if equality constraints are listed before inequality constraints
* :code:`linear_cons_first`: flag if linear constraints are listed before nonlinear constraints
* :code:`nnzj`: number of nonzero entries in constraint Jacobian (for all variables, including fixed)
* :code:`v0`: starting point for Lagrange multipliers (NumPy array of shape :code:`(m,)`)
* :code:`cl`: lower bounds on constraints, as NumPy array of shape :code:`(m,)`
* :code:`cu`: upper bounds on constraints, as NumPy array of shape :code:`(m,)`
* :code:`is_eq_cons`: NumPy array of Boolean flags indicating if i-th constraint is equality or not (i.e. inequality)
* :code:`is_linear_cons`: NumPy array of Boolean flags indicating if i-th constraint is linear or not (i.e. nonlinear)

Full method documentation
---------------------------

Please click on a :code:`CUTEstProblem` method below for full documentation:

.. currentmodule:: pycutest.CUTEstProblem

.. autosummary::
   :toctree: methods
   :template: method.rst

   obj 
   grad 
   objcons 
   cons 
   lag 
   lagjac 
   jprod 
   hess 
   ihess 
   hprod 
   gradhess 
   report 
   sobj 
   sgrad 
   scons 
   slagjac 
   sphess 
   isphess 
   gradsphess 
