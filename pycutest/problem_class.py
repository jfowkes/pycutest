"""
A class to store problem info, where we can set up the interface exactly how we wish
"""

import numpy as np
from scipy.sparse import coo_matrix

__all__ = ['CUTEstProblem']

def pad_vector(x, idx_free, idx_eq, val_eq):
    # Pad a vector x using values from val_eq (i.e. fixed variables)
    xfull = np.zeros((len(idx_free) + len(idx_eq),))
    xfull[idx_free] = x
    xfull[idx_eq] = val_eq[idx_eq]
    return xfull


def sparse_vec_extract_indices(v, idx):
    # Return v[idx] where v is scipy.sparse.coo_matrix; want to return a coo_matrix too
    return (v.tocsc()[0, idx]).tocoo()


def sparse_mat_extract_columns(A, idx):
    # Return A[:, idx] where A is scipy.sparse.coo_matrix; want to return a coo_matrix too
    return (A.tocsc()[:, idx]).tocoo()


def sparse_mat_extract_rows(A, idx):
    # Return A[idx, :] where A is scipy.sparse.coo_matrix; want to return a coo_matrix too
    return (A.tocsc()[idx, :]).tocoo()


def sparse_mat_extract_rows_and_columns(A, row_idx, col_idx):
    # Return A[row_idx, col_idx] where A is scipy.sparse.coo_matrix; want to return a coo_matrix too
    return ((A.tocsc()[:, col_idx]).tocsr()[row_idx, :]).tocoo()


