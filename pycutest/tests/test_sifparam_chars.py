import pycutest
import unittest

# All problems used here: SROSENBR


class TestSROSENBR(unittest.TestCase):
    def runTest(self):
        pycutest.clear_cache('SROSENBR', sifParams={'N/2':250})
        p = pycutest.import_problem('SROSENBR', sifParams={'N/2':250})
        self.assertEqual(p.name, 'SROSENBR', msg="Wrong name")
        self.assertEqual(p.sifParams['N/2'], 250, msg="Wrong sifParams")
        # This problem has digits and '/' in sifParams - cache folder name needs to handle this
