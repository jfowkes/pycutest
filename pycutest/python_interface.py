"""
The Python part of the interface for a specific problem
"""

__all__ = ['get_init_script']

# Raw script has some placeholder strings:
# [problemName], [efirst], [lfirst], [nvfirst], [sifParams|Str], [sifOptions|Str]

initScript = """# PyCutest problem interface module initialization file
# (C)2011 Arpad Buermen
# (C)2018 Jaroslav Fowkes, Lindon Roberts
# Licensed under GNU GPL V3

\"\"\"Interface module for CUTEst problem [problemName] with ordering
  efirst=[efirst], lfirst=[lfirst], nvfirst=[nvfirst]
sifdecode parameters : [sifParamsStr]
sifdecode options    : [sifOptionsStr]

Available functions
getinfo    -- get problem information
varnames   -- get names of problem's variables
connames   -- get names of problem's constraints
objcons    -- objective and constraints
obj        -- objective and objective gradient
cons       -- constraints and constraints gradients/Jacobian
lagjac     -- gradient of objective/Lagrangian and constraints Jacobian
jprod      -- product of constraints Jacobian with a vector
hess       -- Hessian of objective/Lagrangian
ihess      -- Hessian of objective/constraint
hprod      -- product of Hessian of objective/Lagrangian with a vector
gradhess   -- gradient and Hessian of objective (unconstrained problems) or
              gradient of objective/Lagrangian, Jacobian of constraints and
              Hessian of Lagrangian (constrained problems)
scons      -- constraints and sparse Jacobian of constraints
slagjac    -- gradient of objective/Lagrangian and sparse Jacobian
sphess     -- sparse Hessian of objective/Lagrangian
isphess    -- sparse Hessian of objective/constraint
gradsphess -- gradient and sparse Hessian of objective (unconstrained probl.)
              or gradient of objective/Lagrangian, sparse Jacobian of
              constraints and sparse Hessian of Lagrangian (constrained probl.)
report     -- get usage statistics
\"\"\"

# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

from ._pycutestitf import *
from . import _pycutestitf
import os
from scipy.sparse import coo_matrix
from numpy import zeros

# Get the directory where the binary module (and OUTSDIF.d) are found.
(_directory, _module)=os.path.split(_pycutestitf.__file__)

# Problem info structure and dimension
info=None
n=None
m=None

# Constraints and variable ordering
efirst=[efirst]
lfirst=[lfirst]
nvfirst=[nvfirst]

# Remember current directory and go to module directory where OUTSDIF.d is located
fromDir=os.getcwd()
os.chdir(_directory)

# Get problem dimension
(n, m)=_pycutestitf._dims()

# Set up the problem and get basic information
info=_pycutestitf._setup(efirst, lfirst, nvfirst)

# Store constraint and variable ordering information
if m>0:
    info['efirst']=efirst
    info['lfirst']=lfirst
info['nvfirst']=nvfirst

# Store sifdecode parameters and options
info['sifparams']=[sifParams]
info['sifoptions']=[sifOptions]

# Go back to initial directory
os.chdir(fromDir)

# Return problem info
def getinfo():
    \"\"\"
    Return the problem info dictionary.

    info=geinfo()

    Output
    info -- dictionary with the summary of test function's properties

    The dictionary has the following members:
    name       -- problem name
    n          -- number of variables
    m          -- number of constraints (excluding bounds)
    x          -- initial point (1D array of length n)
    bl         -- 1D array of length n with lower bounds on variables
    bu         -- 1D array of length n with upper bounds on variables
    nnzh       -- number of nonzero elements in the diagonal and upper triangle of
                  sparse Hessian
    vartype    -- 1D integer array of length n storing variable type
                  0=real,  1=boolean (0 or 1), 2=integer
    nvfirst    -- boolean flag indicating that nonlinear variables were placed
                  before linear variables
    sifparams  -- parameters passed to sifdecode with the -param option
                  None if no parameters were given
    sifoptions -- additional options passed to sifdecode
                  None if no additional options were given.

    For constrained problems the following additional members are available
    nnzj    -- number of nonzero elements in sparse Jacobian of constraints
    v       -- 1D array of length m with initial values of Lagrange multipliers
    cl      -- 1D array of length m with lower bounds on constraint functions
    cu      -- 1D array of length m with upper bounds on constraint functions
    equatn  -- 1D boolean array of length m indicating whether a constraint
               is an equation constraint
    linear  -- 1D boolean array of length m indicating whether a constraint
               is a linear constraint
    efirst  -- boolean flag indicating that equation constraints were places
               before inequation constraints
    lfirst  -- boolean flag indicating that linear constraints were placed
               before nonlinear constraints
    \"\"\"
    return info

def varnames():
    \"\"\"
    Return the names of problem's variables.

    nameList=varnames()

    nameList -- a list of strings representing the names of problem's variables.
                The variabels are ordered according to nvfirst flag.
    \"\"\"
    return _pycutestitf._varnames()

def connames():
    \"\"\"
    Return the names of problem's constraints.

    nameList=connames()

    nameList -- a list of strings representing the names of problem constraints.
                The constraints are ordered according to efirst and lfirst flags.
    \"\"\"
    return _pycutestitf._connames()

# Sparse tool wrappers (return scipy.sparse.coo_matrix matrices)
# _scons() wrapper
def scons(x, i=None):
    \"\"\"Returns the value of constraints and
    the sparse Jacobian of constraints at x.

    (c, J)=_scons(x)      -- Jacobian of constraints
    (ci, gi)=_scons(x, i) -- i-th constraint and its gradient

    Input
    x -- 1D array of length n with the values of variables
    i -- integer index of constraint (between 0 and m-1)

    Output
    c  -- 1D array of length m holding the values of constraints at x
    J  -- a scipy.sparse.coo_matrix of size m-by-n holding the Jacobian at x
    ci -- 1D array of length 1 holding the value of i-th constraint at x
    gi -- a scipy.sparse.coo_matrix of size 1-by-n holding the gradient of i-th constraint at x

    This function is a wrapper for _scons().
    \"\"\"

    if i is None:
        (c, Ji, Jif, Jv)=_pycutestitf._scons(x)
        return (c, coo_matrix((Jv, (Jif, Ji)), shape=(m, n)))
    else:
        (c, gi, gv)=_pycutestitf._scons(x, i)
        return (c, coo_matrix((gv, (zeros(len(gv)), gi)), shape=(1, n)))

# _slagjac() wrapper
def slagjac(x, v=None):
    \"\"\"Returns the sparse gradient of objective at x or Lagrangian at (x, v),
    and the sparse Jacobian of constraints at x.

    (g, J)=_slagjac(x)    -- objective gradient and Jacobian
    (g, J)=_slagjac(x, v) -- Lagrangian gradient and Jacobian

    Input
    x -- 1D array of length n with the values of variables
    v -- 1D array of length m with the values of Lagrange multipliers

    Output
    g -- a scipy.sparse.coo_matrix of size 1-by-n holding the gradient of objective at x or
         the gradient of Lagrangian at (x, v)
    J -- a scipy.sparse.coo_matrix of size m-by-n holding the sparse Jacobian
         of constraints at x

    This function is a wrapper for _slagjac().
    \"\"\"

    if v is None:
        (gi, gv, Ji, Jfi, Jv)=_pycutestitf._slagjac(x)
    else:
        (gi, gv, Ji, Jfi, Jv)=_pycutestitf._slagjac(x, v)
    return (
        coo_matrix((gv, (zeros(len(gv)), gi)), shape=(1, n)),
        coo_matrix((Jv, (Jfi, Ji)), shape=(m, n))
    )

# _sphess() wrapper
def sphess(x, v=None):
    \"\"\"Returns the sparse Hessian of the objective at x (unconstrained problems)
    or the sparse Hessian of the Lagrangian (constrained problems) at (x, v).

    H=_sphess(x)    -- Hessian of objective (unconstrained problems)
    H=_sphess(x, v) -- Hessian of Lagrangian (constrained problems)

    Input
    x -- 1D array of length n with the values of variables
    v -- 1D array of length m with the values of Lagrange multipliers

    Output
    H -- a scipy.sparse.coo_matrix of size n-by-n holding the sparse Hessian
         of objective at x or the sparse Hessian of the Lagrangian at (x, v)

    This function is a wrapper for _sphess().
    \"\"\"

    if v is None:
        (Hi, Hj, Hv)=_pycutestitf._sphess(x)
    else:
        (Hi, Hj, Hv)=_pycutestitf._sphess(x, v)
    return coo_matrix((Hv, (Hi, Hj)), shape=(n, n))

# _isphess() wrapper
def isphess(x, i=None):
    \"\"\"Returns the sparse Hessian of the objective or the sparse Hessian of i-th
    constraint at x.

    H=_isphess(x)    -- Hessian of objective
    H=_isphess(x, i) -- Hessian of i-th constraint

    Input
    x -- 1D array of length n with the values of variables
    i -- integer holding the index of constraint (between 0 and m-1)

    Output
    H -- a scipy.sparse.coo_matrix of size n-by-n holding the sparse Hessian
         of objective or the sparse Hessian i-th constraint at x

    This function is a wrapper for _isphess().
    \"\"\"

    if i is None:
        (Hi, Hj, Hv)=_pycutestitf._isphess(x)
    else:
        (Hi, Hj, Hv)=_pycutestitf._isphess(x, i)
    return coo_matrix((Hv, (Hi, Hj)), shape=(n, n))

# _gradsphess() wrapper
def gradsphess(x, v=None, lagrFlag=False):
    \"\"\"Returns the sparse Hessian of the Lagrangian, the sparse Jacobian of
    constraints, and the gradient of the objective or Lagrangian.

    (g, H)=gradsphess(x)              -- unconstrained problems
    (g, J, H)=gradsphess(x, v, gradl) -- constrained problems

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

    This function is a wrapper for _gradsphess().
    \"\"\"

    if v is None:
        (g, Hi, Hj, Hv)=_pycutestitf._gradsphess(x)
        return (coo_matrix(g), coo_matrix((Hv, (Hi, Hj)), shape=(n, n)))
    else:
        (gi, gv, Ji, Jfi, Jv, Hi, Hj, Hv)=_pycutestitf._gradsphess(x, v, lagrFlag)
        return (
            coo_matrix((gv, (zeros(len(gv)), gi)), shape=(1, n)),
            coo_matrix((Jv, (Jfi, Ji)), shape=(m, n)),
            coo_matrix((Hv, (Hi, Hj)), shape=(n, n))
        )

# Clean up
del os, fromDir, efirst, lfirst, nvfirst
"""


def get_init_script(problemName, efirst, lfirst, nvfirst, sifParams, sifOptions):
    s = initScript
    s = s.replace('[problemName]', problemName)
    s = s.replace('[efirst]', str(bool(efirst)))
    s = s.replace('[lfirst]', str(bool(lfirst)))
    s = s.replace('[nvfirst]', str(bool(nvfirst)))

    sifParamsStr = ""
    if sifParams is not None:
        for (key, value) in sifParams.items():
            sifParamsStr += "%s=%s " % (str(key), str(value))

    # Convert sifOptions to a string
    sifOptionsStr = ""
    if sifOptions is not None:
        for opt in sifOptions:
            sifOptionsStr += str(opt) + " "

    s = s.replace('[sifParams]', str(sifParams))
    s = s.replace('[sifParamsStr]', sifParamsStr)
    s = s.replace('[sifOptions]', str(sifOptions))
    s = s.replace('[sifOptionsStr]', sifOptionsStr)
    return s