class CUTEstProblem(object):
    # CUTEstProblem instances
    _instances = {}

    def __new__(cls, module, instname, drop_fixed_variables=True):
        """
        Create new CUTEstProblem instance or return existing one if present,
        ensuring that CUTEST_[u|c]setup is only called once on the C module.

        We consider a CUTEstProblem to be the same instance if it has the same
        name and parameters, e.g. ARGLALE_N10 here called 'instname'.
        """
        # Check if CUTEstProblem instance already exists
        if instname not in cls._instances:
            module.info = module.setup() # setup CUTEst problem
            cls._instances[instname] = object.__new__(cls)
        return cls._instances[instname]

    def __init__(self, module, instname, drop_fixed_variables=True):
        """
        Build a wrapper for a Python module containing the compiled CUTEst problem.

        The resulting object has the following fields:

        * problem.name: CUTEst problem name (string)
        * problem.n: number of variables (equal to problem.n_free if drop_fixed_variables=True, otherwise problem.n_full)
        * problem.m: number of constraints
        * problem.x0: starting point for optimization routine (NumPy array of shape (problem.n,))
        * problem.sifParams: dict of parameters passed to sifdecode
        * problem.sifOptions: list of extra options passed to sifdecode
        * problem.vartype: array of variable types (NumPy array size n, entry vartype[i] indicates that x[i] is real(0), boolean(1), or integer(2))
        * problem.nnzh: number of nonzero entries in upper triangular part of objective Hessian (for all variables, including fixed)
        * problem.nonlinear_vars_first: flag if all nonlinear variables are listed before linear variables
        * problem.bl: array of lower bounds on input (unconstrained -> -1e20), as NumPy array of shape (problem.n,)
        * problem.bu: array of upper bounds on input (unconstrained -> 1e20), as NumPy array of shape (problem.n,)
        * problem.n_full: total number of variables in CUTEst problem (n_free + n_fixed)
        * problem.n_free: number of free variables
        * problem.n_fixed: number of fixed variables

        For constrained problems, we also have (these are all set to None for unconstrained problems):

        * problem.eq_cons_first: flag if equality constraints are listed before inequality constraints
        * problem.linear_cons_first: flag if linear constraints are listed before nonlinear constraints
        * problem.nnzj: number of nonzero entries in constraint Jacobian (for all variables, including fixed)
        * problem.v0: starting point for Lagrange multipliers (NumPy array of shape (problem.m,))
        * problem.cl: lower bounds on constraints, as NumPy array of shape (problem.m,)
        * problem.cu: upper bounds on constraints, as NumPy array of shape (problem.m,)
        * problem.is_eq_cons: NumPy array of Boolean flags indicating if i-th constraint is equality or not (i.e. inequality)
        * problem.is_linear_cons: NumPy array of Boolean flags indicating if i-th constraint is linear or not (i.e. nonlinear)

        :param module: the module containing the Python interface
        :param drop_fixed_variables: a flag for whether to ignore fixed variables (i.e. n is smaller, etc.) [default=True]
        """
        self._instname = instname
        self._module = module
        self.drop_fixed_vars = drop_fixed_variables

        # Extract useful problem info

        self.name = self._module.info['name']
        """ CUTEst problem name (string) """

        self.n = self._module.info['n']
        """ number of variables (equal to self.n_free if drop_fixed_variables=True, otherwise self.n_full) """

        self.m = self._module.info['m']
        """ number of constraints """

        self.x0 = self._module.info['x']
        """ starting point for optimization routine (NumPy array of shape (self.n,)) """

        self.sifParams = self._module.info['sifparams']
        """ dict of parameters passed to sifdecode """

        self.sifOptions = self._module.info['sifoptions']
        """ list of extra options passed to sifdecode """

        self.vartype = self._module.info['vartype']
        """ array of variable types (NumPy array size n, entry vartype[i] indicates that x[i] is real(0), boolean(1), or integer(2)) """

        self.nnzh = self._module.info['nnzh']
        """ number of nonzero entries in upper triangular part of objective Hessian (for all variables, including fixed) """

        self.eq_cons_first = self._module.info['efirst'] if self.m > 0 else None
        """ flag if equality constraints are listed before inequality constraints, None for unconstrained problems """

        self.linear_cons_first = self._module.info['lfirst'] if self.m > 0 else None
        """ flag if linear constraints are listed before nonlinear constraints, None for unconstrained problems """

        self.nonlinear_vars_first = self._module.info['nvfirst']
        """ flag if all nonlinear variables are listed before linear variables """

        self.bl = self._module.info['bl']
        """ array of lower bounds on input (unconstrained -> -1e20), as NumPy array of shape (self.n,) """

        self.bu = self._module.info['bu']
        """ array of upper bounds on input (unconstrained -> 1e20), as NumPy array of shape (self.n,) """

        self.nnzj = self._module.info['nnzj'] if self.m > 0 else None
        """ number of nonzero entries in constraint Jacobian (for all variables, including fixed), None for unconstrained problems """

        self.v0 = self._module.info['v'] if self.m > 0 else None
        """ starting point for Lagrange multipliers (NumPy array of shape (self.m,)), None for unconstrained problems """

        self.cl = self._module.info['cl'] if self.m > 0 else None
        """ lower bounds on constraints, as NumPy array of shape (self.m,), None for unconstrained problems """

        self.cu = self._module.info['cu'] if self.m > 0 else None
        """ upper bounds on constraints, as NumPy array of shape (self.m,), None for unconstrained problems """

        self.is_eq_cons = self._module.info['equatn'] if self.m > 0 else None
        """ NumPy array of Boolean flags indicating if i-th constraint is equality or not (i.e. inequality), None for unconstrained problems """

        self.is_linear_cons = self._module.info['linear'] if self.m > 0 else None
        """ NumPy array of Boolean flags indicating if i-th constraint is linear or not (i.e. nonlinear), None for unconstrained problems """

        # Extract fixed/free variables
        self.idx_eq = np.where(self.bu - self.bl <= 1e-15)[0]  # indices of fixed variables
        self.idx_free = np.setdiff1d(np.arange(self.n), self.idx_eq)  # indices of free variables

        # Remove fixed variables from parameter info
        self.bl_full = self.bl.copy()  # for fixed values in self.free_to_all()

        self.n_full = self.n
        """ total number of variables in CUTEst problem (n_free + n_fixed) """

        self.n_fixed = len(self.idx_eq)
        """ number of fixed variables """

        self.n_free = len(self.idx_free)
        """ number of free variables """

        if self.drop_fixed_vars:
            self.x0 = self.all_to_free(self.x0)
            self.bl = self.all_to_free(self.bl)
            self.bu = self.all_to_free(self.bu)
            self.n = self.n_free
            self.vartype = self.all_to_free(self.vartype)
            # Not updating self.nnzh and self.nnzj, because even isphess doesn't give right results
        else:  # Doesn't matter whether they are actually fixed or free, they all look free to us
            self.idx_eq = np.array([], dtype=int)
            self.idx_free = np.arange(self.n, dtype=int)
            self.n_fixed = 0
            self.n_free = self.n_full
            self.n = self.n_full
            self.remove_one_isphess_and_scons = False

        # Save the initial stats, so we can make sure they don't get counted in the final tally
        self.init_stats = self._module.report()

    def __str__(self):
        if self.sifParams is None:
            return "CUTEst problem %s (default params) with %g variables and %g constraints" % (self.name, self.n, self.m)
        else:
            return "CUTEst problem %s (params %s) with %g variables and %g constraints" % (self.name, str(self.sifParams), self.n, self.m)

    def all_to_free(self, x):
        """
        Remove fixed variables from a vector of all variables.

        :param x: vector of values of all variables
        :return: vector of free variables only
        """
        if self.drop_fixed_vars:
            return x[self.idx_free]
        else:
            return x

    def free_to_all(self, x, use_zeros=False):
        """
        Append fixed variables to a vector of free variables.

        :param x: vector of values of free variables
        :param use_zeros: If True, pad with zeros, otherwise with fixed values of input vector
        :return: vector of values of all variables
        """
        if self.drop_fixed_vars:
            return pad_vector(x, self.idx_free, self.idx_eq, np.zeros((self.n_full,)) if use_zeros else self.bl_full)
        else:
            return x

    def check_input_x(self, x):
        """
        Check x has correct dimensions

        :param x: input vector
        :return: raises RuntimeError if x has wrong dimension
        """
        if x.shape != (self.n,):
            raise RuntimeError("x has wrong shape (got %s, expect (%g,))" % (x.shape, self.n))
        return

    def check_input_v(self, v):
        """
        Check v (Lagrange multiplier) has correct dimensions (or None for unconstrained problems)

        :param v: input vector
        :return: raises RuntimeError if v has wrong dimension
        """
        if self.m <= 0:
            if v is not None:
                raise RuntimeError("Lagrange multipliers should not be specified for unconstrained problems")
        elif v.shape != (self.m,):
            raise RuntimeError("v has wrong shape (got %s, expect (%g,))" % (v.shape, self.m))
        return

    def varnames(self):
        """
        Get names of variables (note: ordering depends on self.nonlinear_vars_first).

        :return: a list of strings representing the names of problem's variables (including fixed variables)
        """
        return self._module.varnames()

    def connames(self):
        """
        Get names of constraints (note: ordering depends on self.linear_cons_first and self.nonlinear_vars_first).

        :return: a list of strings representing the names of problem constraints
        """
        return self._module.connames()

    def objcons(self, x):
        """
        Evaluate objective and constraints.

        .. code-block:: python

            # objective and constraints
            f, c = problem.objcons(x)

        For unconstrained problems, c is None.

        This calls CUTEst routine CUTEst_cfn.

        :param x: input vector
        :type x: numpy.ndarray with shape (n,)
        :return: tuple (f, c) of objective and constraint values at x for constrained problems.
        :rtype: (float, numpy.ndarray(m,))
        """
        self.check_input_x(x)
        f, c = self._module.objcons(self.free_to_all(x))
        if len(c) == 0:  # unconstrained problems
            c = None
        return f, c

    def obj(self, x, gradient=False):
        """
        Evaluate the objective (and optionally its gradient).

        .. code-block:: python

            # objective
            f    = problem.obj(x)
            # objective and gradient
            f, g = problem.obj(x, gradient=True)

        This calls CUTEst routine CUTEST_uofg or CUTEST_cofg.

        :param x: input vector
        :type x: numpy.ndarray with shape (n,)
        :param gradient: whether to return objective and gradient, or just objective (default=False; i.e. objective only)
        :type gradient: bool, optional
        :return: objective value f, or tuple (f,g) of objective and gradient at x
        :rtype: float or (float, numpy.ndarray(n,))
        """
        self.check_input_x(x)
        if gradient:
            f, g = self._module.obj(self.free_to_all(x), 1)
            return f, self.all_to_free(g)
        else:
            f = self._module.obj(self.free_to_all(x))
            return f

    def cons(self, x, index=None, gradient=False):
        """
        Evaluate the constraints (and optionally their Jacobian or gradient).

        .. code-block:: python

            # constraint vector
            c      = problem.cons(x)
            # i-th constraint
            ci     = problem.cons(x, index=i)
            # constraints and Jacobian
            c, J   = problem.cons(x, gradient=True)
            # i-th constraint and its gradient
            ci, Ji = problem.cons(x, index=i, gradient=True)

        For unconstrained problems, this returns None.

        This calls CUTEst routine CUTEST_ccfg or CUTEST_ccifg.

        For large problems, problem.scons returns sparse matrices.

        :param x: input vector
        :type x: numpy.ndarray with shape (n,)
        :param index: which constraint to evaluate (default=None -> all constraints). Must be in 0..self.m-1.
        :type index: int, optional
        :param gradient: whether to return constraint(s) and gradient/Jacobian, or just constraint (default=False; i.e. constraint only)
        :type gradient: bool, optional
        :return: value of constraint(s), and Jacobian or gradient of constraint(s) at x
        :rtype: numpy.ndarray(m,) or float or (numpy.ndarray(m,), numpy.ndarray(m,n)) or (float, numpy.ndarray(n,))
        """
        if self.m <= 0:
            return None
        self.check_input_x(x)
        if gradient:
            if index is None:
                c, J = self._module.cons(self.free_to_all(x), True)
                return c, J[:, self.idx_free]
            else:
                assert 0 <= index <= self.m - 1, "Invalid constraint index %g (must be in 0..%g)" % (index, self.m-1)
                ci, Ji = self._module.cons(self.free_to_all(x), True, index)
                ci = float(ci)  # convert from 1x1 NumPy array to float
                return ci, self.all_to_free(Ji)
        else:
            if index is None:
                c = self._module.cons(self.free_to_all(x))
                return c
            else:
                assert 0 <= index <= self.m - 1, "Invalid constraint index %g (must be in 0..%g)" % (index, self.m - 1)
                ci = self._module.cons(self.free_to_all(x), False, index)
                ci = float(ci)  # convert from 1x1 NumPy array to float
                return ci

    def lagjac(self, x, v=None):
        """
        Evaluate gradient of objective or Lagrangian, and Jacobian of constraints.

        .. code-block:: python

            # objective gradient and the Jacobian of constraints
            g, J = problem.lagjac(x)
            # Lagrangian gradient and the Jacobian of constraints
            g, J = problem.lagjac(x, v=v)

        For unconstrained problems, J is None.

        For large problems, problem.slagjac returns sparse matrices.

        This calls CUTEst routine CUTEST_cgr.

        Note: in CUTEst, the sign convention is such that the Lagrangian = objective + lagrange_multipliers * constraints

        :param x: input vector
        :type x: numpy.ndarray with shape (n,)
        :param v: input vector of Lagrange multipliers
        :type v: numpy.ndarray with shape (m,), optional
        :return: gradient of objective or Lagrangian, and Jacobian of constraints
        :rtype: (numpy.ndarray(n,), numpy.ndarray(m,n))
        """
        self.check_input_x(x)
        if v is None:
            g, J = self._module.lagjac(self.free_to_all(x))
        else:
            self.check_input_v(v)
            g, J = self._module.lagjac(self.free_to_all(x), v)
        if self.m > 0:
            return self.all_to_free(g), J[:, self.idx_free]
        else:
            return self.all_to_free(g), None

    def jprod(self, p, transpose=False, x=None):
        """
        Evaluate product of constraint Jacobian with a vector p

        .. code-block:: python

            # evaluate J*p where J is the last computed Jacobian
            r = problem.jprod(p)
            # evaluate J.T*p where J is the last computed Jacobian
            r = problem.jprod(p, transpose=True)
            # evaluate Jacobian at x, and return J(x)*p
            r = problem.jprod(p, x=x)
            # evaluate Jacobian at x, and return J(x).T*p
            r = problem.jprod(p, transpose=True, x=x)

        For unconstrained problems, r is None.

        This calls CUTEst routine CUTEST_cjprod.

        :param p: vector to be multiplied by the Jacobian of constraints
        :type p: numpy.ndarray with shape (n,) or (m,) if transpose=True
        :param transpose: if True, multiply by transpose of Jacobian (J.T*p)
        :type transpose: bool, optional
        :param x: input vector for Jacobian (default=None -> use last computed Jacobian)
        :type x: numpy.ndarray with shape (n,), optional
        :return: Jacobian-vector product J(x)*p or J(x).T*p if transpose=True
        :rtype: numpy.ndarray(m,) or numpy.ndarray(n,) if transpose=True
        """
        if self.m <= 0:
            return None
        if transpose:
            self.check_input_v(p)
        else:
            self.check_input_x(p)
        if x is None:
            r = self._module.jprod(transpose, p if transpose else self.free_to_all(p, use_zeros=True))
        else:
            self.check_input_x(x)
            r = self._module.jprod(transpose, p if transpose else self.free_to_all(p, use_zeros=True), self.free_to_all(x))
        return self.all_to_free(r) if transpose else r

    def hess(self, x, v=None):
        """
        Evaluate the Hessian of the objective or Lagrangian.
        For constrained problems, the Hessian is L_{x,x}(x,v).

        .. code-block:: python

            # Hessian of objective at x for unconstrained problems
            H = problem.hess(x)
            # Hessian of Lagrangian at (x, v) for constrained problems
            H = problem.hess(x, v=v)

        For unconstrained problems, v must be None.
        For constrained problems, v must be specified.
        To evaluate the Hessian of the objective for constrained problems use ihess()

        For large problems, problem.sphess returns sparse matrices.

        This calls CUTEst routine CUTEST_cdh or CUTEST_udh.

        Note: in CUTEst, the sign convention is such that the Lagrangian = objective + lagrange_multipliers * constraints

        :param x: input vector
        :type x: numpy.ndarray with shape (n,)
        :param v: vector of Lagrange multipliers (must be specified for constrained problems)
        :type v: numpy.ndarray with shape (m,), optional
        :return: Hessian of objective (unconstrained) or Lagrangian (constrained) at x
        :rtype: numpy.ndarray(n,n)
        """
        self.check_input_x(x)
        if self.m > 0:
            assert v is not None, "CUTEstProblem.hess: v must be specified for constrained problems. For the objective Hessian, use problem.ihess(x)"
            self.check_input_v(v)
            H = self._module.hess(self.free_to_all(x), v)
        else:
            assert v is None, "CUTEstProblem.hess: v must be None for unconstrained problems"
            H = self._module.hess(self.free_to_all(x))
        # 2d indexing with lists is a bit strange in Python
        # https://stackoverflow.com/questions/4257394/slicing-of-a-numpy-2d-array-or-how-do-i-extract-an-mxm-submatrix-from-an-nxn-ar
        return H[self.idx_free][:, self.idx_free]

    def ihess(self, x, cons_index=None):
        """
        Evaluate the Hessian of the objective or the i-th constraint.

        .. code-block:: python

            # Hessian of the objective
            H = problem.ihess(x)
            # Hessian of i-th constraint
            H = problem.ihess(x, cons_index=i)

        For large problems, problem.isphess returns sparse matrices.

        This calls CUTEst routine CUTEST_cidh or CUTEST_udh.

        :param x: input vector
        :type x: numpy.ndarray with shape (n,)
        :param cons_index: index of constraint (default is None -> use objective). Must be in 0..self.m-1.
        :type cons_index: int, optional
        :return: Hessian of objective or a single constraint at x
        :rtype: numpy.ndarray(n,n)
        """
        self.check_input_x(x)
        if cons_index is None:
            H = self._module.ihess(self.free_to_all(x))
        else:
            assert 0 <= cons_index <= self.m - 1, "Invalid constraint index %g (must be in 0..%g)" % (cons_index, self.m - 1)
            H = self._module.ihess(self.free_to_all(x), cons_index)
        return H[self.idx_free][:, self.idx_free]

    def hprod(self, p, x=None, v=None):
        """
        Calculate Hessian-vector product H*p, where H is Hessian of objective (unconstrained) or Lagrangian (constrained).
        For constrained problems, the Hessian is L_{x,x}(x,v).

        .. code-block:: python

            # use last computed Hessian to compute H*p
            r = problem.hprod(p)
            # use Hessian of Lagrangian L_{x,x}(x,v) to compute H*p (constrained only)
            r = problem.hprod(p, x=x, v=v)
            # use Hessian of objective at x to compute H*p (unconstrained only)
            r = problem.hprod(p, x=x)

        For unconstrained problems, v must be None.
        For constrained problems, v must be specified.

        This calls CUTEst routine CUTEST_chprod or CUTEST_uhprod

        Note: in CUTEst, the sign convention is such that the Lagrangian = objective + lagrange_multipliers * constraints

        :param p: vector to be multiplied by the Hessian
        :type p: numpy.ndarray with shape (n,)
        :param x: input vector for the Hessian
        :type x: numpy.ndarray with shape (n,), optional
        :param v: vector of Lagrange multipliers (must be specified for constrained problems)
        :type v: numpy.ndarray with shape (m,), optional
        :return: Hessian-vector product H*p
        :rtype: numpy.ndarray(n,)
        """
        self.check_input_x(p)
        if self.m > 0:
            if x is not None:
                self.check_input_x(x)
                self.check_input_v(v)
                r = self._module.hprod(self.free_to_all(p, use_zeros=True), self.free_to_all(x), v)
            else:
                r = self._module.hprod(self.free_to_all(p, use_zeros=True))
        else:
            self.check_input_v(v)
            if x is not None:
                self.check_input_x(x)
                r = self._module.hprod(self.free_to_all(p, use_zeros=True), self.free_to_all(x))
            else:
                r = self._module.hprod(self.free_to_all(p, use_zeros=True))
        return r[self.idx_free]

    def gradhess(self, x, v=None, gradient_of_lagrangian=True):
        """
        Evaluate the gradient of objective or Lagrangian, Jacobian of constraints, and Hessian of objective or Lagrangian.
        For constrained problems, the gradient is L_{x}(x,v) and the Hessian is L_{x,x}(x,v).

        .. code-block:: python

            # for unconstrained problems
            g, H    = problem.gradhess(x)
            # for constrained problems (g = grad Lagrangian)
            g, J, H = problem.gradhess(x, v=v)
            # for constrained problems (g = grad objective)
            g, J, H = problem.gradhess(x, v=v, gradient_of_lagrangian=False)

        For constrained problems, v must be specified, and the Hessian of the Lagrangian is always returned.
        For Hessian of the objective, use problem.ihess().

        For large problems, problem.gradsphess returns sparse matrices.

        This calls CUTEst routine CUTEST_cgrdh or CUTEST_ugrdh.

        Note: in CUTEst, the sign convention is such that the Lagrangian = objective + lagrange_multipliers * constraints

        :param x: input vector
        :type x: numpy.ndarray with shape (n,)
        :param v: vector of Lagrange multipliers (must be specified for constrained problems)
        :type v: numpy.ndarray with shape (m,), optional
        :param gradient_of_lagrangian: for constrained problems, return gradient of objective or Lagrangian?
        :type gradient_of_lagrangian: bool, optional
        :return: gradient of objective or Lagrangian, (Jacobian of constraints), and Hessian of objective or Lagrangian at x
        :rtype: (numpy.ndarray(n,), numpy.ndarray(n,n)) or (numpy.ndarray(n,), numpy.ndarray(m,n), numpy.ndarray(n,n))
        """
        self.check_input_x(x)
        self.check_input_v(v)
        if self.m > 0:
            g, J, H = self._module.gradhess(self.free_to_all(x), v, gradient_of_lagrangian)
            return self.all_to_free(g), J[:, self.idx_free], H[self.idx_free][:, self.idx_free]
        else:
            g, H = self._module.gradhess(self.free_to_all(x))
            return self.all_to_free(g), H[self.idx_free][:, self.idx_free]

    # scons() wrapper (private)
    def __scons(self, x, i=None):
        """Returns the value of constraints and
        the sparse Jacobian of constraints at x.

        (c, J)=__scons(x)      -- Jacobian of constraints
        (ci, gi)=__scons(x, i) -- i-th constraint and its gradient

        Input
        x -- 1D array of length n with the values of variables
        i -- integer index of constraint (between 0 and m-1)

        Output
        c  -- 1D array of length m holding the values of constraints at x
        J  -- a scipy.sparse.coo_matrix of size m-by-n holding the Jacobian at x
        ci -- 1D array of length 1 holding the value of i-th constraint at x
        gi -- a scipy.sparse.coo_matrix of size 1-by-n holding the gradient of i-th constraint at x

        This function is a wrapper for scons().
        """

        if i is None:
            (c, Ji, Jif, Jv)=self._module.scons(x)
            return (c, coo_matrix((Jv, (Jif, Ji)), shape=(self.m, self.n)))
        else:
            (c, gi, gv)=self._module.scons(x, i)
            return (c, coo_matrix((gv, (np.zeros(len(gv)), gi)), shape=(1, self.n)))

    def scons(self, x, index=None, gradient=False):
        """
        Evaluate the constraints (and optionally their sparse Jacobian or gradient).

        .. code-block:: python

            # constraints
            c      = problem.scons(x)
            # i-th constraint
            ci     = problem.scons(x, index=i)
            # constraints and sparse Jacobian
            c, J   = problem.scons(x, gradient=True)
            # i-th constraint and its sparse gradient
            ci, Ji = problem.scons(x, index=i, gradient=True)

        The matrix J or vector Ji is of type scipy.sparse.coo_matrix.

        For unconstrained problems, this returns None.

        For small problems, problem.cons returns dense matrices.

        This calls CUTEst routine CUTEST_ccfsg or CUTEST_ccifsg.

        :param x: input vector
        :type x: numpy.ndarray with shape (n,)
        :param index: which constraint to evaluate (default=None -> all constraints). Must be in 0..self.m-1.
        :type index: int, optional
        :param gradient: whether to return constraint(s) and gradient/Jacobian, or just constraint (default=False; i.e. constraint only)
        :type gradient: bool, optional
        :return: value of constraint(s), and sparse Jacobian or gradient of constraint(s) at x
        :rtype: numpy.ndarray(m,) or float or (numpy.ndarray(m,), scipy.sparse.coo_matrix(m,n)) or (float, scipy.sparse.coo_matrix(n,))
        """
        if self.m <= 0:
            return None
        self.check_input_x(x)
        if index is None:
            c, J = self.__scons(self.free_to_all(x))
            if gradient:
                return c, sparse_mat_extract_columns(J, self.idx_free)
            else:
                return c
        else:
            assert 0 <= index <= self.m - 1, "Invalid constraint index %g (must be in 0..%g)" % (index, self.m - 1)
            ci, Ji = self.__scons(self.free_to_all(x), index)
            ci = float(ci)  # convert from 1x1 NumPy array to float
            if gradient:
                return ci, sparse_vec_extract_indices(Ji, self.idx_free)
            else:
                return ci

    # slagjac() wrapper
    def __slagjac(self, x, v=None):
        """Returns the sparse gradient of objective at x or Lagrangian at (x, v),
        and the sparse Jacobian of constraints at x.

        (g, J)=__slagjac(x)    -- objective gradient and Jacobian
        (g, J)=__slagjac(x, v) -- Lagrangian gradient and Jacobian

        Input
        x -- 1D array of length n with the values of variables
        v -- 1D array of length m with the values of Lagrange multipliers

        Output
        g -- a scipy.sparse.coo_matrix of size 1-by-n holding the gradient of objective at x or
            the gradient of Lagrangian at (x, v)
        J -- a scipy.sparse.coo_matrix of size m-by-n holding the sparse Jacobian
            of constraints at x

        This function is a wrapper for slagjac().
        """

        if v is None:
            (gi, gv, Ji, Jfi, Jv)=self._module.slagjac(x)
        else:
            (gi, gv, Ji, Jfi, Jv)=self._module.slagjac(x, v)
        return (
            coo_matrix((gv, (np.zeros(len(gv)), gi)), shape=(1, self.n)),
            coo_matrix((Jv, (Jfi, Ji)), shape=(self.m, self.n))
        )

    def slagjac(self, x, v=None):
        """
        Evaluate sparse gradient of objective or Lagrangian, and sparse Jacobian of constraints.

        .. code-block:: python

            # objective gradient and Jacobian
            g, J = problem.slagjac(x)
            # Lagrangian gradient and Jacobian
            g, J = problem.slagjac(x, v=v)

        The vector g and matrix J are of type scipy.sparse.coo_matrix.

        For unconstrained problems, J is None.

        For small problems, problem.lagjac returns dense matrices.

        This calls CUTEst routine CUTEST_csgr.

        Note: in CUTEst, the sign convention is such that the Lagrangian = objective + lagrange_multipliers * constraints

        :param x: input vector
        :type x: numpy.ndarray with shape (n,)
        :param v: vector of Lagrange multipliers
        :type v: numpy.ndarray with shape (m,), optional
        :return: sparse gradient of objective or Lagrangian, and sparse Jacobian of constraints
        :rtype: (scipy.sparse.coo_matrix(n,), scipy.sparse.coo_matrix(m,n))
        """
        self.check_input_x(x)
        if v is None:
            g, J = self.__slagjac(self.free_to_all(x))
        else:
            self.check_input_v(v)
            g, J = self.__slagjac(self.free_to_all(x), v)
        if self.m > 0:
            return sparse_vec_extract_indices(g, self.idx_free), sparse_mat_extract_columns(J, self.idx_free)
        else:
            return sparse_vec_extract_indices(g, self.idx_free), None

    # sphess() wrapper (private)
    def __sphess(self, x, v=None):
        """Returns the sparse Hessian of the objective at x (unconstrained problems)
        or the sparse Hessian of the Lagrangian (constrained problems) at (x, v).

        H=__sphess(x)    -- Hessian of objective (unconstrained problems)
        H=__sphess(x, v) -- Hessian of Lagrangian (constrained problems)

        Input
        x -- 1D array of length n with the values of variables
        v -- 1D array of length m with the values of Lagrange multipliers

        Output
        H -- a scipy.sparse.coo_matrix of size n-by-n holding the sparse Hessian
            of objective at x or the sparse Hessian of the Lagrangian at (x, v)

        This function is a wrapper for sphess().
        """

        if v is None:
            (Hi, Hj, Hv)=self._module.sphess(x)
        else:
            (Hi, Hj, Hv)=self._module.sphess(x, v)
        return coo_matrix((Hv, (Hi, Hj)), shape=(self.n, self.n))

    def sphess(self, x, v=None):
        """
        Evaluate sparse Hessian of objective or Lagrangian.
        For constrained problems, the Hessian is L_{x,x}(x,v).

        .. code-block:: python

            # Hessian of objective (unconstrained problems)
            H = problem.sphess(x)
            # Hessian of Lagrangian (constrained problems)
            H = problem.sphess(x, v)

        For unconstrained problems, v must be None.
        For constrained problems, v must be specified.
        To evaluate the Hessian of the objective for constrained problems use isphess()

        The matrix H is of type scipy.sparse.coo_matrix.

        For small problems, problem.hess returns dense matrices.

        This calls CUTEst routine CUTEST_csh or CUTEST_ush.

        Note: in CUTEst, the sign convention is such that the Lagrangian = objective + lagrange_multipliers * constraints

        :param x: input vector
        :type x: numpy.ndarray with shape (n,)
        :param v: vector of Lagrange multipliers (must be specified for constrained problems)
        :type v: numpy.ndarray with shape (m,), optional
        :return: sparse Hessian of objective (unconstrained) or Lagrangian (constrained) at x
        :rtype: scipy.sparse.coo_matrix(n,n)
        """
        self.check_input_x(x)
        if self.m > 0:
            assert v is not None, "CUTEstProblem.sphess: v must be specified for constrained problems. For the objective Hessian, use problem.isphess(x)"
            self.check_input_v(v)
            H = self.__sphess(self.free_to_all(x), v)
        else:
            assert v is None, "CUTEstProblem.sphess: v must be None for unconstrained problems"
            H = self.__sphess(self.free_to_all(x), v)
        return sparse_mat_extract_rows_and_columns(H, self.idx_free, self.idx_free)

    # isphess() wrapper (private)
    def __isphess(self, x, i=None):
        """Returns the sparse Hessian of the objective or the sparse Hessian of i-th
        constraint at x.

        H=__isphess(x)    -- Hessian of objective
        H=__isphess(x, i) -- Hessian of i-th constraint

        Input
        x -- 1D array of length n with the values of variables
        i -- integer holding the index of constraint (between 0 and m-1)

        Output
        H -- a scipy.sparse.coo_matrix of size n-by-n holding the sparse Hessian
            of objective or the sparse Hessian i-th constraint at x

        This function is a wrapper for isphess().
        """

        if i is None:
            (Hi, Hj, Hv)=self._module.isphess(x)
        else:
            (Hi, Hj, Hv)=self._module.isphess(x, i)
        return coo_matrix((Hv, (Hi, Hj)), shape=(self.n, self.n))

    def isphess(self, x, cons_index=None):
        """
        Evaluate the sparse Hessian of the objective or the i-th constraint.

        .. code-block:: python

            # Hessian of the objective
            H = problem.isphess(x)
            # Hessian of the i-th constraint
            H = problem.isphess(x, cons_index=i)

        The matrix H is of type scipy.sparse.coo_matrix.

        For small problems, problem.ihess returns dense matrices.

        This calls CUTEst routine CUTEST_cish or CUTEST_ush.

        :param x: input vector
        :type x: numpy.ndarray with shape (n,)
        :param cons_index: index of constraint (default is None -> use objective). Must be in 0..self.m-1.
        :type cons_index: int, optional
        :return: sparse Hessian of objective or a single constraint at x
        :rtype: scipy.sparse.coo_matrix(n,n)
        """
        self.check_input_x(x)
        if cons_index is None:
            H = self.__isphess(self.free_to_all(x))
        else:
            assert 0 <= cons_index <= self.m - 1, "Invalid constraint index %g (must be in 0..%g)" % (
            cons_index, self.m - 1)
            H = self.__isphess(self.free_to_all(x), cons_index)
        return sparse_mat_extract_rows_and_columns(H, self.idx_free, self.idx_free)

    # gradsphess() wrapper (private)
    def __gradsphess(self, x, v=None, lagrFlag=False):
        """Returns the sparse Hessian of the Lagrangian, the sparse Jacobian of
        constraints, and the gradient of the objective or Lagrangian.

        (g, H)=__gradsphess(x)              -- unconstrained problems
        (g, J, H)=__gradsphess(x, v, gradl) -- constrained problems

        Input
        x     -- 1D array of length n with the values of variables
        v     -- 1D array of length m with the values of Lagrange multipliers
        gradl -- boolean flag. If False the gradient of the objective is returned,
                if True the gradient of the Lagrangian is returned.
                Default is False

        Output
        g -- a scipy.sparse.coo_matrix of size 1-by-n holding the gradient of objective at x or
            the gradient of Lagrangian at (x, v)
        J -- a scipy.sparse.coo_matrix of size m-by-n holding the sparse Jacobian
            of constraints at x
        H -- a scipy.sparse.coo_matrix of size n-by-n holding the sparse Hessian
            of objective at x or the sparse Hessian of the Lagrangian at (x, v)

        This function is a wrapper for gradsphess().
        """

        if v is None:
            (g, Hi, Hj, Hv)=self._module.gradsphess(x)
            return (coo_matrix(g), coo_matrix((Hv, (Hi, Hj)), shape=(self.n, self.n)))
        else:
            (gi, gv, Ji, Jfi, Jv, Hi, Hj, Hv)=self._module.gradsphess(x, v, lagrFlag)
            return (
                coo_matrix((gv, (np.zeros(len(gv)), gi)), shape=(1, self.n)),
                coo_matrix((Jv, (Jfi, Ji)), shape=(self.m, self.n)),
                coo_matrix((Hv, (Hi, Hj)), shape=(self.n, self.n))
            )

    def gradsphess(self, x, v=None, gradient_of_lagrangian=True):
        """
        Evaluate the sparse gradient of objective or Lagrangian, sparse Jacobian of constraints, and sparse Hessian of objective or Lagrangian.
        For constrained problems, the gradient is L_{x}(x,v) and the Hessian is L_{x,x}(x,v).

        .. code-block:: python

            # For unconstrained problems
            g, H    = problem.gradsphess(x)
            # For constrained problem (g = grad Lagrangian)
            g, J, H = problem.gradsphess(x, v=v)
            # For constrained problems (g = grad objective)
            g, J, H = problem.gradsphess(x, v=v, gradient_of_lagrangian=False)

        For constrained problems, v must be specified, and the Hessian of the Lagrangian is always returned.
        For Hessian of the objective, use problem.ihess().

        The vector g and matrices J and H are of type scipy.sparse.coo_matrix.

        For small problems, problem.gradhess returns dense matrices.

        This calls CUTEst routine CUTEST_csgrsh or CUTEST_ugrsh.

        Note: in CUTEst, the sign convention is such that the Lagrangian = objective + lagrange_multipliers * constraints

        :param x: input vector
        :type x: numpy.ndarray with shape (n,)
        :param v: vector of Lagrange multipliers (must be specified for constrained problems)
        :type v: numpy.ndarray with shape (m,), optional
        :param gradient_of_lagrangian: for constrained problems, return gradient of objective or Lagrangian?
        :type gradient_of_lagrangian: bool, optional
        :return: sparse gradient of objective or Lagrangian, (sparse Jacobian of constraints), and sparse Hessian of objective or Lagrangian at x
        :rtype: (scipy.sparse.coo_matrix(n,), scipy.sparse.coo_matrix(n,n)) or (scipy.sparse.coo_matrix(n,), scipy.sparse.coo_matrix(m,n), scipy.sparse.coo_matrix(n,n)
        """
        self.check_input_x(x)
        self.check_input_v(v)
        if self.m > 0:
            g, J, H = self.__gradsphess(self.free_to_all(x), v, gradient_of_lagrangian)
            return sparse_vec_extract_indices(g, self.idx_free), \
                   sparse_mat_extract_columns(J, self.idx_free), \
                   sparse_mat_extract_rows_and_columns(H, self.idx_free, self.idx_free)
        else:
            g, H = self.__gradsphess(self.free_to_all(x))
            return sparse_vec_extract_indices(g, self.idx_free), sparse_mat_extract_rows_and_columns(H, self.idx_free, self.idx_free)

    def report(self):
        """
        Get CUTEst usage statistics.

        .. code-block:: python

            stats = problem.report()

        Statistics are:

        * f = number of objective evaluations
        * g = number of objective gradient evaluations
        * H = number of objective Hessian evaluations
        * Hprod = number of objective Hessian-vector products
        * tsetup = CPU time for setup
        * trun = CPU time for run

        and for constrained problems, also

        * c = number of constraint evaluations (None for unconstrained)
        * cg = number of constraint gradient evaluations (None for unconstrained)
        * cH = number of constraint Hessian evaluations (None for unconstrained)

        This calls CUTEst routine CUTEST_creport or CUTEST_ureport.

        :return: dict of usage statistics
        """
        stats = self._module.report()
        # Remove any counts that were there when we initialised the object
        for s in ['f', 'g', 'H', 'Hprod']:
            stats[s] = stats[s] - self.init_stats[s]
        if self.m <= 0:
            stats['c'] = None
            stats['cg'] = None
            stats['cH'] = None
        else:
            for s in ['c', 'cg', 'cH']:
                stats[s] = stats[s] - self.init_stats[s]

        return stats

    def __del__(self):
        """
        Delete CUTEstProblem instance and clear CUTEst problem memory.
        """
        del self._instances[self._instname]
        self._module.terminate()

