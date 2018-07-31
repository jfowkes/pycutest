"""
A class to store problem info, where we can set up the interface exactly how we wish
"""

# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np

__all__ = ['CUTEstProblem']


def pad_vector(x, idx_free, idx_eq, val_eq):
    # Pad a vector x using values from val_eq (i.e. fixed variables)
    xfull = np.zeros((len(idx_free) + len(idx_eq),))
    xfull[idx_free] = x
    xfull[idx_eq] = val_eq[idx_eq]
    return xfull


def sparse_vec_extract_indices(v, idx):
    # Return v[idx] where v is scipy.sparse.coo_matrix; want to return a coo_matrix too
    return (v.tocsc()[idx]).tocoo()


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
    def __init__(self, module, drop_fixed_variables=True):
        """
        Build a wrapper for a Python module containing the compiled CUTEst problem.

        :param module: the module containing the Python interface
        """
        self._module = module
        self.drop_fixed_vars = drop_fixed_variables

        # Extract useful problem info
        self.name = self._module.info['name']
        self.n = self._module.info['n']  # number of variables
        self.m = self._module.info['m']  # number of constraints
        self.x0 = self._module.info['x']  # starting point
        self.sifParams = self._module.info['sifparams']  # SIF problem parameters
        self.sifOptions = self._module.info['sifoptions']  # sifdecoder options
        self.vartype = self._module.info['vartype']  # array of variable types (0=real, 1=boolean, 2=integer)
        self.nnzh = self._module.info['nnzh']  # number of nonzeros in upper triangular part of (sparse) Hessian, in all variables
        self.eq_cons_first = self._module.info['efirst'] if self.m > 0 else None  # if True, equality constraints are listed before inequality constraints
        self.linear_cons_first = self._module.info['lfirst'] if self.m > 0 else None  # if True, linear constraints are listed befor nonlinear constraints
        self.nonlinear_vars_first = self._module.info['nvfirst']  # if True, nonlinear variables listed before nonlinear variables
        self.bl = self._module.info['bl']  # lower bounds on x (-1e20 -> unconstrained)
        self.bu = self._module.info['bu']  # upper bounds on x (+1e20 -> unconstrained)
        self.nnzj = self._module.info['nnzj'] if self.m > 0 else None  # number of nonzeros in sparse Jacobian of constraints, in all variables
        self.v0 = self._module.info['v'] if self.m > 0 else None  # init vector of Lagrange multipliers
        self.cl = self._module.info['cl'] if self.m > 0 else None  # vector of lower bounds on constraint functions
        self.cu = self._module.info['cu'] if self.m > 0 else None  # vector of upper bounds on constraint functions
        self.is_eq_cons = self._module.info['equatn'] if self.m > 0 else None  # vector of Booleans if constraint i is equality
        self.is_linear_cons = self._module.info['linear'] if self.m > 0 else None  # vector of Booleans if constraint i is linear

        # Extract fixed/free variables
        self.idx_eq = np.where(self.bu - self.bl <= 1e-15)[0]  # indices of fixed variables
        self.idx_free = np.setdiff1d(np.arange(self.n), self.idx_eq)  # indices of free variables

        # Remove fixed variables from parameter info
        self.bl_full = self.bl.copy()  # for fixed values in self.free_to_all()
        self.n_full = self.n
        self.n_fixed = len(self.idx_eq)
        self.n_free = len(self.idx_free)
        if self.drop_fixed_vars:
            self.x0 = self.all_to_free(self.x0)
            self.bl = self.all_to_free(self.bl)
            self.bu = self.all_to_free(self.bu)
            self.n = self.n_free
            self.vartype = self.all_to_free(self.vartype)
            # Not updating self.nnzh and self.nnzj, because this would require 2 evaluations (messes up statistics)

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
            f, c = problem.objcons(x)  -- objective and constraints

        This calls CUTEst routine CUTEst_cfn.

        :param x: input vector
        :return: tuple (f, c) of objective and constraint values at x for constrained problems.
        """
        f, c = self._module.objcons(self.free_to_all(x))
        f = float(f)  # convert from 1x1 NumPy array to float
        return f, c

    def obj(self, x, gradient=False):
        """
        Evaluate the objective (and optionally its gradient).
            f    = problem.obj(x)                  -- objective
            f, g = problem.obj(x, gradient=True)  -- objective and gradient

        This calls CUTEst routine CUTEST_uofg or CUTEST_cofg.

        :param x: input vector
        :param gradient: whether to return objective and gradient, or just objective (default=False; i.e. objective only)
        :return: objective value f, or tuple (f,g) of objective and gradient at x
        """
        if gradient:
            f, g = self._module.obj(self.free_to_all(x), gradFlag=1)
            f = float(f)  # convert from 1x1 NumPy array to float
            return f, self.all_to_free(g)
        else:
            f = self._module.obj(self.free_to_all(x))
            f = float(f)  # convert from 1x1 NumPy array to float
            return f

    def cons(self, x, index=None, gradient=False):
        """
        Evaluate the constraints (and optionally their Jacobian).
            c      = problem.cons(x)                         -- constraints
            ci     = problem.cons(x, index=i)                -- i-th constraint
            c, J   = problem.cons(x, gradient=True)          -- constraints and Jacobian
            ci, Ji = problem.cons(x, index=i, gradient=True) -- i-th constraint and its gradient

        This calls CUTEst routine CUTEST_ccfg or CUTEST_ccifg.

        For large problems, problem.scons returns sparse matrices.

        :param x: input vector
        :param index: which constraint to evaluate (default=None -> all constraints). Must be in 0..self.m-1.
        :param gradient: whether to return constraint(s) and gradient/Jacobian, or just constraint (default=False; i.e. constraint only)
        :return: value of constraint(s) and Jacobian/gradient of constraint(s) at x
        """
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
                c = self._module.cons(x)
                return c
            else:
                assert 0 <= index <= self.m - 1, "Invalid constraint index %g (must be in 0..%g)" % (index, self.m - 1)
                ci = self._module.cons(self.free_to_all(x), False, index)
                ci = float(ci)  # convert from 1x1 NumPy array to float
                return ci

    def lagjac(self, x, v=None):
        """
        Evaluate gradient of objective/Lagrangian, and Jacobian of constraints.
            g, J = problem.lagjac(x)      -- objective gradient and the Jacobian of constraints\n"
            g, J = problem.lagjac(x, v=v) -- Lagrangian gradient and the Jacobian of constraints\n"

        For large problems, problem.slagjac returns sparse matrices.

        This calls CUTEst routine CUTEST_cgr.

        :param x: input vector
        :param v: input vector of Lagrange multipliers
        :return: gradient of objective/Lagrangian, and Jacobian of constraints
        """
        if v is None:
            g, J = self._module.lagjac(self.free_to_all(x))
        else:
            g, J = self._module.lagjac(self.free_to_all(x), v)
        return self.all_to_free(g), J[:, self.idx_free]

    def jprod(self, p, transpose=False, x=None):
        """
        Evaluate product of constraint Jacobian with a vector p
            r = problem.jprod(p)                      -- evaluate J*p where J is the last compute Jacobian
            r = problem.jprod(p, transpose=True)      -- evaluate J.T*p where J is the last compute Jacobian
            r = problem.jprod(p, x=x)                 -- evaluate Jacobian at x, and return J(x)*p
            r = problem.jprod(p, transpose=True, x=x) -- evaluate Jacobian at x, and return J(x).T*p

        This calls CUTEst routine CUTEST_cjprod.

        :param p: vector to be multiplied by the Jacobian of constraints
        :param transpose: if True, multiply by transpose of Jacobian (J.T*p)
        :param x: input vector for Jacobian (default=None -> use last computed Jacobian)
        :return: Jacobian-vector product J(x)*p or J(x).T * p if transpose=True
        """
        if x is None:
            r = self._module.jprod(transpose, p if transpose else self.free_to_all(p, use_zeros=True))
        else:
            r = self._module.jprod(transpose, p if transpose else self.free_to_all(p, use_zeros=True), self.free_to_all(x))
        return self.all_to_free(r) if transpose else r

    def hess(self, x, v=None):
        """
        Evaluate the Hessian of the objective or Lagrangian.
        For constrained problems, the Hessian is L_{x,x}(x,v).
            H = problem.hess(x)      -- Hessian of objective at x for unconstrained problems
            H = problem.hess(x, v=v) -- Hessian of Lagrangian at (x, v) for constrained problems

        For unconstrained problems, v must be None.
        For constrained problems, v must be specified.
        To evaluate the Hessian of the objective for constrained problems use ihess()

        For large problems, problem.sphess returns sparse matrices.

        This calls CUTEst routine CUTEST_cdh or CUTEST_udh.

        :param x: input vector
        :param v: Lagrange multiplies (needed for constrained problems)
        :return: Hessian of objective (unconstrained) or Lagrangian (constrained) at x
        """
        if self.m > 0:
            assert v is not None, "Lagrange multipliers must be specified for constrained problems"
            H = self._module.hess(self.free_to_all(x), v)
        else:
            assert v is None, "Unconstrained problem - Lagrange multipliers cannot be specified"
            H = self._module.hess(self.free_to_all(x))
        return H[self.idx_free, self.idx_free]

    def ihess(self, x, cons_index=None):
        """
        Evaluate the Hessian of the objective or the index-th constraint.
            H = problem.ihess(x)               -- Hessian of the objective
            H = problem.ihess(x, cons_index=i) -- Hessian of i-th constraint

        For large problems, problem.isphess returns sparse matrices.

        This calls CUTEst routine CUTEST_cidh or CUTEST_udh.

        :param x: input vector
        :param cons_index: index of constraint (default is None -> use objective). Must be in 0..self.m-1.
        :return: Hessian of objective or a single constraint at x
        """
        if cons_index is None:
            H = self._module.ihess(self.free_to_all(x))
        else:
            assert 0 <= cons_index <= self.m - 1, "Invalid constraint index %g (must be in 0..%g)" % (cons_index, self.m - 1)
            H = self._module.ihess(self.free_to_all(x), cons_index)
        return H[self.idx_free, self.idx_free]

    def hprod(self, p, x=None, v=None):
        """
        Calculate Hessian-vector product H*p, where H is Hessian of objective (unconstrained) or Lagrangian (constrained).
        For constrained problems, the Hessian is L_{x,x}(x,v).
            r = problem.hprod(p)           -- use last computed Hessian to compute H*p
            r = problem.hprod(p, x=x, v=v) -- use Hessian of Lagrangian L_{x,x}(x,v) to compute H*p (constrained only)
            r = problem.hprod(p, x=x)      -- use Hessian of objective at x to compute H*p (unconstrained only)

        For unconstrained problems, v must be None.
        For constrained problems, v must be specified.

        This calls CUTEst routine CUTEST_chprod or CUTEST_uhprod

        :param p: vector to be multiplied by the Hessian
        :param x: input vector for the Hessian
        :param v: Lagrange multipliers for the Lagrangian. Required for constrained problems.
        :return: Hessian-vector product H*p
        """
        if self.m > 0:
            if x is not None:
                assert v is not None, "Lagrange multipliers must be specified for constrained problems"
                H = self._module.hprod(self.free_to_all(p, use_zeros=True), self.free_to_all(x), v)
            else:
                H = self._module.hprod(self.free_to_all(p, use_zeros=True))
        else:
            assert v is None, "Unconstrained problem - Lagrange multipliers cannot be specified"
            if x is not None:
                H = self._module.hprod(self.free_to_all(p, use_zeros=True), self.free_to_all(x))
            else:
                H = self._module.hprod(self.free_to_all(p, use_zeros=True))
        return H[self.idx_free, self.idx_free]

    def gradhess(self, x, v=None, gradient_of_lagrangian=True):
        """
        Evaluate the gradient of objective or Lagrangian, Jacobian of constraints and Hessian of objective/Lagrangian.
        For constrained problems, the gradient is L_{x}(x,v) and the Hessian is L_{x,x}(x,v).
            g, H    = problem.gradhess(x)                                    -- for unconstrained problems
            g, J, H = problem.gradhess(x, v=v)                               -- for constrained problems (g = grad Lagrangian)
            g, J, H = problem.gradhess(x, v=v, gradient_of_lagrangian=False) -- for constrained problems (g = grad objective)

        For constrained problems, v must be specified, and the Hessian of the Lagrangian is always returned.
        For Hessian of the objective, use problem.ihess().

        For large problems, problem.gradsphess returns sparse matrices.

        This calls CUTEst routine CUTEST_cgrdh or CUTEST_ugrdh.

        :param x: input vector
        :param v: vector of Lagrange multipliers. Required for constrained problems.
        :param gradient_of_lagrangian: for constrained problems, return gradient of objective or Lagrangian?
        :return: gradient of objective or Lagrangian, (Jacobian of constraints) and Hessian of objective/Lagrangian at x
        """
        if self.m > 0:
            assert v is not None, "Lagrange multipliers must be specified for constrained problems"
            g, J, H = self._module.gradhess(self.free_to_all(x), v, gradient_of_lagrangian)
            return self.all_to_free(g), J[:, self.idx_free], H[self.idx_free, self.idx_free]
        else:
            assert v is None, "Unconstrained problem - Lagrange multipliers cannot be specified"
            g, H = self._module.gradhess(self.free_to_all(x))
            return self.all_to_free(g), H[self.idx_free, self.idx_free]

    def scons(self, x, index=None):
        """
        Evaluate the constraints and optionally their sparse Jacobian/gradient.
            c, J   = problem.scons(x)          -- constraints and sparse Jacobian
            ci, Ji = problem.scons(x, index=i) -- i-th constraint and its sparse gradient

        The matrix J or vector Ji is of type scipy.sparse.coo_matrix.

        For small problems, problem.cons returns dense matrices.

        This calls CUTEst routine CUTEST_ccfsg or CUTEST_ccifsg.

        :param x: input vector
        :param index: which constraint to evaluate (default=None -> all constraints). Must be in 0..self.m-1.
        :return: value of constraint(s) and sparse Jacobian/gradient of constraint(s) at x, type scipy.sparse.coo_matrix
        """
        if index is None:
            c, J = self._module.scons(self.free_to_all(x))
            return c, sparse_mat_extract_columns(J, self.idx_free)
        else:
            assert 0 <= index <= self.m - 1, "Invalid constraint index %g (must be in 0..%g)" % (index, self.m - 1)
            ci, Ji = self._module.scons(self.free_to_all(x), index)
            ci = float(ci)  # convert from 1x1 NumPy array to float
            return ci, sparse_vec_extract_indices(Ji, self.idx_free)

    def slagjac(self, x, v=None):
        """
        Evaluate sparse gradient of objective or Lagrangian, and sparse Jacobian of constraints
            g, J = problem.slagjac(x)      -- objective gradient and Jacobian
            g, J = problem.slagjac(x, v=v) -- Lagrangian gradient and Jacobian

        The vector g and matrix J are of type scipy.sparse.coo_matrix.

        For small problems, problem.lagjac returns dense matrices.

        This calls CUTEst routine CUTEST_csgr.

        :param x: input vector
        :param v: vector of Lagrange multipliers
        :return: gradient of objective/Lagrangian, and Jacobian, type scipy.sparse.coo_matrix
        """
        if v is None:
            g, J = self._module.slagjac(self.free_to_all(x))
        else:
            g, J = self._module.slagac(self.free_to_all(x), v)
        return sparse_vec_extract_indices(g, self.idx_free), sparse_mat_extract_columns(J, self.idx_free)

    def sphess(self, x, v=None):
        """
        Evaluate sparse Hessian of objective or Lagrangian.
        For constrained problems, the Hessian is L_{x,x}(x,v).
            H = problem.sphess(x)    -- Hessian of objective (unconstrained problems)
            H = problem.sphess(x, v) -- Hessian of Lagrangian (constrained problems)

        For unconstrained problems, v must be None.
        For constrained problems, v must be specified.
        To evaluate the Hessian of the objective for constrained problems use isphess()

        The matrix H is of type scipy.sparse.coo_matrix.

        For small problems, problem.hess returns dense matrices.

        This calls CUTEst routine CUTEST_csh or CUTEST_ush.

        :param x: input vector
        :param v: vector of Lagrange multipliers. Must be specified for constrained problems.
        :return: Hessian of objective or Lagrangian, type scipy.sparse.coo_matrix
        """
        if self.m > 0:
            assert v is not None, "Lagrange multipliers must be specified for constrained problems"
            H = self._module.sphess(self.free_to_all(x), v)
        else:
            assert v is None, "Unconstrained problem - Lagrange multipliers cannot be specified"
            H = self._module.sphess(self.free_to_all(x), v)
        return sparse_mat_extract_rows_and_columns(H, self.idx_free, self.idx_free)

    def isphess(self, x, cons_index=None):
        """
        Evaluate the sparse Hessian of the objective or the index-th constraint.
            H = problem.isphess(x)               -- Hessian of the objective
            H = problem.isphess(x, cons_index=i) -- Hessian of i-th constraint

        The matrix H is of type scipy.sparse.coo_matrix.

        For small problems, problem.ihess returns dense matrices.

        This calls CUTEst routine CUTEST_cish or CUTEST_ush.

        :param x: input vector
        :param cons_index: index of constraint (default is None -> use objective). Must be in 0..self.m-1.
        :return: Hessian of objective or a single constraint at x, type scipy.sparse.coo_matrix
        """
        if cons_index is None:
            H = self._module.isphess(self.free_to_all(x))
        else:
            assert 0 <= cons_index <= self.m - 1, "Invalid constraint index %g (must be in 0..%g)" % (
            cons_index, self.m - 1)
            H = self._module.isphess(self.free_to_all(x), cons_index)
        return sparse_mat_extract_rows_and_columns(H, self.idx_free, self.idx_free)

    def gradsphess(self, x, v=None, gradient_of_lagrangian=True):
        """
        Evaluate the gradient of objective or Lagrangian, Jacobian of constraints and Hessian of objective/Lagrangian.
        For constrained problems, the gradient is L_{x}(x,v) and the Hessian is L_{x,x}(x,v).
            g, H    = problem.gradsphess(x)                                    -- for unconstrained problems
            g, J, H = problem.gradsphess(x, v=v)                               -- for constrained problems (g = grad Lagrangian)
            g, J, H = problem.gradsphess(x, v=v, gradient_of_lagrangian=False) -- for constrained problems (g = grad objective)

        For constrained problems, v must be specified, and the Hessian of the Lagrangian is always returned.
        For Hessian of the objective, use problem.ihess().

        The vector g and matrices J and H are of type scipy.sparse.coo_matrix.

        For small problems, problem.gradhess returns dense matrices.

        This calls CUTEst routine CUTEST_csgrsh or CUTEST_ugrsh.

        :param x: input vector
        :param v: vector of Lagrange multipliers. Required for constrained problems.
        :param gradient_of_lagrangian: for constrained problems, return gradient of objective or Lagrangian?
        :return: gradient of objective or Lagrangian, (Jacobian of constraints) and Hessian of objective/Lagrangian at x, type scipy.sparse.coo_matrix
        """
        if self.m > 0:
            assert v is not None, "Lagrange multipliers must be specified for constrained problems"
            g, J, H = self._module.gradsphess(self.free_to_all(x), v, gradient_of_lagrangian)
            return sparse_vec_extract_indices(g, self.idx_free), \
                   sparse_mat_extract_columns(J, self.idx_free), \
                   sparse_mat_extract_rows_and_columns(H, self.idx_free, self.idx_free)
        else:
            assert v is None, "Unconstrained problem - Lagrange multipliers cannot be specified"
            g, H = self._module.gradsphess(self.free_to_all(x))
            return sparse_vec_extract_indices(g, self.idx_free), sparse_mat_extract_rows_and_columns(H, self.idx_free, self.idx_free)

    def report(self):
        """
        Get CUTEst usage statistics.
            stats = problem.report()

        Statistics are:
        - f = number of objective evaluations
        - g = number of objective gradient evaluations
        - H = number of objective Hessian evaluations
        - Hprod = number of objective Hessian-vector products
        - tsetup = CPU time for setup
        - trun = CPU time for run
        and for constrained problems, also
        - c = number of constraint evaluations
        - cg = number of constraint gradient evaluations
        - cH = number of constraint Hessian evaluations

        This calls CUTEst routine CUTEST_creport or CUTEST_ureport.

        :return: dict of usage statistics
        """
        # TODO keep track of own stats using this module to report more detailed info?
        return self._module.report()
