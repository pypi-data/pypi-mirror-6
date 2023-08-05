from __future__ import division
import numpy as np
import logging

__docformat__ = 'restructuredtext'


# Default (null) logger.
null_log = logging.getLogger('linop')
null_log.setLevel(logging.INFO)
null_log.addHandler(logging.NullHandler())


class BaseLinearOperator(object):

    """
    Base class defining the common interface shared by all linear operators.

    A linear operator is a linear mapping x -> A(x) such that the size of the
    input vector x is `nargin` and the size of the output is `nargout`. It can
    be visualized as a matrix of shape (`nargout`, `nargin`). Its type is any
    valid Numpy `dtype`. By default, it has `dtype` `numpy.float` but this can
    be changed to, e.g., `numpy.complex` via the `dtype` keyword argument and
    attribute.

    A logger may be attached to the linear operator via the `logger` keyword
    argument.

    """

    def __init__(self, nargin, nargout, symmetric=False, **kwargs):
        self.__nargin = nargin
        self.__nargout = nargout
        self.__symmetric = symmetric
        self.__shape = (nargout, nargin)
        self.__dtype = kwargs.get('dtype', np.float)
        self._nMatvec = 0

        # Log activity.
        self.logger = kwargs.get('logger', null_log)
        self.logger.info('New linear operator with shape ' + str(self.shape))
        return

    @property
    def nargin(self):
        """The size of an input vector."""
        return self.__nargin

    @property
    def nargout(self):
        """The size of an output vector."""
        return self.__nargout

    @property
    def symmetric(self):
        """Indicate whether the operator is symmetric or not."""
        return self.__symmetric

    @property
    def shape(self):
        """The shape of the operator."""
        return self.__shape

    @property
    def dtype(self):
        """The data type of the operator."""
        return self.__dtype

    @property
    def nMatvec(self):
        """The number of products with vectors computed so far."""
        return self._nMatvec

    def reset_counters(self):
        """Reset operator/vector product counter to zero."""
        self._nMatvec = 0

    def __call__(self, *args, **kwargs):
        # An alias for __mul__.
        return self.__mul__(*args, **kwargs)

    def __mul__(self, x):
        raise NotImplementedError('Please subclass to implement __mul__.')

    def __repr__(self):
        if self.symmetric:
            s = 'Symmetric'
        else:
            s = 'Unsymmetric'
        s += ' <' + self.__class__.__name__ + '>'
        s += ' of type %s' % self.dtype
        s += ' with shape (%d,%d)' % (self.nargout, self.nargin)
        return s


