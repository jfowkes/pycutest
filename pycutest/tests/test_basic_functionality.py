import math as ma
import numpy as np
import pycutest
import unittest

# All problems used here: ALLINITU (unconstrained), ALLINITC (constrained), ARWHEAD, ARWHDNE, NGONE, BOX2
# ALLINITC and BOX2 have fixed variables

def array_compare(x, y, thresh=1e-8):
    return np.max(np.abs(x - y)) < thresh


def allinit_obj(x):  # ALLINIT* objective
    return np.array([
	x[2]-1 + x[0]**2 + x[1]**2 + (x[2]+x[3])**2 + ma.sin(x[2])**2 + x[0]**2*x[1]**2 + x[3]-3 +
	ma.sin(x[2])**2 + (x[3]-1)**2 + (x[1]**2)**2 + (x[2]**2 + (x[3]+x[0])**2)**2 +
	(x[0]-4 + ma.sin(x[3])**2 + x[1]**2*x[2]**2)**2 + ma.sin(x[3])**4
	])


def allinit_grad(x):  # Gradient of ALLINIT* objective
    return np.array([
	2*(-4 + 2*x[0] + x[0]*x[1]**2 + x[1]**2*x[2]**2 + 2*(x[0]+x[3]) *
	 (x[2]**2 + (x[0]+x[3])**2) + ma.sin(x[3])**2),
    2*x[1] * (1 + x[0]**2 + 2*x[1]**2 + 2*x[2]**2 * (-4 + x[0] + x[1]**2 * x[2]**2 + ma.sin(x[3])**2)),
    1 + 2*(x[2]+x[3]) + 4*x[2] * (x[2]**2 + (x[0]+x[3])**2) + 4*ma.cos(x[2])*ma.sin(x[2]) +
     4*x[1]**2*x[2] * (-4 + x[0] + x[1]**2*x[2]**2 + ma.sin(x[3])**2),
    -1 + 2*x[2] + 4*x[3] + 4*(x[0]+x[3])*(x[2]**2 + (x[0]+x[3])**2) +
     4*ma.cos(x[3])*ma.sin(x[3]) * (-4 + x[0] + x[1]**2*x[2]**2 + 2*ma.sin(x[3])**2)
	])


def allinit_hess(x):  # Hessian of ALLINIT* objective
    return np.array([
	[2*(2 + x[1]**2 + 2*x[2]**2 + 6*(x[0]+x[3])**2),
	 4*x[1]*(x[0]+x[2]**2),
     4*x[2]*(x[1]**2 + 2*(x[0]+x[3])),
     4*(x[2]**2 + 3*(x[0] + x[3])**2 + ma.cos(x[3])*ma.sin(x[3]))
    ],
    [4*x[1]*(x[0] + x[2]**2),
     2*(1 + x[0]**2 - 8*x[2]**2 + 2*x[0]*x[2]**2 + 6*x[1]**2*(1 + x[2]**4) + 2*x[2]**2*ma.sin(x[3])**2),
     4*x[1]*x[2]*(-7 + 2*x[0] + 4*x[1]**2*x[2]**2 - ma.cos(2*x[3])),
     8*x[1]*x[2]**2*ma.cos(x[3])*ma.sin(x[3])
    ],
    [4*x[2]*(x[1]**2 + 2*(x[0]+x[3])),
     4*x[1]*x[2]*(-7 + 2*x[0] + 4*x[1]**2*x[2]**2 - ma.cos(2*x[3])),
     2 + 12*x[2]**2 + 8*x[1]**4*x[2]**2 + 4*(x[0] + x[3])**2 + 4*ma.cos(x[2])**2 -
      4*ma.sin(x[2])**2 + 4*x[1]**2*(-4 + x[0] + x[1]**2*x[2]**2 + ma.sin(x[3])**2),
     2 + 8*x[2]*(x[0]+x[3]) + 8*x[1]**2*x[2]*ma.cos(x[3])*ma.sin(x[3])
    ],
    [4*(x[2]**2 + 3*(x[0] + x[3])**2 + ma.cos(x[3])*ma.sin(x[3])),
     8*x[1]*x[2]**2*ma.cos(x[3])*ma.sin(x[3]),
     2 + 8*x[2]*(x[0]+x[3]) + 8*x[1]**2*x[2]*ma.cos(x[3])*ma.sin(x[3]),
     4*(1 + x[2]**2 + 3*(x[0]+x[3])**2 + (-3 + x[0] + x[1]**2*x[2]**2)*ma.cos(2*x[3]) - ma.cos(4*x[3]))
    ]
	])


class TestRemoval(unittest.TestCase):
    def runTest(self):
        probs = [('ALLINITU', None), ('ALLINITC', None), ('ARWHEAD', {'N':100}), ('ARWHDNE', {'N':100})]
        for (p, sifParams) in probs:
            pycutest.clear_cache(p, sifParams=sifParams)
        all_probs = pycutest.all_cached_problems()
        print(all_probs)
        for (p, sifParams) in probs:
            self.assertFalse((p, sifParams) in all_probs, msg="Found %s in cached problems" % p)


