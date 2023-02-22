import numpy as np
import pycutest
import unittest

# All problems used here: ROSENBR, ARGLALE

def array_compare(x, y, thresh=1e-8):
    return np.max(np.abs(x - y)) < thresh

class testCUTEstProblemInstances(unittest.TestCase):
    def runTest(self):
        # clear cached problems (if any)
        pycutest.clear_cache('ROSENBR')
        pycutest.clear_cache('ARGLALE', sifParams={'N':10})

        # test re-import of same problem
        p = pycutest.import_problem('ROSENBR')
        self.assertTrue(array_compare(p.x0, np.array([-1.2,1.])), msg="Wrong x0")
        p = pycutest.import_problem('ROSENBR')
        self.assertTrue(array_compare(p.x0, np.array([-1.2,1.])), msg="Wrong x0")
        del p

        # test re-import of same problem after delete
        p = pycutest.import_problem('ROSENBR')
        self.assertTrue(array_compare(p.x0, np.array([-1.2,1.])), msg="Wrong x0")
        p = pycutest.import_problem('ROSENBR')
        self.assertTrue(array_compare(p.x0, np.array([-1.2,1.])), msg="Wrong x0")

        # test re-import of problem with parameters
        p2 = pycutest.import_problem('ARGLALE', sifParams={'N':10})
        self.assertTrue(array_compare(p2.x0, np.ones((10,))), msg="Wrong x0")
        p2 = pycutest.import_problem('ARGLALE', sifParams={'N':10})
        self.assertTrue(array_compare(p2.x0, np.ones((10,))), msg="Wrong x0")
        del p2
        p2 = pycutest.import_problem('ARGLALE', sifParams={'N':10})
        self.assertTrue(array_compare(p2.x0, np.ones((10,))), msg="Wrong x0")
        p2 = pycutest.import_problem('ARGLALE', sifParams={'N':10})
        self.assertTrue(array_compare(p2.x0, np.ones((10,))), msg="Wrong x0")
