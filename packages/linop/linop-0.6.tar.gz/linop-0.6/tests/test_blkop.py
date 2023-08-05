"""Test suite for the blkop module."""

from __future__ import division
from numpy.testing import TestCase, assert_, assert_equal, assert_raises
import numpy as np
import linop as lo
import linop.blkop as bo
from linop import ShapeError


class TestBlockLinearOperator(TestCase):
    def setUp(self):
        self.A = lo.IdentityOperator(2)
        self.B = lo.MatrixOperator(np.arange(1, 7).reshape([2, 3]))
        self.C = lo.DiagonalOperator(np.arange(3))
        self.D = lo.MatrixOperator(np.arange(6, 0, -1).reshape([3, 2]))

    def test_init(self):
        M = bo.BlockLinearOperator([[self.A, self.B], [self.D, self.C]])
        assert_(M.shape == (5, 5))
        assert_(self.A in M)
        assert_(M[0, 0] is self.A)
        assert_(self.B in M)
        assert_(M[0, 1] is self.B)
        assert_(self.C in M)
        assert_(M[1, 1] is self.C)
        assert_(self.D in M)
        assert_(M[1, 0] is self.D)

        M = bo.BlockLinearOperator([[self.A, self.B], [self.C]], symmetric=True)
        assert_(M.shape == (5, 5))
        assert_(self.B.T in M)
        assert_(M[1, 0] is self.B.T)

        M = bo.BlockLinearOperator([[self.A, self.B], [self.A, self.B]])
        assert_(M.shape == (4, 5))

        assert_raises(ValueError, bo.BlockLinearOperator,
                      [self.A, self.C, self.D, self.C])
        assert_raises(ShapeError, bo.BlockLinearOperator,
                      [[self.A, self.C], [self.D, self.C]])
        assert_raises(ShapeError, bo.BlockLinearOperator,
                      [[self.A, self.B], [self.B, self.C]])
        assert_raises(ValueError, bo.BlockLinearOperator,
                      [[self.A, self.B], [self.B]], symmetric=True)

    def test_runtime(self):
        M = bo.BlockLinearOperator([[self.A, self.B], [self.D, self.C]])
        matrix_M = np.array([[1, 0, 1, 2, 3],
                             [0, 1, 4, 5, 6],
                             [6, 5, 0, 0, 0],
                             [4, 3, 0, 1, 0],
                             [2, 1, 0, 0, 2]])
        x = np.ones(M.shape[1])
        assert_equal(M * x, np.dot(matrix_M, x))
        x = np.ones(M.T.shape[1])
        assert_equal(M.T * x, np.dot(matrix_M.T, x))

        M = bo.BlockLinearOperator([[self.A, self.B], [self.C]], symmetric=True)
        matrix_M = np.array([[1, 0, 1, 2, 3],
                             [0, 1, 4, 5, 6],
                             [1, 4, 0, 0, 0],
                             [2, 5, 0, 1, 0],
                             [3, 6, 0, 0, 2]])
        x = np.ones(M.shape[1])
        assert_equal(M * x, np.dot(matrix_M, x))
        x = np.ones(M.T.shape[1])
        assert_equal(M.T * x, np.dot(matrix_M.T, x))

        M = bo.BlockLinearOperator([[self.A, self.B], [self.A, self.B]])
        matrix_M = np.array([[1, 0, 1, 2, 3],
                             [0, 1, 4, 5, 6],
                             [1, 0, 1, 2, 3],
                             [0, 1, 4, 5, 6]])
        x = np.ones(M.shape[1])
        assert_equal(M * x, np.dot(matrix_M, x))
        x = np.ones(M.T.shape[1])
        assert_equal(M.T * x, np.dot(matrix_M.T, x))

    def test_dtypes(self):
        pass


