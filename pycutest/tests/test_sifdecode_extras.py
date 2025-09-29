import pycutest
import unittest
import io, sys  # to catch stdout

# All problems used here: ARGLALE, ROSENBR, BRATU2D


class TestAvailableParamsARGLALE(unittest.TestCase):
    def runTest(self):
        prob = 'ARGLALE'
        # Catch stdout
        # https://stackoverflow.com/questions/1218933/can-i-redirect-the-stdout-in-python-into-some-sort-of-string-buffer
        real_stdout = sys.stdout
        fake_stdout = io.StringIO()
        try:
            sys.stdout = fake_stdout
            # Now do the work
            pycutest.print_available_sif_params(prob)
        finally:
            sys.stdout = real_stdout
            output_string = fake_stdout.getvalue()
            fake_stdout.close()
            # Now can do checking
            print(output_string)
            """
            From ARGLALE.SIF:
            *IE N                   10             $-PARAMETER
            *IE N                   50             $-PARAMETER
            *IE N                   100            $-PARAMETER
             IE N                   200            $-PARAMETER

            *IE M                   20             $-PARAMETER .ge. N
            *IE M                   100            $-PARAMETER .ge. N
            *IE M                   200            $-PARAMETER .ge. N
             IE M                   400            $-PARAMETER .ge. N
            """
            self.assertTrue(prob in output_string, msg="Output missing problem name")
            self.assertTrue("N = 10 (int)" in output_string, msg="Missing option N=10")
            self.assertTrue("N = 50 (int)" in output_string, msg="Missing option N=50")
            self.assertTrue("N = 100 (int)" in output_string, msg="Missing option N=100")
            self.assertTrue("N = 200 (int) [default]" in output_string, msg="Missing (default) option N=200")
            self.assertTrue("M = 20 (int, .ge. N)" in output_string, msg="Missing option M=20")
            self.assertTrue("M = 100 (int, .ge. N)" in output_string, msg="Missing option M=100")
            self.assertTrue("M = 200 (int, .ge. N)" in output_string, msg="Missing option M=200")
            self.assertTrue("M = 400 (int, .ge. N) [default]" in output_string, msg="Missing (default) option M=400")


class TestAvailableParamsBRATU(unittest.TestCase):
    def runTest(self):
        prob = 'BRATU2D'
        # Catch stdout
        # https://stackoverflow.com/questions/1218933/can-i-redirect-the-stdout-in-python-into-some-sort-of-string-buffer
        real_stdout = sys.stdout
        fake_stdout = io.StringIO()
        try:
            sys.stdout = fake_stdout
            # Now do the work
            pycutest.print_available_sif_params(prob)
        finally:
            sys.stdout = real_stdout
            output_string = fake_stdout.getvalue()
            fake_stdout.close()
            # Now can do checking
            print(output_string)
            """
            From BRATU2D.SIF:
            *IE P                   7              $-PARAMETER  n=P**2   original value
            *IE P                   10             $-PARAMETER  n=P**2
            *IE P                   22             $-PARAMETER  n=P**2
            *IE P                   32             $-PARAMETER  n=P**2
             IE P                   72             $-PARAMETER  n=P**2

            *   LAMBDA is the Bratu problem parameter.  It should be positive.

             RE LAMBDA              4.0            $-PARAMETER > 0
            """
            self.assertTrue(prob in output_string, msg="Output missing problem name")
            self.assertTrue("P = 7 (int, n=P**2 original value)" in output_string, msg="Missing option P=7")
            self.assertTrue("P = 10 (int, n=P**2)" in output_string, msg="Missing option P=10")
            self.assertTrue("P = 22 (int, n=P**2)" in output_string, msg="Missing option P=22")
            self.assertTrue("P = 32 (int, n=P**2)" in output_string, msg="Missing option P=32")
            self.assertTrue("P = 72 (int, n=P**2) [default]" in output_string, msg="Missing (default) option P=72")
            self.assertTrue("LAMBDA = 4 (float, > 0) [default]" in output_string, msg="Missing (default) option LAMBDA=4")


class TestAvailableParamsROSENBR(unittest.TestCase):
    def runTest(self):
        prob = 'ROSENBR'
        # Catch stdout
        # https://stackoverflow.com/questions/1218933/can-i-redirect-the-stdout-in-python-into-some-sort-of-string-buffer
        real_stdout = sys.stdout
        fake_stdout = io.StringIO()
        try:
            sys.stdout = fake_stdout
            # Now do the work
            pycutest.print_available_sif_params(prob)
        finally:
            sys.stdout = real_stdout
            output_string = fake_stdout.getvalue()
            fake_stdout.close()
            # Now can do checking
            print(output_string)
            # ROSENBR has no parameters available
            self.assertTrue(prob in output_string, msg="Output missing problem name")
            output_string = output_string.replace("Parameters available for problem %s:" % prob, "")
            output_string = output_string.replace("End of parameters for problem %s" % prob, "")
            output_string = output_string.rstrip()
            print("***")
            print("'%s', %g" % (output_string, len(output_string)))
            print("***")
            self.assertEqual(len(output_string), 0, msg="Some parameters found")


