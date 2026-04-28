import pycutest
import unittest

# All problems used here: FLETCBV3


class TestFLETCBV3(unittest.TestCase):
    def runTest(self):
        pycutest.clear_cache('FLETCBV3', sifParams={'N': 10, 'KAPPA': 0.0})
        p = pycutest.import_problem('FLETCBV3', sifParams={'N': 10, 'KAPPA': 0.0})
        self.assertEqual(p.name, 'FLETCBV3', msg="Wrong name")
        self.assertEqual(p.sifParams['N'], 10, msg="Wrong N sifParam")
        self.assertEqual(p.sifParams['KAPPA'], 0.0, msg="Wrong KAPPA sifParam")
        self.assertEqual(p.n_free, 10, msg="Wrong number of free variables")
        # This problem has multiple parameters in sifParams and sifdecode needs to handle this
