import os
import pycutest
import unittest

# All problems used here: SCURLY20

class testCUTEstRestoreCWD(unittest.TestCase):
    def runTest(self):
        # clear cached problems (if any)
        pycutest.clear_cache('SCURLY20', sifParams={'N':10})

        # test restoration of current working directory on problem failure
        try:
            print("Testing problem failure...")
            pycutest.import_problem('SCURLY20', sifParams={'N': 10})
        except RuntimeError:
            print("Problem failed as expected, testing restoration of cwd...")
        print(os.getcwd())
        print()
