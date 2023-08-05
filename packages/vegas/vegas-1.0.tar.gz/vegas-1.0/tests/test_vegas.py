# Created by G. Peter Lepage (Cornell University) in 12/2013.
# Copyright (c) 2013 G. Peter Lepage. 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version (see <http://www.gnu.org/licenses/>).
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from vegas import * 
import math
import numpy as np
from numpy.testing import assert_allclose as np_assert_allclose
import unittest


class TestAdaptiveMap(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        " AdaptiveMap(...) "
        m = AdaptiveMap(grid=[[0, 1], [2, 4]])
        np_assert_allclose(m.grid, [[0, 1], [2, 4]])
        np_assert_allclose(m.inc, [[1], [2]])
        m = AdaptiveMap(grid=[[0, 1], [-2, 4]], ninc=2)
        np_assert_allclose(m.grid, [[0, 0.5, 1.], [-2., 1., 4.]])
        np_assert_allclose(m.inc, [[0.5, 0.5], [3., 3.]])
        self.assertEqual(m.dim, 2)
        self.assertEqual(m.ninc, 2)
        m = AdaptiveMap([[0, 0.4, 1], [-2, 0., 4]], ninc=4)
        np_assert_allclose(
            m.grid, 
            [[0, 0.2, 0.4, 0.7, 1.], [-2., -1., 0., 2., 4.]]
            )
        np_assert_allclose(m.inc, [[0.2, 0.2, 0.3, 0.3], [1, 1, 2, 2]])
        self.assertEqual(m.dim, 2)
        self.assertEqual(m.ninc, 4)

    def test_map(self):
        " map(...) "
        m = AdaptiveMap(grid=[[0, 1, 3], [-2, 0, 6]])
        # 5 y values
        y = np.array(
            [[0, 0], [0.25, 0.25], [0.5, 0.5], [0.75, 0.75], [1.0, 1.0]]
            )
        x = np.empty(y.shape, float)
        jac = np.empty(y.shape[0], float)
        m.map(y, x, jac)
        np_assert_allclose(
            x,
            [[0, -2], [0.5, -1], [1, 0], [2, 3], [3, 6]]
            )
        np_assert_allclose(
            jac,
            [8, 8, 48, 48, 48]
            )
        np_assert_allclose(m(y), x)
        np_assert_allclose(m.jac(y), jac)

    def test_region(self):
        " region(...) "
        m = AdaptiveMap(grid=[[0, 1, 3], [-2, 0, 6]])
        np_assert_allclose(m.region(0), [0, 3])
        np_assert_allclose(m.region(1), [-2, 6])
        np_assert_allclose(m.region(), [[0, 3], [-2, 6]])

    def test_settings(self):
        " settings(...) "
        m = AdaptiveMap(grid=[[0, 1, 3], [-2, 0, 6]], ninc=4)
        output = "    grid[ 0] = [ 0.   0.5  1.   2.   3. ]\n"
        output += "    grid[ 1] = [-2. -1.  0.  3.  6.]\n"
        self.assertEqual(m.settings(5), output)
        output = "    grid[ 0] = [ 0.5  2. ]\n"
        output += "    grid[ 1] = [-1.  3.]\n"
        self.assertEqual(m.settings(2), output)

    def test_training_data_adapt(self):
        "add_training_data(...)  adapt(...) "

        # change ninc; no adaptation -- already adapted
        m = AdaptiveMap([[0, 2], [-1, 1]], ninc=2)
        y = np.array([[0.25, 0.25], [0.75, 0.75]])
        f = m.jac(y)
        m.add_training_data(y, f)
        m.adapt(alpha=1.5)
        np_assert_allclose(m.grid, [[0., 1., 2.], [-1, 0, 1]])

        # no adaptation -- alpha = 0
        m = AdaptiveMap([[0, 1.5, 2], [-1, 0, 1]])
        y = np.array([[0.25, 0.25], [0.75, 0.75]])
        f = m.jac(y)
        m.add_training_data(y, f)
        m.adapt(alpha=0.0)
        np_assert_allclose(m.grid, [[0, 1.5, 2], [-1, 0, 1]])

        # Adapt to functions:
        # Place y values at 2-pt Gaussian quadrature
        # abscissas so training is equivalent to 
        # an integral for functions that are linear
        # or quadratic (or a superposition). This
        # simulates random y's spread uniformly
        # over space. ygauss below is for ninc=2,
        # with two abscissas per increment.
        g = 1. /3.**0.5 
        ygauss = [(1-g)/4., (1+g)/4, (3-g)/4, (3+g)/4.]

        m = AdaptiveMap([[0, 2]], ninc=2)
        y = np.array([[yi] for yi in ygauss])
        def F(x):
            return x[:, 0] ** 2
        for i in range(60):
            f = F(m(y)) * m.jac(y)
            m.add_training_data(y, f)
            m.adapt(alpha=2.)
        np_assert_allclose(m.grid, [[0, 2./2.**(1./3.), 2.]])

        m = AdaptiveMap([[0, 2], [0, 4]], ninc=2)
        y = np.array([[yi, yj] for yi in ygauss for yj in ygauss])
        def F(x):
            return x[:, 0] * x[:, 1] ** 2
        for i in range(60):
            f = F(m(y)) * m.jac(y)
            m.add_training_data(y, f)
            m.adapt(alpha=2.)
        np_assert_allclose(
            m.grid, 
            [[0, 2. * 2.**(-0.5), 2.], [0, 4. * 2**(-1./3.), 4.]]
            )

        # same again, with no smoothing
        m = AdaptiveMap([[0, 2], [0, 4]], ninc=2)
        y = np.array([[yi, yj] for yi in ygauss for yj in ygauss])
        def F(x):
            return x[:, 0] * x[:, 1] ** 2
        for i in range(20):
            f = F(m(y)) * m.jac(y)
            m.add_training_data(y, f)
            m.adapt(alpha=-2.)
        np_assert_allclose(
            m.grid, 
            [[0, 2. * 2.**(-0.5), 2.], [0, 4. * 2**(-1./3.), 4.]]
            )

class TestRunningWAvg(unittest.TestCase):
    def setUp(self):
        pass 

    def tearDown(self):
        pass 

    def test_all(self):
        " RunningWavg "
        a = RunningWAvg()
        a.add(gvar.gvar(1, 1))
        a.add(gvar.gvar(2, 2))
        a.add(gvar.gvar(3, 3))
        np_assert_allclose(a.mean, 1.346938775510204)
        np_assert_allclose(a.sdev, 0.8571428571428571)
        self.assertEqual(a.dof, 2)
        np_assert_allclose(a.chi2, 0.5306122448979592)
        np_assert_allclose(a.Q, 0.7669711269557102)
        self.assertEqual(str(a), '1.35(86)')
        s = [
            "itn   integral        wgt average     chi2/dof        Q",
            "-------------------------------------------------------",
            "  1   1.0(1.0)        1.0(1.0)            0.00     1.00",
            "  2   2.0(2.0)        1.20(89)            0.20     0.65",
            "  3   3.0(3.0)        1.35(86)            0.27     0.77",
            ""
            ]
        self.assertEqual(a.summary(), '\n'.join(s))


class TestIntegrator(unittest.TestCase):
    def setUp(self):
        pass 

    def tearDown(self):
        pass 

    def test_init(self):
        " Integrator "
        I = Integrator([[0.,1.],[-1.,1.]], neval=234, nitn=123)
        self.assertEqual(I.neval, 234)
        self.assertEqual(I.nitn, 123)
        for k in Integrator.defaults:
            if k in ['neval', 'nitn']:
                self.assertNotEqual(getattr(I,k), Integrator.defaults[k])
            elif k not in ['map']:
                self.assertEqual(getattr(I,k), Integrator.defaults[k])
        np.testing.assert_allclose(I.map.grid[0], [0., 1.])
        np.testing.assert_allclose(I.map.grid[1], [-1., 1.])
        lines = [
            'Integrator Settings:',
            '    234 (max) integrand evaluations in each of 123 iterations',
            '    number of:  strata/axis = 7  increments/axis = 21',
            '                h-cubes = 49  evaluations/h-cube = 2 (min)',
            '                h-cubes/vector = 100',
            '    adapt_to_errors = False',
            '    damping parameters: alpha = 0.5  beta= 0.75',
            '    limits: h-cubes < 5e+08  evaluations/h-cube < 1e+07',
            '    accuracy: relative = 0  absolute accuracy = 0',
            '',
            '    axis 0 covers (0.0, 1.0)',
            '    axis 1 covers (-1.0, 1.0)',
            '',
            ]
        for i, l in enumerate(I.settings().split('\n')):
            self.assertEqual(l, lines[i])

    def test_set(self):
        " set "
        new_defaults = dict(
            map=AdaptiveMap([[1,2],[0,1]]),
            fcntype='vectpr', # default integrand type
            neval=100,       # number of evaluations per iteration
            maxinc_axis=100,  # number of adaptive-map increments per axis
            nhcube_vec=10,    # number of h-cubes per vector
            max_nhcube=5e2,    # max number of h-cubes
            max_neval_hcube=1e1, # max number of evaluations per h-cube
            nitn=100,           # number of iterations
            alpha=0.35,
            beta=0.25,
            adapt_to_errors=True,
            rtol=0.1,
            atol=0.2,
            analyzer=reporter(5),
            )
        I = Integrator([[1,2]])
        old_defaults = I.set(**new_defaults)
        for k in new_defaults:
            if k == 'map':
                np_assert_allclose(I.map.grid, new_defaults['map'].grid)
            else:
                self.assertEqual(getattr(I,k), new_defaults[k])

    def test_volume(self):
        " integrate 1 "
        def f(x):
            return 2.
        I = Integrator([[-1, 1], [0, 4]])
        r = I(f)
        np_assert_allclose(r.mean, 16)
        self.assertTrue(r.sdev < 1e-6)

    def test_scalar(self):
        " integrate scalar fcn "
        def f(x):
            return (math.sin(x[0]) ** 2 + math.cos(x[1]) ** 2) / math.pi ** 2
        I = Integrator([[0, math.pi], [-math.pi/2., math.pi/2.]])
        r = I(f, neval=10000)
        self.assertTrue(abs(r.mean - 1.) < 5 * r.sdev)
        self.assertTrue(r.Q > 1e-3)

    def test_vector(self):
        " integrate vector fcn "
        class f_vec(VecIntegrand):
            def __call__(self, x, f, nx):
                for i in range(nx):
                    f[i] = (
                        math.sin(x[i, 0]) ** 2 + math.cos(x[i, 1]) ** 2
                        ) / math.pi ** 2
        I = Integrator([[0, math.pi], [-math.pi/2., math.pi/2.]])
        r = I(f_vec(), neval=10000)
        self.assertTrue(abs(r.mean - 1.) < 5 * r.sdev)
        self.assertTrue(r.Q > 1e-3)
        self.assertTrue(r.sdev < 1e-3)

    def test_adapt_to_errors(self):
        " use adapt_to_errors "
        def f(x):
            return (math.sin(x[0]) ** 2 + math.cos(x[1]) ** 2) / math.pi ** 2
        I = Integrator(
            [[0, math.pi], [-math.pi/2., math.pi/2.]], 
            adapt_to_errors=True,
            )
        r = I(f, neval=10000)
        self.assertTrue(abs(r.mean - 1.) < 5 * r.sdev)
        self.assertTrue(r.Q > 1e-3)
        self.assertTrue(r.sdev < 1e-3)

    def test_adaptive(self):
        " adaptive? "
        def f(x): 
            dx2 = 0 
            for i in range(4): 
                dx2 += (x[i] - 0.5) ** 2
            return math.exp(-dx2 * 100.) * 1013.2118364296088
        I = Integrator(4 * [[0, 1]])
        r0 = I(f, neval=10000, nitn=10)
        r1 = I(f, neval=10000, nitn=10)
        self.assertTrue(r0.itn_results[0].sdev / 30 > r1.itn_results[-1].sdev)
        self.assertTrue(r0.itn_results[0].sdev < 1.)
        self.assertTrue(r1.itn_results[-1].sdev < 0.01)
        self.assertTrue(r1.Q > 1e-3)

if __name__ == '__main__':
    unittest.main()