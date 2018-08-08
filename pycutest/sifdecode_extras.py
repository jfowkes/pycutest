"""
Wrapper to other SIF information - classifications, available parameters
"""

# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

import os, re
import subprocess
from glob import iglob

from .system_paths import get_sifdecoder_path, get_mastsif_path

__all__ = ['print_available_sif_params', 'problem_properties', 'find_problems']


def print_available_sif_params(problemName):
    """
    Call sifdecode on given problem to print out available parameters
    This function is OS dependent. Currently works only for Linux and MacOS.

    :param problemName: CUTEst problem name
    :return: Nothing
    """
    # Call sifdecode
    spawnOK=True
    try:
        # Start sifdecode
        p = subprocess.Popen(
            [get_sifdecoder_path()] + ['-show'] + [problemName],
            universal_newlines=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        # Collect output
        messages=p.stdout.read()

        # Now wait for the process to finish. If we don't wait p might get garbage-collected before the
        # actual process finishes which can result in a crash of the interpreter.
        retcode=p.wait()

        # Check return code. Nonzero return code means that something has gone bad.
        # if retcode!=0:
        #     spawnOK=False
    except:
        spawnOK=False

    if not spawnOK:
        print(messages)
        print("Unable to show available parameters (SIFDecode error)")
        return

    # Parse the output and show it in a useful way
    print("Parameters available for problem %s:" % problemName)
    for line in messages.split('\n'):
        if '=' in line:
            if 'uncommented' in line:
                comment = None
            else:
                comment = line[line.find('comment:') + len('comment:'):].strip()
            default = 'default value' in line
            vals = line.split()
            var_name, value = vals[0].split('=')
            if vals[1] == '(IE)':
                dtype = 'int'
                value = int(value)
            elif vals[1] == '(RE)':
                dtype = 'float'
                value = float(value)
            else:
                dtype = 'unknown type'
                value = None
            if comment is not None:
                print("%s = %g (%s, %s) %s" % (var_name, value, dtype, comment, '[default]' if default else ''))
            else:
                print("%s = %g (%s) %s" % (var_name, value, dtype, '[default]' if default else ''))
    print("End of parameters for problem %s" % problemName)
    return


# Problem classifications
classification=None


def update_classifications(verbose=False):
    """
    Updates the list of problem classifications from SIF files.
    Collects the CUTEst problem classification strings.

    * *verbose* -- if set to ``True``, prints output as files are scanned

    Every SIF file contains a line of the form
      ``-something- classification -code-``

    Code has the following format
      ``OCRr-GI-N-M``

    *O* (single letter) - type of objective

    * ``N`` .. no objective function defined
    * ``C`` .. constant objective function
    * ``L`` .. linear objective function
    * ``Q`` .. quadratic objective function
    * ``S`` .. objective function is a sum of squares
    * ``O`` .. none of the above

    *C* (single letter) - type of constraints

    * ``U`` .. unconstrained
    * ``X`` .. equality constraints on variables
    * ``B`` .. bounds on variables
    * ``N`` .. constraints represent the adjacency matrix of a (linear) network
    * ``L`` .. linear constraints
    * ``Q`` .. quadratic constraints
    * ``O`` .. more general than any of the above

    *R* (single letter) - problem regularity

    * ``R`` .. regular - first and second derivatives exist and are continuous
    * ``I`` .. irregular problem

    *r* (integer) - degree of the highest derivatives provided analytically
        within the problem description, can be 0, 1, or 2

    *G* (single letter) - origin of the problem

    * ``A`` .. academic (created for testing algorithms)
    * ``M`` .. modelling exercise (actual value not used in practical application)
    * ``R`` .. real-world problem

    *I* (single letter) - problem contains explicit internal variables

    * ``Y`` .. yes
    * ``N`` .. no

    *N* (integer or ``V``) - number of variables, ``V`` = can be set by user

    *M* (integer or ``V``) - number of constraints, ``V`` = can be set by user
    """
    global classification

    classification={}
    # Get a list of files in the MASTSIF folder
    it = iglob(os.path.join(get_mastsif_path(), '*.SIF'))

    p=re.compile('\\s*\\*\\s*classification\\s*', re.IGNORECASE)
    for fileName in it:
        # Extract problem name
        head, problemName=os.path.split(fileName)
        problemName=problemName[:-4]

        # Open and scan
        fh=open(fileName, 'r')

        while True:
            line=fh.readline()
            if not line:
                break
            # Match
            m=p.match(line)
            if m:
                # Found a match
                cf=line[m.end():].strip()

                # Report
                if verbose:
                    print("%8s: %s" % (problemName, cf))

                # Process
                classification[problemName]=cf

                # Done with file
                break
        # Close file
        fh.close()


def problem_properties(problemName):
    """
    Returns problem properties (uses the CUTEst problem classification string).

    See http://www.cuter.rl.ac.uk/Problems/classification.shtml for details on the properties.

    The output is a dictionary with the following members:

    * objective -- objective type code
    * constraints -- constraints type code
    * regular -- ``True`` if problem is regular
    * degree -- highest degree of analytically available derivative
    * origin -- problem origin code
    * internal -- ``True`` if problem has internal variables
    * n -- number of variables (``None`` = can be set by the user)
    * m -- number of constraints (``None`` = can be set by the user)

    :param problemName: problem name
    :return: dict
    """

    if classification is None:
        update_classifications()
    cfString=classification[problemName]

    data={
        'objective': cfString[0].upper(),
        'constraints': cfString[1].upper(),
        'regular': cfString[2] in "Rr",
        'degree': int(cfString[3]),
        'origin': cfString[5].upper(),
        'internal': cfString[6] in "Yy",
    }

    parts=cfString.split("-")

    if parts[2] in "Vv":
        data['n']=None
    else:
        data['n']=int(parts[2])

    try:
        if parts[3] in "Vv":
            data['m']=None
        else:
            data['m']=int(parts[3])
    except IndexError:
        # Some CUTEst problems are missing this entry
        data['m'] = None
        # print("Error finding constraint properties for %s" % problemName)

    return data


def find_problems(objective=None, constraints=None, regular=None,
        degree=None, origin=None, internal=None,
        n=None, userN=None, m=None, userM=None):
    """
    Returns the problem names of problems that match the given requirements.
    The search is based on the CUTEst problem classification string.

    Problems with a user-settable number of variables/constraints match any given n / m.

    Returns the problem names of problems that matched the given requirements.

    If a requirement is not given, it is not applied.

    See http://www.cuter.rl.ac.uk/Problems/classification.shtml for details on the letters used in the requirements.

    :param objective: a string containing one or more letters (NCLQSO) specifying the type of the objective function
    :param constraints: a string containing one or more letters (UXBNLQO) the type of the constraints
    :param regular: a boolean, ``True`` if the problem must be regular, ``False`` if it must be irregular
    :param degree: list of the form ``[min, max]`` specifying the minimum and the maximum number of analytically available derivatives
    :param origin: a string containing one or more letters (AMR) specifying the origin of the problem
    :param internal: a boolean, ``True`` if the problem must have internal variables, ``False`` if internal variables are not allowed
    :param n: a list of the form ``[min, max]`` specifying the lowest and the highest allowed number of variables
    :param userN: ``True`` if the problems must have user settable number of variables, ``False`` if the number must be hardcoded
    :param m: a list of the form ``[min, max]`` specifying the lowest and the highest allowed number of constraints
    :param userM: ``True`` of the problems must have user settable number of variables, ``False`` if the number must be hardcoded
    :return: list of strings with problem names which satisfy the given requirements
    """

    # Prepare classifications
    if classification is None:
        update_classifications()

    # Prepare name list
    nameList=[]

    # Go through all problems
    for name in classification.keys():
        # Extract data
        data=problem_properties(name)

        # Match
        if objective is not None and data['objective'] not in objective:
            continue
        if constraints is not None and data['constraints'] not in constraints:
            continue
        if regular is not None and data['regular']!=regular:
            continue
        if degree is not None and (data['degree']<degree[0] or data['degree']>degree[1]):
            continue
        if origin is not None and data['origin'] not in origin:
            continue
        if internal is not None and data['internal']!=internal:
            continue
        if n is not None and data['n'] is not None and (data['n']<n[0] or data['n']>n[1]):
            continue
        if  userN is not None:
            if userN and data['n'] is not None:
                continue
            if not userN and data['n'] is None:
                continue
        if m is not None and data['m'] is not None and (data['m']<m[0] or data['m']>m[1]):
            continue
        if userM is not None:
            if userM and data['m'] is not None:
                continue
            if not userM and data['m'] is None:
                continue

        # Problem matches, append it to the list
        nameList.append(name)

    return nameList
