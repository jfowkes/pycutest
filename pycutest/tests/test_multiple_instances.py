import pycutest
import unittest

# All problems used here: ROSENBR, ARGLALE

class testCUTEstProblemInstances(unittest.TestCase):
    def runTest(self):
        # clear cached problems (if any)
        pycutest.clear_cache('ROSENBR')
        pycutest.clear_cache('ARGLALE', sifParams={'N':10})

        # test re-import of same problem
        p = pycutest.import_problem('ROSENBR')
        print(p.x0)
        p = pycutest.import_problem('ROSENBR')
        print(p.x0)
        del p

        # test re-import of same problem after delete
        p = pycutest.import_problem('ROSENBR')
        print(p.x0)
        p = pycutest.import_problem('ROSENBR')
        print(p.x0)

        # test re-import of problem with parameters
        p2 = pycutest.import_problem('ARGLALE', sifParams={'N':10})
        print(p2.x0)
        p2 = pycutest.import_problem('ARGLALE', sifParams={'N':10})
        print(p2.x0)
        del p2
        p2 = pycutest.import_problem('ARGLALE', sifParams={'N':10})
        print(p2.x0)
        p2 = pycutest.import_problem('ARGLALE', sifParams={'N':10})
        print(p2.x0)