class LinearOperator(BaseLinearOperator):

    """
    Generic linear operator class.

    A linear operator constructed from a `matvec` and (possibly) a
    `matvec_transp` function. If `symmetric` is `True`, `matvec_transp` is
    ignored. All other keyword arguments are passed directly to the superclass.

    """

    def __init__(self, nargin, nargout, matvec, matvec_transp=None, **kwargs):

        super(LinearOperator, self).__init__(nargin, nargout, **kwargs)
        self.__transposed = kwargs.get('transposed', False)
        transpose_of = kwargs.get('transpose_of', None)
        matvec_transp = matvec_transp or kwargs.get('rmatvec', None)

        self.__matvec = matvec

        if self.symmetric:
            self.__H = self
        else:
            if transpose_of is None:
                if matvec_transp is not None:
                    # Create 'pointer' to transpose operator.
                    self.__H = LinearOperator(nargout, nargin,
                                              matvec_transp,
                                              matvec_transp=matvec,
                                              transposed=not self.__transposed,
                                              transpose_of=self,
                                              **kwargs)
                else:
                    self.__H = None
            else:
                # Use operator supplied as transpose operator.
                if isinstance(transpose_of, BaseLinearOperator):
                    self.__H = transpose_of
                else:
                    msg = 'kwarg transposed_of must be a BaseLinearOperator.'
                    msg += ' Got ' + str(transpose_of.__class__)
                    raise ValueError(msg)

        if self.__H is not None:
            self.rmatvec = self.__H.matvec

        if not issubclass(np.dtype(self.dtype).type, np.complex):
            self.T = self.__H

    @property
    def H(self):
        """The adjoint operator."""
        return self.__H

    def matvec(self, x):
        """
        Matrix-vector multiplication.

        The matvec property encapsulates the matvec routine specified at
        construct time, to ensure the consistency of the input and output
        arrays with the operator's shape.

        """
        x = np.asanyarray(x)
        M, N = self.shape

        # check input data consistency
        try:
            x = x.reshape(N)
        except ValueError:
            msg = 'input array size incompatible with operator dimensions'
            raise ValueError(msg)

        y = self.__matvec(x)

        # check output data consistency
        try:
            y = y.reshape(M)
        except ValueError:
            msg = 'output array size incompatible with operator dimensions'
            raise ValueError(msg)

        return y

    def to_array(self):
        n, m = self.shape
        H = np.empty((n, m))
        for j in xrange(m):
            ej = np.zeros(m)
            ej[j] = 1.0
            H[:, j] = self * ej
        return H

    def __mul_scalar(self, x):
        """Product between a linear operator and a scalar."""
        result_type = np.result_type(self.dtype, type(x))

        if x != 0:
            def matvec(y):
                return x * (self(y))

            def matvec_transp(y):
                return x * (self.H(y))

            return LinearOperator(self.nargin, self.nargout,
                                  symmetric=self.symmetric,
                                  matvec=matvec,
                                  matvec_transp=matvec_transp,
                                  dtype=result_type)
        else:
            return ZeroOperator(self.nargin, self.nargout,
                                dtype=result_type)

    def __mul_linop(self, op):
        """Product between two linear operators."""
        if self.nargin != op.nargout:
            raise ShapeError('Cannot multiply operators together')

        def matvec(x):
            return self(op(x))

        def matvec_transp(x):
            return op.T(self.H(x))

        result_type = np.result_type(self.dtype, op.dtype)

        return LinearOperator(op.nargin, self.nargout,
                              symmetric=False,   # Generally.
                              matvec=matvec,
                              matvec_transp=matvec_transp,
                              dtype=result_type)

    def __mul_vector(self, x):
        """Product between a linear operator and a vector."""
        self._nMatvec += 1
        result_type = np.result_type(self.dtype, x.dtype)
        return self.matvec(x).astype(result_type)

    def __mul__(self, x):
        if np.isscalar(x):
            return self.__mul_scalar(x)
        elif isinstance(x, BaseLinearOperator):
            return self.__mul_linop(x)
        elif isinstance(x, np.ndarray):
            return self.__mul_vector(x)
        else:
            raise ValueError('Cannot multiply')

    def __rmul__(self, x):
        if np.isscalar(x):
            return self.__mul__(x)
        raise ValueError('Cannot multiply')

    def __add__(self, other):
        if not isinstance(other, BaseLinearOperator):
            raise ValueError('Cannot add')
        if self.shape != other.shape:
            raise ShapeError('Cannot add')

        def matvec(x):
            return self(x) + other(x)

        def matvec_transp(x):
            return self.H(x) + other.T(x)

        result_type = np.result_type(self.dtype, other.dtype)

        return LinearOperator(self.nargin, self.nargout,
                              symmetric=self.symmetric and other.symmetric,
                              matvec=matvec,
                              matvec_transp=matvec_transp,
                              dtype=result_type)

    def __neg__(self):
        return self * (-1)

    def __sub__(self, other):
        if not isinstance(other, BaseLinearOperator):
            raise ValueError('Cannot add')
        if self.shape != other.shape:
            raise ShapeError('Cannot add')

        def matvec(x):
            return self(x) - other(x)

        def matvec_transp(x):
            return self.H(x) - other.T(x)

        result_type = np.result_type(self.dtype, other.dtype)

        return LinearOperator(self.nargin, self.nargout,
                              symmetric=self.symmetric and other.symmetric,
                              matvec=matvec,
                              matvec_transp=matvec_transp,
                              dtype=result_type)

    def __truediv__(self, other):
        if np.isscalar(other):
            return self * (1 / other)
        else:
            raise ValueError('Cannot divide')

    def __pow__(self, other):
        if not isinstance(other, int):
            raise ValueError('Can only raise to integer power')
        if other < 0:
            raise ValueError('Can only raise to nonnegative power')
        if self.nargin != self.nargout:
            raise ShapeError('Can only raise square operators to a power')
        if other == 0:
            return IdentityOperator(self.nargin)
        if other == 1:
            return self
        return self * self ** (other - 1)