class TestBlockDiagonalOperator(TestCase):
    def setUp(self):
        self.A = lo.IdentityOperator(2)
        self.B = lo.MatrixOperator(np.arange(1, 7).reshape([2, 3]))
        self.C = lo.DiagonalOperator(np.arange(3))
        self.D = lo.MatrixOperator(np.arange(6, 0, -1).reshape([3, 2]))

    def test_init(self):
        M = bo.BlockDiagonalLinearOperator([self.A, self.C])
        assert_(M.shape == (5, 5))
        assert_(M.symmetric is True)
        assert_(self.A in M)
        assert_(M[0] is self.A)
        assert_(self.C in M)
        assert_(M[1] is self.C)

        M = bo.BlockDiagonalLinearOperator([self.A, self.D*self.B])
        assert_(M.symmetric is False)

        assert_raises(ValueError, bo.BlockDiagonalLinearOperator,
                      [[self.A, self.C]])

    def test_runtime(self):
        M = bo.BlockDiagonalLinearOperator([self.A, self.C])
        matrix_M = np.array([[1, 0, 0, 0, 0],
                             [0, 1, 0, 0, 0],
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 1, 0],
                             [0, 0, 0, 0, 2]])
        x = np.ones(M.shape[1])
        assert_equal(M * x, np.dot(matrix_M, x))
        x = np.ones(M.T.shape[1])
        assert_equal(M.T * x, np.dot(matrix_M.T, x))


class TestBlockHorizontalOperator(TestCase):
    def setUp(self):
        self.A = lo.IdentityOperator(2)
        self.B = lo.MatrixOperator(np.arange(1, 7).reshape([2, 3]))
        self.C = lo.DiagonalOperator(np.arange(3))
        self.D = lo.MatrixOperator(np.arange(6, 0, -1).reshape([3, 2]))

    def test_init(self):
        M = bo.BlockHorizontalLinearOperator([self.A, self.B])
        assert_(M.shape == (2, 5))
        assert_(M.symmetric is False)
        assert_(self.A in M)
        assert_(M[0, 0] is self.A)
        assert_(self.B in M)
        assert_(M[0, 1] is self.B)
        assert_raises(ShapeError, bo.BlockHorizontalLinearOperator,
                      [self.A, self.D])
        assert_raises(ValueError, bo.BlockHorizontalLinearOperator,
                      [[self.A, self.B]])

    def test_runtime(self):
        M = bo.BlockHorizontalLinearOperator([self.A, self.B])
        matrix_M = np.array([[1, 0, 1, 2, 3],
                             [0, 1, 4, 5, 6]])
        x = np.ones(M.shape[1])
        assert_equal(M * x, np.dot(matrix_M, x))
        x = np.ones(M.T.shape[1])
        assert_equal(M.T * x, np.dot(matrix_M.T, x))


class TestBlockVerticalOperator(TestCase):
    def setUp(self):
        self.A = lo.IdentityOperator(2)
        self.B = lo.MatrixOperator(np.arange(1, 7).reshape([2, 3]))
        self.C = lo.DiagonalOperator(np.arange(3))
        self.D = lo.MatrixOperator(np.arange(6, 0, -1).reshape([3, 2]))

    def test_init(self):
        M = bo.BlockVerticalLinearOperator([self.A, self.D])
        assert_(M.shape == (5, 2))
        assert_(M.symmetric is False)
        assert_(self.A in M)
        assert_(M[0, 0] is self.A)
        assert_(self.D in M)
        assert_(M[1, 0] is self.D)
        assert_raises(ShapeError, bo.BlockVerticalLinearOperator,
                      [self.A, self.B])
        assert_raises(ValueError, bo.BlockVerticalLinearOperator,
                      [[self.A, self.D]])

    def test_runtime(self):
        M = bo.BlockVerticalLinearOperator([self.A, self.D])
        matrix_M = np.array([[1, 0],
                             [0, 1],
                             [6, 5],
                             [4, 3],
                             [2, 1]])
        x = np.ones(M.shape[1])
        assert_equal(M * x, np.dot(matrix_M, x))
        x = np.ones(M.T.shape[1])
        assert_equal(M.T * x, np.dot(matrix_M.T, x))
