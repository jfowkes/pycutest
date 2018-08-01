# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

import math as ma
import numpy as np
import scipy.sparse as sparse
import pycutest
import unittest

# All problems used here: ARWHEAD (unconstrained) / ARWHDNE (constrained)
# Test sparsity by comparing to dense versions

def array_compare(x, y, thresh=1e-8):
    return np.max(np.abs(x - y)) < thresh


# class TestSparseUnconstrained(unittest.TestCase):
#     def runTest(self):
#         p = pycutest.import_problem('ARWHEAD', sifParams={'N':100})
#         # Some test vectors
#         xs = [p.x0, np.ones((p.n,)), -np.ones((p.n)), 0.2*np.arange(p.n), np.sin(np.arange(p.n))-np.cos(np.arange(p.n))]
#
#         for x in xs:
#             places = 8  # accuracy
#             print("Trying x = [...]")
#             ftrue, gdense = p.obj(x, gradient=True)
#             Hdense = p.hess(x)
#             # scons
#             c = p.scons(x)
#             self.assertIsNone(c, msg="scons c is not None")
#             # slagjac
#             g, J = p.slagjac(x)
#             print(g.shape)
#             self.assertTrue(array_compare(gdense, g.toarray(), thresh=10**(-places)), msg="slagjac g wrong")
#             self.assertIsNone(J, msg="slagjac J is not None")
#             # sphess
#             H = p.sphess(x)
#             self.assertTrue(array_compare(Hdense, H.toarray(), thresh=10 ** (-places)), msg="sphess H wrong")
#             # isphess
#             H = p.isphess(x)
#             self.assertTrue(array_compare(Hdense, H.toarray(), thresh=10 ** (-places)), msg="isphess H wrong")
#             # gradsphess
#             g, H = p.gradsphess(x)
#             self.assertTrue(array_compare(gdense, g.toarray(), thresh=10 ** (-places)), msg="gradsphess g wrong")
#             self.assertTrue(array_compare(Hdense, H.toarray(), thresh=10 ** (-places)), msg="gradsphess H wrong")


class TestSparseConstrained(unittest.TestCase):
    def runTest(self):
        p = pycutest.import_problem('ARWHDNE', sifParams={'N':100})
        # Some test vectors
        xs = [p.x0, np.ones((p.n,)), -np.ones((p.n)), 0.2 * np.arange(p.n),
              np.sin(np.arange(p.n)) - np.cos(np.arange(p.n))]

        for x in xs:
            places = 8  # accuracy
            print("Trying x = [...]")
            cdense, Jdense = p.cons(x, gradient=True)
            # scons
            c = p.scons(x)
            self.assertTrue(array_compare(cdense, c, thresh=10**(-places)), msg="scons c is wrong 1")
            for i in range(p.n):
                ci = p.scons(x, index=i)
                self.assertAlmostEqual(ci, cdense[i], places=places, msg="scons ci is wrong 2 [i = %g]" % i)
            c, J = p.scons(x, gradient=True)
            self.assertTrue(array_compare(cdense, c, thresh=10 ** (-places)), msg="scons c is wrong 3")
            self.assertTrue(array_compare(Jdense, J.toarray(), thresh=10 ** (-places)), msg="scons J is wrong 3")
            for i in range(p.n):
                ci, Ji = p.scons(x, index=0, gradient=True)
                self.assertAlmostEqual(ci, cdense[i], places=places, msg="scons ci is wrong 4 [i = %g]" % i)
                self.assertTrue(array_compare(Jdense[i,:], Ji.toarray(), thresh=10 ** (-places)), msg="scons J is wrong 4 [i = %g]" % i)

            # # slagjac
            # g, J = p.slagjac(x)
            # print(g.shape)
            # self.assertTrue(array_compare(gdense, g.toarray(), thresh=10 ** (-places)), msg="slagjac g wrong")
            # self.assertIsNone(J, msg="slagjac J is not None")
            # # sphess
            # H = p.sphess(x)
            # self.assertTrue(array_compare(Hdense, H.toarray(), thresh=10 ** (-places)), msg="sphess H wrong")
            # # isphess
            # H = p.isphess(x)
            # self.assertTrue(array_compare(Hdense, H.toarray(), thresh=10 ** (-places)), msg="isphess H wrong")
            # # gradsphess
            # g, H = p.gradsphess(x)
            # self.assertTrue(array_compare(gdense, g.toarray(), thresh=10 ** (-places)), msg="gradsphess g wrong")
            # self.assertTrue(array_compare(Hdense, H.toarray(), thresh=10 ** (-places)), msg="gradsphess H wrong")
        self.assertTrue(False)