class IdentityOperator(LinearOperator):

    """Class representing the identity operator of size `nargin`."""

    def __init__(self, nargin, **kwargs):
        if 'symmetric' in kwargs:
            kwargs.pop('symmetric')
        if 'matvec' in kwargs:
            kwargs.pop('matvec')

        super(IdentityOperator, self).__init__(nargin, nargin,
                                               symmetric=True,
                                               matvec=lambda x: x,
                                               **kwargs)


class DiagonalOperator(LinearOperator):

    """
    Class representing a diagonal operator.

    A diagonal linear operator defined by its diagonal `diag` (a Numpy array.)
    The type must be specified in the `diag` argument, e.g.,
    `np.ones(5, dtype=np.complex)` or `np.ones(5).astype(np.complex)`.

    """

    def __init__(self, diag, **kwargs):
        if 'symmetric' in kwargs:
            kwargs.pop('symmetric')
        if 'matvec' in kwargs:
            kwargs.pop('matvec')
        if 'dtype' in kwargs:
            kwargs.pop('dtype')

        diag = np.asarray(diag)
        if diag.ndim != 1:
            msg = "diag array must be 1-d"
            raise ValueError(msg)

        super(DiagonalOperator, self).__init__(diag.shape[0], diag.shape[0],
                                               symmetric=True,
                                               matvec=lambda x: diag * x,
                                               dtype=diag.dtype,
                                               **kwargs)


class MatrixOperator(LinearOperator):

    """
    Class representing a matrix operator.

    A linear operator wrapping the multiplication with a matrix and its
    transpose (real) or conjugate transpose (complex). The operator's dtype
    is the same as the specified `matrix` argument.

    .. versionadded:: 0.3

    """

    def __init__(self, matrix, **kwargs):
        if 'symmetric' in kwargs:
            kwargs.pop('symmetric')
        if 'matvec' in kwargs:
            kwargs.pop('matvec')
        if 'dtype' in kwargs:
            kwargs.pop('dtype')

        if not hasattr(matrix, 'shape'):
            matrix = np.asanyarray(matrix)

        if matrix.ndim != 2:
            msg = "matrix must be 2-d (shape can be [M, N], [M, 1] or [1, N])"
            raise ValueError(msg)

        matvec = matrix.dot
        iscomplex = issubclass(np.dtype(matrix.dtype).type, np.complex)

        symmetric = (np.all(matrix == matrix.conj().T) if iscomplex
                     else np.all(matrix == matrix.T))

        if not symmetric:
            matvec_transp = (matrix.conj().T.dot if iscomplex
                             else matrix.T.dot)
        else:
            matvec_transp = None

        super(MatrixOperator, self).__init__(matrix.shape[1], matrix.shape[0],
                                             symmetric=symmetric,
                                             matvec=matvec,
                                             matvec_transp=matvec_transp,
                                             dtype=matrix.dtype,
                                             **kwargs)


class ZeroOperator(LinearOperator):

    """Class representing the zero operator of shape `nargout`-by-`nargin`."""

    def __init__(self, nargin, nargout, **kwargs):
        if 'matvec' in kwargs:
            kwargs.pop('matvec')
        if 'matvec_transp' in kwargs:
            kwargs.pop('matvec_transp')

        def matvec(x):
            if x.shape != (nargin,):
                msg = 'Input has shape ' + str(x.shape)
                msg += ' instead of (%d,)' % self.nargin
                raise ValueError(msg)
            return np.zeros(nargout)

        def matvec_transp(x):
            if x.shape != (nargout,):
                msg = 'Input has shape ' + str(x.shape)
                msg += ' instead of (%d,)' % self.nargout
                raise ValueError(msg)
            return np.zeros(nargin)

        super(ZeroOperator, self).__init__(nargin, nargout,
                                           matvec=matvec,
                                           matvec_transp=matvec_transp,
                                           **kwargs)