class TestClassification(unittest.TestCase):
    def runTest(self):
        # http://www.cuter.rl.ac.uk/Problems/classification.shtml
        probs = {}
        probs['ARGLALE'] = 'NLR2-AN-V-V'
        probs['ROSENBR'] = 'SUR2-AN-2-0'
        probs['BRATU2D'] = 'NOR2-MN-V-V'
        true_probs = {}
        true_probs['ARGLALE'] = {'objective':'none', 'constraints':'linear', 'regular':True, 'degree':2,
                                 'origin':'academic', 'internal':False, 'n':'variable', 'm':'variable'}
        true_probs['ROSENBR'] = {'objective':'sum of squares', 'constraints':'unconstrained', 'regular':True,
                                 'degree':2, 'origin':'academic', 'internal':False, 'n':2, 'm':0}
        true_probs['BRATU2D'] = {'objective':'none', 'constraints':'other', 'regular':True, 'degree':2,
                                 'origin':'modelling', 'internal':False, 'n':'variable', 'm':'variable'}
        for p in probs:
            properties = pycutest.problem_properties(p)
            true_properties = true_probs[p]
            print(properties)
            self.assertEqual(true_properties['objective'], properties['objective'], "Incorrect objective for %s" % p)
            self.assertEqual(true_properties['constraints'], properties['constraints'], "Incorrect constraints for %s" % p)
            self.assertEqual(true_properties['regular'], properties['regular'], "Incorrect regularity for %s" % p)
            self.assertEqual(true_properties['degree'], properties['degree'], "Incorrect degree for %s" % p)
            self.assertEqual(true_properties['origin'], properties['origin'], "Incorrect origin for %s" % p)
            self.assertEqual(true_properties['internal'], properties['internal'], "Incorrect internal for %s" % p)
            self.assertEqual(true_properties['n'], properties['n'], "Incorrect n for %s" % p)
            self.assertEqual(true_properties['m'], properties['m'], "Incorrect m for %s" % p)


class TestFindProblems(unittest.TestCase):
    def runTest(self):
        # Check for:
        # ARGLALE = 'NLR2-AN-V-V'
        # ROSENBR = 'SUR2-AN-2-0'
        # BRATU2D = 'NOR2-MN-V-V'
        # First, just find any problem
        all_probs = pycutest.find_problems()
        for p in ['ARGLALE', 'ROSENBR', 'BRATU2D']:
            self.assertTrue(p in all_probs, msg="All problems doesn't contain %s" % p)
        # Now just find those with nonlinear objectives
        nl = pycutest.find_problems(objective='none')
        for p in ['ARGLALE', 'BRATU2D']:
            self.assertTrue(p in nl, msg="Nonlinear problems doesn't contain %s" % p)
        # Simple objectives (unconstrained & linear)
        simple_cons = pycutest.find_problems(constraints='unconstrained linear')
        for p in ['ARGLALE', 'ROSENBR']:
            self.assertTrue(p in simple_cons, msg="Nonlinear problems doesn't contain %s" % p)
        # Regularity
        reg = pycutest.find_problems(regular=True)
        for p in ['ARGLALE', 'ROSENBR', 'BRATU2D']:
            self.assertTrue(p in reg, msg="Regular problems doesn't contain %s" % p)
        # Degree
        deg = pycutest.find_problems(degree=[2,2])
        for p in ['ARGLALE', 'ROSENBR', 'BRATU2D']:
            self.assertTrue(p in deg, msg="2nd order problems doesn't contain %s" % p)
        # Origin
        academic = pycutest.find_problems(origin='academic')
        for p in ['ARGLALE', 'ROSENBR']:
            self.assertTrue(p in academic, msg="Academic problems doesn't contain %s" % p)
        # Internal
        no_internal = pycutest.find_problems(internal=False)
        for p in ['ARGLALE', 'ROSENBR', 'BRATU2D']:
            self.assertTrue(p in no_internal, msg="Non-internal problems doesn't contain %s" % p)
        # Dimensions
        twod = pycutest.find_problems(n=[2,2])
        for p in ['ROSENBR']:
            self.assertTrue(p in twod, msg="2D problems doesn't contain %s" % p)
        # Variable dim
        vardim = pycutest.find_problems(userN=True)
        for p in ['ARGLALE', 'BRATU2D']:
            self.assertTrue(p in vardim, msg="Variable-dim problems doesn't contain %s" % p)
        # Constraints
        nocons = pycutest.find_problems(m=[0, 0])
        for p in ['ROSENBR']:
            self.assertTrue(p in nocons, msg="Unconstrained problems doesn't contain %s" % p)
        # Variable dim
        varcons = pycutest.find_problems(userM=True)
        for p in ['ARGLALE', 'BRATU2D']:
            self.assertTrue(p in varcons, msg="Variable-constraint problems doesn't contain %s" % p)
