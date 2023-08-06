import base
import numpy
import pandas as pd
import unittest

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import pyblock

class pdBlockTest(unittest.TestCase):
    def check_stats(self, data_len, reblock, cov, benchmark):
        bench_slice = numpy.array([x[0] for x in benchmark])
        numpy.testing.assert_array_equal(data_len.index.values, bench_slice)

        bench_slice = numpy.array([x[1] for x in benchmark])
        numpy.testing.assert_array_equal(data_len.values, bench_slice)

        for (ind, key) in [(2,'mean'), (4,'standard error'), (5, 'standard error error')]:
            bench_slice = numpy.array([x[ind] for x in benchmark]).flatten()
            numpy.testing.assert_array_almost_equal(reblock.xs(key, axis=1, level=1).values.flatten(), bench_slice, decimal=8)

        bench_slice = numpy.array([x[3] for x in benchmark]).flatten()
        numpy.testing.assert_array_almost_equal(cov.values.flatten(), bench_slice, decimal=8)
        

class BlockingTests1D(pdBlockTest):
    def setUp(self):
        self.data = pd.Series(base.corr_data(10, 6, 5))
    def tearDown(self):
        del self.data
    def test_pdblock(self):
        (data_len, reblock, cov) = pyblock.pd_utils.reblock(self.data)
        self.check_stats(data_len, reblock, cov, base.reblock_1D)
    def test_pdblock_opt(self):
        (data_len, reblock, cov) = pyblock.pd_utils.reblock(self.data)
        self.assertEqual(pyblock.pd_utils.optimal_block(reblock), base.reblock_1D_opt[0])
        opt = reblock[('data', 'optimal block')]
        self.assertEqual(pyblock.pd_utils.optimal_block(opt), base.reblock_1D_opt[0])
        reblock.loc[base.reblock_1D_opt[0]-1, ('data', 'optimal block')] = '<---'
        with self.assertRaises(ValueError):
            pyblock.pd_utils.optimal_block(reblock)
        reblock[('data', 'optimal block')] = ''
        self.assertEqual(pyblock.pd_utils.optimal_block(opt), float('inf'))
        self.assertTrue(pyblock.pd_utils.reblock_summary(reblock).empty)

class BlockingTests2D(pdBlockTest):
    def setUp(self):
        self.data = pd.DataFrame({1:base.corr_data(10, 6, 5), 2:base.corr_data(10, 6, 7)})
    def tearDown(self):
        del self.data
    def test_pdblock(self):
        (data_len, reblock, cov) = pyblock.pd_utils.reblock(self.data)
        self.check_stats(data_len, reblock, cov, base.reblock_2D)
    def test_pdblock_rows(self):
        data = self.data.T
        (data_len, reblock, cov) = pyblock.pd_utils.reblock(data, axis=1)
        self.check_stats(data_len, reblock, cov, base.reblock_2D)
    def test_pdblock_opt(self):
        (data_len, reblock, cov) = pyblock.pd_utils.reblock(self.data)
        self.assertEqual(pyblock.pd_utils.optimal_block(reblock), max(base.reblock_2D_opt))
        for x in reblock.groupby(level=0, axis=1):
            self.assertEqual(pyblock.pd_utils.optimal_block(x[1]), base.reblock_2D_opt[x[0]-1])
    def test_pdblock_summary(self):
        (data_len, reblock, cov) = pyblock.pd_utils.reblock(self.data)
        summary = pyblock.pd_utils.reblock_summary(reblock)
        opt = base.reblock_2D[max(base.reblock_2D_opt)]
        opt = numpy.array([opt[2], opt[4], opt[5]]).transpose()
        numpy.testing.assert_array_almost_equal(summary.values.flatten(), opt.flatten(), decimal=8)
        summary = pyblock.pd_utils.reblock_summary(reblock[1])
        numpy.testing.assert_array_almost_equal(summary.values.flatten(), opt[0], decimal=8)

class OptimalErrorTest(unittest.TestCase):
    def test1(self):
        data = pd.Series(numpy.random.randn(5), name='rand')
        with self.assertRaises(ValueError):
            pyblock.pd_utils.optimal_block(data)
    def test2(self):
        data = pd.DataFrame({1:numpy.random.randn(5), 2:numpy.random.randn(5)})
        with self.assertRaises(ValueError):
            pyblock.pd_utils.optimal_block(data)

def main():
    unittest.main()

if __name__ == '__main__':

    main()