class TestParamError(unittest.TestCase):
    def runTest(self):
        prob = 'NGONE'
        bad_params = {'HNS': 4}
        pycutest.clear_cache(prob, sifParams=bad_params)
        self.assertRaises(RuntimeError, pycutest.import_problem, prob, sifParams=bad_params)


class TestALLINITU(unittest.TestCase):
    def runTest(self):
        pycutest.clear_cache('ALLINITU')
        p = pycutest.import_problem('ALLINITU')
        # Start with basic problem properties
        self.assertEqual(p.name, 'ALLINITU', msg="Wrong name")
        self.assertEqual(p.n, 4, msg="Wrong dimension")
        self.assertEqual(p.m, 0, msg="Wrong number of constraints")
        self.assertTrue(array_compare(p.x0, np.zeros((4,))), msg="Wrong x0")
        self.assertIsNone(p.sifParams, msg="Have sifParams")
        self.assertIsNone(p.sifOptions , msg="Have sifOptions")
        self.assertTrue(np.all(p.vartype == 0), msg="Not all variables are real")
        self.assertEqual(p.nnzh, 10, msg="Wrong nnzh")  # nnz of dense upper triangular 4x4 Hessian
        self.assertIsNone(p.eq_cons_first, msg="eq_cons_first is not None")
        self.assertIsNone(p.linear_cons_first, msg="linear_cons_first is not None")
        self.assertFalse(p.nonlinear_vars_first, msg="Nonlinear variables listed first")
        self.assertTrue(array_compare(p.bl, -1e20*np.ones((4,))), msg="Wrong lower bounds")
        self.assertTrue(array_compare(p.bu, 1e20 * np.ones((4,))), msg="Wrong upper bounds")
        self.assertIsNone(p.nnzj, msg="nnzj is not None")
        self.assertIsNone(p.v0, msg="v0 is not None")
        self.assertIsNone(p.cl, msg="cl is not None")
        self.assertIsNone(p.cu, msg="cu is not None")
        self.assertIsNone(p.is_eq_cons, msg="is_eq_cons is not None")
        self.assertIsNone(p.is_linear_cons, msg="is_linear_cons is not None")

        # If we need to multiply against another vector, use these
        ps = [np.zeros((4,)), 0.3 * np.ones((4,)), -0.5*np.arange(4)]

        # Now actually test the main routines
        for x in [p.x0, np.ones((4,)), -np.ones((4,)), np.arange(4)+1.0]:
            places = 8  # places accuracy for comparing floats
            print("Trying x =", x)
            # objcons
            f, c = p.objcons(x)
            self.assertAlmostEqual(f, allinit_obj(x), places=places, msg="Wrong objcons f value")
            self.assertIsNone(c, msg="objcons c value should be None")
            # obj
            f = p.obj(x)
            self.assertAlmostEqual(f, allinit_obj(x), places=places, msg="Wrong obj f value 1")
            f, g = p.obj(x, gradient=True)
            self.assertAlmostEqual(f, allinit_obj(x), places=places, msg="Wrong obj f value 2")
            self.assertTrue(array_compare(g, allinit_grad(x), thresh=10**(-places)), msg="Wrong obj g value 2")
            # grad
            g = p.grad(x)
            self.assertTrue(array_compare(g, allinit_grad(x), thresh=10**(-places)), msg="Wrong grad g value")
            # cons
            c = p.cons(x)
            self.assertIsNone(c, msg="cons should be None")
            # lagjac
            g, J = p.lagjac(x)
            self.assertTrue(array_compare(g, allinit_grad(x), thresh=10 ** (-places)), msg="Wrong lagjac g value")
            self.assertIsNone(J, msg="lagjac J should be None")
            # jprod
            r = p.jprod(x)
            self.assertIsNone(r, msg="jprod r should be None")
            # hess
            H = p.hess(x)
            self.assertTrue(array_compare(H, allinit_hess(x), thresh=10 ** (-places)), msg="Wrong hess H value")
            # ihess
            H = p.ihess(x)
            self.assertTrue(array_compare(H, allinit_hess(x), thresh=10 ** (-places)), msg="Wrong ihess H value")
            # hprod
            for pvec in ps:
                r = p.hprod(pvec, x=x)
                self.assertTrue(array_compare(r, allinit_hess(x).dot(pvec), thresh=10 ** (-places)),
                                msg="Wrong hprod r value for p = %s" % str(pvec))
                _ = p.hess(x+1.5)  # evaluate Hessian at another x, to test default x value
                r = p.hprod(pvec)
                self.assertTrue(array_compare(r, allinit_hess(x+1.5).dot(pvec), thresh=10 ** (-places)),
                                msg="Wrong hprod r value for p = %s" % str(pvec))
            # gradhess
            g, H = p.gradhess(x)
            self.assertTrue(array_compare(g, allinit_grad(x), thresh=10 ** (-places)), msg="Wrong gradhess g value")
            self.assertTrue(array_compare(H, allinit_hess(x), thresh=10 ** (-places)), msg="Wrong gradhess H value")

        stats = p.report()
        num_xs = 4
        self.assertEqual(stats['f'], 3*num_xs, msg="Wrong stat f")
        self.assertEqual(stats['g'], 4*num_xs, msg="Wrong stat g")
        self.assertEqual(stats['H'], (3+2*len(ps))*num_xs, msg="Wrong stat H")
        self.assertEqual(stats['Hprod'], (2*len(ps))*num_xs, msg="Wrong stat Hprod")
        self.assertIsNone(stats['c'], msg="Stat c should be None")
        self.assertIsNone(stats['cg'], msg="Stat cg should be None")
        self.assertIsNone(stats['cH'], msg="Stat cH should be None")


