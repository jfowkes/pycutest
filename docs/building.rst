Building Test Problems
======================

In this section, we describe the interface for finding and compiling CUTEst problems.

Finding Problems
----------------
CUTEst has a scheme for classifying problems (see `here <http://www.cuter.rl.ac.uk/Problems/classification.shtml>`_).
Based on these properties, we can search for test problems using the :code:`find_problems()` method.
We can check the properties of a specific function with :code:`problem_properties()`.

  .. code-block:: python

      # Example: using problem classification system
      import pycutest
      # Find unconstrained, variable-dimension problems
      probs = pycutest.find_problems(constraints='U', userN=True)
      print(sorted(probs)[:5])
      # Properties of problem ROSENBR
      print(pycuttest.problem_properties('ROSENBR'))

Which produces output

  .. code-block:: none

      # List of unconstrained, variable-dimension problems
      ['ARGLINA', 'ARGLINB', 'ARGLINC', 'ARGTRIGLS', 'ARWHEAD']
      # Properties of problem 'ROSENBR'
      {'internal': False, 'degree': 2, 'n': 2, 'm': 0, 'objective': 'S', 'origin': 'A', 'constraints': 'U', 'regular': True}

Full documentation for these functions is given below.

.. autofunction:: pycutest.find_problems

.. autofunction:: pycutest.problem_properties


Building Problems
-----------------
Many CUTEst problems have optional input parameters. The :code:`print_available_sif_params()` function prints a list of valid parameters for a given problem.
Then, we can build a problem, including optional parameters, with :code:`import_problem()`.
This returns an instance of the :code:`CUTEstProblem` class (see next section).

  .. code-block:: python

      # Example: building problem
      import pycutest
      # Print parameters for problem ARGLALE
      pycutest.print_available_sif_params('ARGLALE')
      # Build this problem with N=100, M=200
      problem = pycutest.import_problem('ARGLALE', sifParams={'N':100, 'M':200})
      print(problem)

The available parameters for this problem, as shown by PyCUTEst, are:

  .. code-block:: none

      Parameters available for problem ARGLALE:
      N = 10 (int)
      N = 50 (int)
      N = 100 (int)
      N = 200 (int) [default]
      M = 20 (int, .ge. N)
      M = 100 (int, .ge. N)
      M = 200 (int, .ge. N)
      M = 400 (int, .ge. N) [default]
      End of parameters for problem ARGLALE
      # Built problem
      CUTEst problem ARGLALE (params {'M': 200, 'N': 100}) with 100 variables and 200 constraints

This means that this problem has two integer parameters :code:`N` and :code:`M` (default 200 and 400 respectively), where :code:`N` cannot be smaller than :code:`M`.

Full documentation for these functions is given below.

.. autofunction:: pycutest.print_available_sif_params

.. autofunction:: pycutest.import_problem

Cache Management
----------------
PyCUTEst works by compiling each problem in its own folder inside its cache (given by the :code:`PYCUTEST_CACHE` environment variable).
A problem can be cleared from the cache using :code:`clear_cache()`, and a list of all problems currently installed can be displayed with :code:`all_cached_problems()`.
Documentation for these functions is given below.

.. autofunction:: pycutest.clear_cache

.. autofunction:: pycutest.all_cached_problems
