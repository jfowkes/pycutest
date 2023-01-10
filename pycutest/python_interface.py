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

Available interface functions
setup       -- setup problem and get problem information
dims       -- get problem dimensions
varnames   -- get names of problem's variables
connames   -- get names of problem's constraints
objcons     -- objective and constraints
obj         -- objective and objective gradient
cons        -- constraints and constraints gradients/Jacobian
lagjac      -- gradient of objective/Lagrangian and constraints Jacobian
jprod       -- product of constraints Jacobian with a vector
hess        -- Hessian of objective/Lagrangian
ihess       -- Hessian of objective/constraint
hprod       -- product of Hessian of objective/Lagrangian with a vector
gradhess    -- gradient and Hessian of objective (unconstrained problems) or
               gradient of objective/Lagrangian, Jacobian of constraints and
               Hessian of Lagrangian (constrained problems)
scons      -- constraints and sparse Jacobian of constraints
slagjac    -- gradient of objective/Lagrangian and sparse Jacobian
sphess     -- sparse Hessian of objective/Lagrangian
isphess    -- sparse Hessian of objective/constraint
gradsphess -- gradient and sparse Hessian of objective (unconstrained probl.)
               or gradient of objective/Lagrangian, sparse Jacobian of
               constraints and sparse Hessian of Lagrangian (constrained probl.)
report      -- get usage statistics
terminate   -- clear problem memory
\"\"\"

# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

from ._pycutestitf import *
from . import _pycutestitf

def setup():
    \"\"\"
    Set up the problem and get problem information.

    info=setup()

    info -- dictionary with the summary of test function's properties (see getinfo())
    \"\"\"
    import os

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
    (n, m)=_pycutestitf.dims()

    # Set up the problem and get basic information
    info=_pycutestitf.setup(efirst, lfirst, nvfirst)

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

    return info

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