class TestALLINITC_with_fixed(unittest.TestCase):
    def runTest(self):
        # ALLINITC has the same objective function as above, but extra constraints:
        # Bounds:
        # x[1] >= 1
        # -1e10 <= x[2] <= 1
        # x[3] == 2
        # Nonlinear constraint
        # x[0]**2 + x[1]**2 - 1 == 0
        pycutest.clear_cache('ALLINITC')
        p = pycutest.import_problem('ALLINITC', drop_fixed_variables=False)
        # Start with basic problem properties
        self.assertEqual(p.name, 'ALLINITC', msg="Wrong name")
        self.assertEqual(p.n, 4, msg="Wrong dimension")
        self.assertEqual(p.m, 1, msg="Wrong number of constraints")
        self.assertTrue(array_compare(p.x0, np.zeros((4,))), msg="Wrong x0")
        self.assertIsNone(p.sifParams, msg="Have sifParams")
        self.assertIsNone(p.sifOptions , msg="Have sifOptions")
        self.assertTrue(np.all(p.vartype == 0), msg="Not all variables are real")
        self.assertEqual(p.nnzh, 10, msg="Wrong nnzh")  # nnz of dense upper triangular 4x4 Hessian
        self.assertFalse(p.eq_cons_first, msg="eq_cons_first is True")
        self.assertFalse(p.linear_cons_first, msg="linear_cons_first is True")
        self.assertFalse(p.nonlinear_vars_first, msg="Nonlinear variables listed first")
        self.assertTrue(array_compare(p.bl, np.array([-1e20, 1.0, -1e10, 2.0])), msg="Wrong lower bounds")
        self.assertTrue(array_compare(p.bu, np.array([1e20, 1e20, 1.0, 2.0])), msg="Wrong upper bounds")
        self.assertEqual(p.nnzj, 2, msg="Wrong nnzj")
        self.assertTrue(array_compare(p.v0, np.array([0.0])), msg="Wrong v0")
        self.assertTrue(array_compare(p.cl, np.array([0.0])), msg="Wrong cl")
        self.assertTrue(array_compare(p.cu, np.array([0.0])), msg="Wrong cu")
        self.assertEqual(p.is_eq_cons, np.array([True], dtype=bool), msg="Wrong is_eq_cons")
        self.assertEqual(p.is_linear_cons, np.array([False], dtype=bool), msg="Wrong is_linear_cons")

        # If we need to multiply against another vector, use these
        ps = [np.zeros((4,)), 0.3 * np.ones((4,)), -0.5*np.arange(4)]

        # If we need Lagrange multipliers, use these
        vs = [np.array([v]).reshape((1,)) for v in [p.v0, 1.0, -1.0, 0.4]]

        # The simple nonlinear constraint and its derivatives
        cons = lambda x: x[0]**2 + x[1]**2 - 1.0
        gradcons = lambda x: np.array([2.0*x[0], 2.0*x[1], 0.0, 0.0])
        jaccons = lambda x: gradcons(x).reshape((1,4))
        hesscons = lambda x: np.array([[2.0, 0.0, 0.0, 0.0], [0.0, 2.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])

        # CUTEst uses the + convention for the Lagrangian
        lag = lambda x, v: allinit_obj(x) + v*cons(x)
        gradlag = lambda x, v: allinit_grad(x) + v*gradcons(x)
        hesslag = lambda x, v: allinit_hess(x) + v*hesscons(x)
        hessjohn = lambda y0, x, v: y0*allinit_hess(x) + v*hesscons(x)

        # Now actually test the main routines
        for x in [p.x0, np.ones((4,)), -np.ones((4,)), np.arange(4)+1.0]:
            places = 8  # places accuracy for comparing floats
            print("Trying x =", x)
            # objcons
            f, c = p.objcons(x)
            self.assertAlmostEqual(f, allinit_obj(x), places=places, msg="Wrong objcons f value")
            self.assertAlmostEqual(c, cons(x), places=places, msg="Wrong objcons c value")
            # obj
            f = p.obj(x)
            self.assertAlmostEqual(f, allinit_obj(x), places=places, msg="Wrong obj f value 1")
            f, g = p.obj(x, gradient=True)
            self.assertAlmostEqual(f, allinit_obj(x), places=places, msg="Wrong obj f value 2")
            self.assertTrue(array_compare(g, allinit_grad(x), thresh=10**(-places)), msg="Wrong obj g value 2")
            # grad
            g = p.grad(x)
            self.assertTrue(array_compare(g, allinit_grad(x), thresh=10**(-places)), msg="Wrong grad g value")
            g = p.grad(x,0)
            self.assertTrue(array_compare(g, gradcons(x), thresh=10**(-places)), msg="Wrong grad g value 1")
            # cons
            c = p.cons(x)
            self.assertAlmostEqual(c, cons(x), places=places, msg="Wrong cons c value 1")
            c = p.cons(x, index=0)
            self.assertAlmostEqual(c, cons(x), places=places, msg="Wrong cons c value 2")
            c, J = p.cons(x, gradient=True)
            self.assertAlmostEqual(c, cons(x), places=places, msg="Wrong cons c value 3")
            self.assertTrue(array_compare(J, jaccons(x), thresh=10**(-places)), msg="Wrong cons J value 3")
            c, g = p.cons(x, index=0, gradient=True)
            self.assertAlmostEqual(c, cons(x), places=places, msg="Wrong cons c value 4")
            self.assertTrue(array_compare(g, gradcons(x), thresh=10**(-places)), msg="Wrong cons g value 4")
            # lag
            for v in vs:
                l = p.lag(x, v)
                self.assertAlmostEqual(l, lag(x, v), places=places, msg="Wrong lag l value for v = %s" % str(v))
                l, g = p.lag(x, v, gradient=True)
                self.assertAlmostEqual(l, lag(x, v), places=places, msg="Wrong lag l value 2 for v = %s" % str(v))
                self.assertTrue(array_compare(g, gradlag(x, v), thresh=10 ** (-places)), msg="Wrong lag g value 2 for v = %s" % str(v))
            # lagjac
            g, J = p.lagjac(x)
            self.assertTrue(array_compare(g, allinit_grad(x), thresh=10 ** (-places)), msg="Wrong lagjac g value 1")
            self.assertTrue(array_compare(J, jaccons(x), thresh=10 ** (-places)), msg="Wrong lagjac J value 1")
            for v in vs:
                g, J = p.lagjac(x, v=v)
                self.assertTrue(array_compare(g, gradlag(x, v), thresh=10 ** (-places)), msg="Wrong lagjac g value for v = %s" % str(v))
                self.assertTrue(array_compare(J, jaccons(x), thresh=10 ** (-places)), msg="Wrong lagjac J value for v = %s" % str(v))
            # jprod
            for pvec in ps:
                r = p.jprod(pvec, x=x)
                self.assertTrue(array_compare(r,jaccons(x).dot(pvec) ,thresh=10**(-places)), msg="Wrong jprod r value 1")
                _, _ = p.cons(x+1.5, gradient=True)  # evaluate Jacobian at another x to test default x value
                r = p.jprod(pvec)
                self.assertTrue(array_compare(r, jaccons(x+1.5).dot(pvec), thresh=10 ** (-places)), msg="Wrong jprod r value 2")
            for v in vs:
                # Test J.T products against v (correct dimension)
                r = p.jprod(v, x=x, transpose=True)
                self.assertTrue(array_compare(r, jaccons(x).T.dot(v), thresh=10 ** (-places)), msg="Wrong jprod r value 3")
                _, _ = p.cons(x + 1.5, gradient=True)  # evaluate Jacobian at another x to test default x value
                r = p.jprod(v, transpose=True)
                self.assertTrue(array_compare(r, jaccons(x+1.5).T.dot(v), thresh=10 ** (-places)), msg="Wrong jprod r value 4")
            # hess
            for v in vs:
                H = p.hess(x, v=v)
                self.assertTrue(array_compare(H, hesslag(x, v), thresh=10 ** (-places)), msg="Wrong hess H value")
            # ihess
            H = p.ihess(x)
            self.assertTrue(array_compare(H, allinit_hess(x), thresh=10 ** (-places)), msg="Wrong ihess H value 1")
            H = p.ihess(x, cons_index=0)
            self.assertTrue(array_compare(H, hesscons(x), thresh=10 ** (-places)), msg="Wrong ihess H value 2")
            # hprod
            for pvec in ps:
                for v in vs:
                    r = p.hprod(pvec, x=x, v=v)
                    self.assertTrue(array_compare(r, hesslag(x, v).dot(pvec), thresh=10 ** (-places)),
                                    msg="Wrong hprod r value for p = %s" % str(pvec))
                    _ = p.hess(x+1.5, v=v-0.2)  # evaluate Hessian at another x, to test default x value
                    r = p.hprod(pvec)
                    self.assertTrue(array_compare(r, hesslag(x+1.5, v-0.2).dot(pvec), thresh=10 ** (-places)),
                                    msg="Wrong hprod r value for p = %s" % str(pvec))
            # hjprod
            y0 = 3.5
            for pvec in ps:
                for v in vs:
                    r = p.hjprod(pvec, y0, x=x, v=v)
                    self.assertTrue(array_compare(r, hessjohn(y0, x, v).dot(pvec), thresh=10 ** (-places)),
                                    msg="Wrong hjprod r value for p = %s" % str(pvec))
                    #_ = p.hessj(y0, x+1.5, v=v-0.2) # evaluate Hessian of John function at another x, to test default x value
                    #r = p.hjprod(pvec, y0)
                    #self.assertTrue(array_compare(r, hessjohn(y0, x+1.5, v-0.2).dot(pvec), thresh=10 ** (-places)),
                    #                msg="Wrong hjprod r value for p = %s" % str(pvec))
            # gradhess
            for v in vs:
                g, J, H = p.gradhess(x, v=v)
                self.assertTrue(array_compare(g, gradlag(x, v), thresh=10 ** (-places)), msg="Wrong gradhess g value 1")
                self.assertTrue(array_compare(J, jaccons(x), thresh=10 ** (-places)), msg="Wrong gradhess J value 1")
                self.assertTrue(array_compare(H, hesslag(x, v), thresh=10 ** (-places)), msg="Wrong gradhess H value 1")
                g, J, H = p.gradhess(x, v=v, gradient_of_lagrangian=False)
                self.assertTrue(array_compare(g, allinit_grad(x), thresh=10 ** (-places)), msg="Wrong gradhess g value 2")
                self.assertTrue(array_compare(J, jaccons(x), thresh=10 ** (-places)), msg="Wrong gradhess J value 2")
                self.assertTrue(array_compare(H, hesslag(x, v), thresh=10 ** (-places)), msg="Wrong gradhess H value 2")

        stats = p.report()
        num_xs = 4
        self.assertEqual(stats['f'], (3 + 2*len(vs)) * num_xs, msg="Wrong stat f")
        self.assertEqual(stats['g'], (3 + 4*len(vs)) * num_xs, msg="Wrong stat g")
        self.assertEqual(stats['H'], (1 + 3*len(vs) + 3*len(vs)*len(ps)) * num_xs, msg="Wrong stat H")
        self.assertEqual(stats['Hprod'], (3*len(vs)*len(ps)) * num_xs, msg="Wrong stat Hprod")
        self.assertEqual(stats['c'], (5 + len(vs) + len(ps)) * num_xs, msg="Wrong stat c")
        self.assertEqual(stats['cg'], (4 + 6*len(vs) + 2*len(ps)) * num_xs, msg="Wrong stat cg")
        self.assertEqual(stats['cH'], (1 + 3*len(vs) + 3*len(ps)*len(vs)) * num_xs, msg="Wrong stat cH")


class TestALLINITC_with_free(unittest.TestCase):
    def runTest(self):
        # ALLINITC has the same objective function as above, but extra constraints:
        # Bounds:
        # x[1] >= 1
        # -1e10 <= x[2] <= 1
        # x[3] == 2
        # Nonlinear constraint
        # x[0]**2 + x[1]**2 - 1 <= 0
        # But here, we drop the fixed x[3], so effectively we get a 3D problem
        pycutest.clear_cache('ALLINITC')
        p = pycutest.import_problem('ALLINITC')
        # Start with basic problem properties
        self.assertEqual(p.name, 'ALLINITC', msg="Wrong name")
        self.assertEqual(p.n, 3, msg="Wrong dimension")
        self.assertEqual(p.m, 1, msg="Wrong number of constraints")
        self.assertTrue(array_compare(p.x0, np.zeros((3,))), msg="Wrong x0")
        self.assertIsNone(p.sifParams, msg="Have sifParams")
        self.assertIsNone(p.sifOptions , msg="Have sifOptions")
        self.assertTrue(np.all(p.vartype == 0), msg="Not all variables are real")
        self.assertEqual(p.nnzh, 10, msg="Wrong nnzh")  # nnz of dense upper triangular 4x4 Hessian
        self.assertFalse(p.eq_cons_first, msg="eq_cons_first is True")
        self.assertFalse(p.linear_cons_first, msg="linear_cons_first is True")
        self.assertFalse(p.nonlinear_vars_first, msg="Nonlinear variables listed first")
        self.assertTrue(array_compare(p.bl, np.array([-1e20, 1.0, -1e10])), msg="Wrong lower bounds")
        self.assertTrue(array_compare(p.bu, np.array([1e20, 1e20, 1.0])), msg="Wrong upper bounds")
        self.assertEqual(p.nnzj, 2, msg="Wrong nnzj")
        self.assertTrue(array_compare(p.v0, np.array([0.0])), msg="Wrong v0")
        self.assertTrue(array_compare(p.cl, np.array([0.0])), msg="Wrong cl")
        self.assertTrue(array_compare(p.cu, np.array([0.0])), msg="Wrong cu")
        self.assertEqual(p.is_eq_cons, np.array([True], dtype=bool), msg="Wrong is_eq_cons")
        self.assertEqual(p.is_linear_cons, np.array([False], dtype=bool), msg="Wrong is_linear_cons")

        # If we need to multiply against another vector, use these
        ps = [np.zeros((3,)), 0.3 * np.ones((3,)), -0.5*np.arange(3)]

        # If we need Lagrange multipliers, use these
        vs = [np.array([v]).reshape((1,)) for v in [p.v0, 1.0, -1.0, 0.4]]

        # The simple nonlinear constraint and its derivatives
        cons = lambda x: x[0]**2 + x[1]**2 - 1.0
        gradcons = lambda x: np.array([2.0*x[0], 2.0*x[1], 0.0])
        jaccons = lambda x: gradcons(x).reshape((1,3))
        hesscons = lambda x: np.array([[2.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 0.0]])

        obj = lambda x: allinit_obj(np.array([x[0], x[1], x[2], 2.0]))
        grad = lambda x: allinit_grad(np.array([x[0], x[1], x[2], 2.0]))[:-1]
        hess = lambda x: allinit_hess(np.array([x[0], x[1], x[2], 2.0]))[:-1, :-1]

        # CUTEst uses the + convention for the Lagrangian
        lag = lambda x, v: obj(x) + v*cons(x)
        gradlag = lambda x, v: grad(x) + v*gradcons(x)
        hesslag = lambda x, v: hess(x) + v*hesscons(x)
        hessjohn = lambda y0, x, v: y0*hess(x) + v*hesscons(x)

        # Now actually test the main routines
        for x in [p.x0, np.ones((3,)), -np.ones((3,)), np.arange(3)+1.0]:
            places = 8  # places accuracy for comparing floats
            print("Trying x =", x)
            # objcons
            f, c = p.objcons(x)
            self.assertAlmostEqual(f, obj(x), places=places, msg="Wrong objcons f value")
            self.assertAlmostEqual(c, cons(x), places=places, msg="Wrong objcons c value")
            # obj
            f = p.obj(x)
            self.assertAlmostEqual(f, obj(x), places=places, msg="Wrong obj f value 1")
            f, g = p.obj(x, gradient=True)
            self.assertAlmostEqual(f, obj(x), places=places, msg="Wrong obj f value 2")
            self.assertTrue(array_compare(g, grad(x), thresh=10**(-places)), msg="Wrong obj g value 2")
            # grad
            g = p.grad(x)
            self.assertTrue(array_compare(g, grad(x), thresh=10**(-places)), msg="Wrong grad g value")
            g = p.grad(x,0)
            self.assertTrue(array_compare(g, gradcons(x), thresh=10**(-places)), msg="Wrong grad g value 1")
            # cons
            c = p.cons(x)
            self.assertAlmostEqual(c, cons(x), places=places, msg="Wrong cons c value 1")
            c = p.cons(x, index=0)
            self.assertAlmostEqual(c, cons(x), places=places, msg="Wrong cons c value 2")
            c, J = p.cons(x, gradient=True)
            self.assertAlmostEqual(c, cons(x), places=places, msg="Wrong cons c value 3")
            self.assertTrue(array_compare(J, jaccons(x), thresh=10**(-places)), msg="Wrong cons J value 3")
            c, g = p.cons(x, index=0, gradient=True)
            self.assertAlmostEqual(c, cons(x), places=places, msg="Wrong cons c value 4")
            self.assertTrue(array_compare(g, gradcons(x), thresh=10**(-places)), msg="Wrong cons g value 4")
            # lag
            for v in vs:
                l = p.lag(x, v)
                self.assertAlmostEqual(l, lag(x, v), places=places, msg="Wrong lag l value for v = %s" % str(v))
                l, g = p.lag(x, v, gradient=True)
                self.assertAlmostEqual(l, lag(x, v), places=places, msg="Wrong lag l value 2 for v = %s" % str(v))
                self.assertTrue(array_compare(g, gradlag(x, v), thresh=10 ** (-places)), msg="Wrong lag g value 2 for v = %s" % str(v))
            # lagjac
            g, J = p.lagjac(x)
            self.assertTrue(array_compare(g, grad(x), thresh=10 ** (-places)), msg="Wrong lagjac g value 1")
            self.assertTrue(array_compare(J, jaccons(x), thresh=10 ** (-places)), msg="Wrong lagjac J value 1")
            for v in vs:
                g, J = p.lagjac(x, v=v)
                self.assertTrue(array_compare(g, gradlag(x, v), thresh=10 ** (-places)), msg="Wrong lagjac g value for v = %s" % str(v))
                self.assertTrue(array_compare(J, jaccons(x), thresh=10 ** (-places)), msg="Wrong lagjac J value for v = %s" % str(v))
            # jprod
            for pvec in ps:
                r = p.jprod(pvec, x=x)
                self.assertTrue(array_compare(r,jaccons(x).dot(pvec) ,thresh=10**(-places)), msg="Wrong jprod r value 1")
                _, _ = p.cons(x+1.5, gradient=True)  # evaluate Jacobian at another x to test default x value
                r = p.jprod(pvec)
                self.assertTrue(array_compare(r, jaccons(x+1.5).dot(pvec), thresh=10 ** (-places)), msg="Wrong jprod r value 2")
            for v in vs:
                # Test J.T products against v (correct dimension)
                r = p.jprod(v, x=x, transpose=True)
                self.assertTrue(array_compare(r, jaccons(x).T.dot(v), thresh=10 ** (-places)), msg="Wrong jprod r value 3")
                _, _ = p.cons(x + 1.5, gradient=True)  # evaluate Jacobian at another x to test default x value
                r = p.jprod(v, transpose=True)
                self.assertTrue(array_compare(r, jaccons(x+1.5).T.dot(v), thresh=10 ** (-places)), msg="Wrong jprod r value 4")
            # hess
            for v in vs:
                H = p.hess(x, v=v)
                self.assertTrue(array_compare(H, hesslag(x, v), thresh=10 ** (-places)), msg="Wrong hess H value")
            # ihess
            H = p.ihess(x)
            self.assertTrue(array_compare(H, hess(x), thresh=10 ** (-places)), msg="Wrong ihess H value 1")
            H = p.ihess(x, cons_index=0)
            self.assertTrue(array_compare(H, hesscons(x), thresh=10 ** (-places)), msg="Wrong ihess H value 2")
            # hprod
            for pvec in ps:
                for v in vs:
                    r = p.hprod(pvec, x=x, v=v)
                    self.assertTrue(array_compare(r, hesslag(x, v).dot(pvec), thresh=10 ** (-places)),
                                    msg="Wrong hprod r value for p = %s" % str(pvec))
                    _ = p.hess(x+1.5, v=v-0.2)  # evaluate Hessian at another x, to test default x value
                    r = p.hprod(pvec)
                    self.assertTrue(array_compare(r, hesslag(x+1.5, v-0.2).dot(pvec), thresh=10 ** (-places)),
                                    msg="Wrong hprod r value for p = %s" % str(pvec))
            # hjprod
            y0 = 3.5
            for pvec in ps:
                for v in vs:
                    r = p.hjprod(pvec, y0, x=x, v=v)
                    self.assertTrue(array_compare(r, hessjohn(y0, x, v).dot(pvec), thresh=10 ** (-places)),
                                    msg="Wrong hjprod r value for p = %s" % str(pvec))
                    #_ = p.hessj(x+1.5, v=v-0.2) # evaluate Hessian of John function at another x, to test default x value
                    #r = p.hjprod(y0, pvec)
                    #self.assertTrue(array_compare(r, hessjohn(y0, x+1.5, v-0.2).dot(pvec), thresh=10 ** (-places)),
                    #                msg="Wrong hjprod r value for p = %s" % str(pvec))
            # gradhess
            for v in vs:
                g, J, H = p.gradhess(x, v=v)
                self.assertTrue(array_compare(g, gradlag(x, v), thresh=10 ** (-places)), msg="Wrong gradhess g value 1")
                self.assertTrue(array_compare(J, jaccons(x), thresh=10 ** (-places)), msg="Wrong gradhess J value 1")
                self.assertTrue(array_compare(H, hesslag(x, v), thresh=10 ** (-places)), msg="Wrong gradhess H value 1")
                g, J, H = p.gradhess(x, v=v, gradient_of_lagrangian=False)
                self.assertTrue(array_compare(g, grad(x), thresh=10 ** (-places)), msg="Wrong gradhess g value 2")
                self.assertTrue(array_compare(J, jaccons(x), thresh=10 ** (-places)), msg="Wrong gradhess J value 2")
                self.assertTrue(array_compare(H, hesslag(x, v), thresh=10 ** (-places)), msg="Wrong gradhess H value 2")

        stats = p.report()
        num_xs = 4
        self.assertEqual(stats['f'], (3 + 2 * len(vs)) * num_xs, msg="Wrong stat f")
        self.assertEqual(stats['g'], (3 + 4 * len(vs)) * num_xs, msg="Wrong stat g")
        self.assertEqual(stats['H'], (1 + 3 * len(vs) + 3 * len(vs) * len(ps)) * num_xs, msg="Wrong stat H")
        self.assertEqual(stats['Hprod'], (3 * len(vs) * len(ps)) * num_xs, msg="Wrong stat Hprod")
        self.assertEqual(stats['c'], (5 + len(vs) + len(ps)) * num_xs, msg="Wrong stat c")
        self.assertEqual(stats['cg'], (4 + 6 * len(vs) + 2 * len(ps)) * num_xs, msg="Wrong stat cg")
        self.assertEqual(stats['cH'], (1 + 3 * len(vs) + 3 * len(ps) * len(vs)) * num_xs, msg="Wrong stat cH")


def box2_res(x):  # BOX2 residual
    r = np.zeros((10,))
    for i in range(10):
        t = 0.1*(i+1)
        r[i] = np.exp(-t*x[0])-np.exp(-t*x[1])-x[2]*(np.exp(-t)-np.exp(-10*t))
    return r

def box2_jac(x):  # BOX2 Jacobian
    J = np.zeros((10,3))
    for i in range(10):
        t = 0.1*(i+1)
        J[i,0] = -t*np.exp(-t*x[0])
        J[i,1] = t*np.exp(-t*x[1])
        J[i,2] = -(np.exp(-t)-np.exp(-10*t))
    return J

def box2_obj(x):  # BOX2 objective
    r = box2_res(x)
    return r.dot(r)

def box2_grad(x):  # Gradient of BOX2 objective
    r = box2_res(x)
    J = box2_jac(x)
    return 2*J.T.dot(r)


class TestBOX2_with_fixed(unittest.TestCase):
    def runTest(self):
        # pycutest.clear_cache('BOX2')
        p = pycutest.import_problem('BOX2', drop_fixed_variables=False)
        # Some test vectors
        xs = [p.x0, np.ones((p.n,)), -np.ones((p.n)), 0.2*np.arange(p.n), np.sin(np.arange(p.n))-np.cos(np.arange(p.n))]

        for x in xs:
            places = 8  # places accuracy for comparing floats
            print("Trying x =", x)
            # objcons
            f, c = p.objcons(x)
            self.assertAlmostEqual(f, box2_obj(x), places=places, msg="Wrong objcons f value")
            self.assertIsNone(c, msg="objcons c value should be None")
            # obj
            f = p.obj(x)
            self.assertAlmostEqual(f, box2_obj(x), places=places, msg="Wrong obj f value 1")
            f, g = p.obj(x, gradient=True)
            self.assertAlmostEqual(f, box2_obj(x), places=places, msg="Wrong obj f value 2")
            self.assertTrue(array_compare(g, box2_grad(x), thresh=10**(-places)), msg="Wrong obj g value 2")
            # grad
            g = p.grad(x)
            self.assertTrue(array_compare(g, box2_grad(x), thresh=10**(-places)), msg="Wrong grad g value")
            # cons
            c = p.cons(x)
            self.assertIsNone(c, msg="cons should be None")
            # lagjac
            g, J = p.lagjac(x)
            self.assertTrue(array_compare(g, box2_grad(x), thresh=10 ** (-places)), msg="Wrong lagjac g value")
            self.assertIsNone(J, msg="lagjac J should be None")
            # jprod
            r = p.jprod(x)
            self.assertIsNone(r, msg="jprod r should be None")


class TestBOX2_with_free(unittest.TestCase):
    def runTest(self):
        # pycutest.clear_cache('BOX2')
        p = pycutest.import_problem('BOX2')
        # Some test vectors
        xs = [p.x0, np.ones((p.n,)), -np.ones((p.n)), 0.2*np.arange(p.n), np.sin(np.arange(p.n))-np.cos(np.arange(p.n))]

        obj = lambda x: box2_obj(np.array([x[0], x[1], 1.0]))
        grad = lambda x: box2_grad(np.array([x[0], x[1], 1.0]))[:-1]

        for x in xs:
            places = 8  # places accuracy for comparing floats
            print("Trying x =", x)
            # objcons
            f, c = p.objcons(x)
            self.assertAlmostEqual(f, obj(x), places=places, msg="Wrong objcons f value")
            self.assertIsNone(c, msg="objcons c value should be None")
            # obj
            f = p.obj(x)
            self.assertAlmostEqual(f, obj(x), places=places, msg="Wrong obj f value 1")
            f, g = p.obj(x, gradient=True)
            self.assertAlmostEqual(f, obj(x), places=places, msg="Wrong obj f value 2")
            self.assertTrue(array_compare(g, grad(x), thresh=10**(-places)), msg="Wrong obj g value 2")
            # grad
            g = p.grad(x)
            self.assertTrue(array_compare(g, grad(x), thresh=10**(-places)), msg="Wrong grad g value")
            # cons
            c = p.cons(x)
            self.assertIsNone(c, msg="cons should be None")
            # lagjac
            g, J = p.lagjac(x)
            self.assertTrue(array_compare(g, grad(x), thresh=10 ** (-places)), msg="Wrong lagjac g value")
            self.assertIsNone(J, msg="lagjac J should be None")
            # jprod
            r = p.jprod(x)
            self.assertIsNone(r, msg="jprod r should be None")