def ReducedLinearOperator(op, row_indices, col_indices):
    """
    Implement reduction of a linear operator (non symmetrical).

    Reduce a linear operator by limiting its input to `col_indices` and its
    output to `row_indices`.

    """

    nargin, nargout = len(col_indices), len(row_indices)
    m, n = op.shape    # Shape of non-reduced operator.

    def matvec(x):
        z = np.zeros(n, dtype=x.dtype)
        z[col_indices] = x[:]
        y = op * z
        return y[row_indices]

    def matvec_transp(x):
        z = np.zeros(m, dtype=x.dtype)
        z[row_indices] = x[:]
        y = op.H * z
        return y[col_indices]

    return LinearOperator(nargin, nargout, matvec=matvec, symmetric=False,
                          matvec_transp=matvec_transp)


def SymmetricallyReducedLinearOperator(op, indices):
    """
    Implement reduction of a linear operator (symmetrical).

    Reduce a linear operator symmetrically by reducing boths its input and
    output to `indices`.

    """

    nargin = len(indices)
    m, n = op.shape    # Shape of non-reduced operator.

    def matvec(x):
        z = np.zeros(n, dtype=x.dtype)
        z[indices] = x[:]
        y = op * z
        return y[indices]

    def matvec_transp(x):
        z = np.zeros(m, dtype=x.dtype)
        z[indices] = x[:]
        y = op * z
        return y[indices]

    return LinearOperator(nargin, nargin, matvec=matvec,
                          symmetric=op.symmetric, matvec_transp=matvec_transp)


class ShapeError(Exception):

    """
    Exception class for handling shape mismatch errors.

    Exception raised when defining a linear operator of the wrong shape or
    multiplying a linear operator with a vector of the wrong shape.

    """

    def __init__(self, value):
        super(ShapeError, self).__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


def PysparseLinearOperator(A):
    """Return a linear operator from a Pysparse sparse matrix."""

    nargout, nargin = A.shape
    try:
        symmetric = A.issym
    except:
        symmetric = A.isSymmetric()

    def matvec(x):
        if x.shape != (nargin,):
            msg = 'Input has shape ' + str(x.shape)
            msg += ' instead of (%d,)' % nargin
            raise ValueError(msg)
        if hasattr(A, '__mul__'):
            return A * x
        Ax = np.empty(nargout)
        A.matvec(x, Ax)
        return Ax

    def matvec_transp(y):
        if y.shape != (nargout,):
            msg = 'Input has shape ' + str(y.shape)
            msg += ' instead of (%d,)' % nargout
            raise ValueError(msg)
        if hasattr(A, '__rmul__'):
            return y * A
        ATy = np.empty(nargin)
        A.matvec_transp(y, ATy)
        return ATy

    return LinearOperator(nargin, nargout, matvec=matvec,
                          matvec_transp=matvec_transp, symmetric=symmetric)


def linop_from_ndarray(A):
    """
    Return a linear operator from a Numpy `ndarray`.

    .. deprecated:: 0.4
        Use :class:`MatrixOperator` or :func:`aslinearoperator` instead.

    """
    return LinearOperator(A.shape[1], A.shape[0],
                          lambda v: np.dot(A, v),
                          matvec_transp=lambda u: np.dot(A.T, u),
                          symmetric=False,
                          dtype=A.dtype)


def aslinearoperator(A):
    """Return A as a LinearOperator.

    'A' may be any of the following types:
    - linop.LinearOperator
    - scipy.LinearOperator
    - ndarray
    - matrix
    - sparse matrix (e.g. csr_matrix, lil_matrix, etc.)
    - any object with .shape and .matvec attributes

    See the :class:`LinearOperator` documentation for additonal information.

    .. versionadded:: 0.4

    """
    from scipy.sparse import isspmatrix

    if isinstance(A, LinearOperator):
        return A

    elif isinstance(A, np.ndarray) or isinstance(A, np.matrix):
        return MatrixOperator(A)

    elif isspmatrix(A):
        return MatrixOperator(A)

    elif hasattr(A, 'shape') and hasattr(A, 'matvec'):

        if hasattr(A, 'matvec_transp'):
            matvec_transp = A.matvec_transp
        elif hasattr(A, 'rmatvec'):
            matvec_transp = A.rmatvec
        else:
            matvec_transp = None

        if hasattr(A, 'dtype'):
            dtype = A.dtype
        else:
            dtype = None

        matvec = A.matvec
        nargout, nargin = A.shape

        return LinearOperator(
            nargin, nargout, symmetric=False, matvec=matvec,
            matvec_transp=matvec_transp, dtype=dtype)

    else:
        raise TypeError('unsupported object type')
