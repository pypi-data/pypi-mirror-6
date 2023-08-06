.. Description of linear operators
.. _linop-page:


The :mod:`linop` Module
=======================

.. automodule:: linop.linop

Base Class for Linear Operators
-------------------------------

All linear operators derive from the base class ``BaseLinearOperator``. This
base class is not meant to be used directly to define linear operators, other
than by subclassing to define classes of more specific linear operators.

.. autoclass:: BaseLinearOperator
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

Linear Operators Defined by Functions
-------------------------------------

It is intuitive to define an operator by its *action* on vectors. The
``LinearOperator`` class takes arguments ``matvec`` and ``rmatvec`` to
define the action of the operator and of its transpose.

Here is a simple example:

.. code-block:: python

    import numpy as np
    A = LinearOperator(nargin=3, nargout=3, matvec=lambda v: 2*v, symmetric=True)
    B = LinearOperator(nargin=4, nargout=3, matvec=lambda v: np.arange(3)*v[:3],
                       rmatvec=lambda v: np.concatenate((np.arange(3)*v, np.zeros(1))))

The API also supports using the keyword argument ``matvec_transp`` to replace 
to maintain compatibility with pysparse-style instantiation.

Here, ``A`` represents the operator :math:`2I`, where :math:`I` is the identity
and ``B`` could be represented by the matrix

.. math::

    \begin{bmatrix}
      1 & & & \\
        & 2 & & \\
        & & 3 & 0 \\
    \end{bmatrix}.

Note that any callable object can be used to pass values for ``matvec`` and
``rmatvec``. For example :

.. code-block:: python

    def func(v):
        return np.arange(3) * v

    class MyClass(object):
        def __call__(self, u):
            return np.concatenate((np.arange(3)*v, np.zeros(1)))

    myobject = MyClass()
    B = LinearOperator(nargin=4, nargout=3, matvec=func, rmatvec=myobject)


is perfectly valid. Based on this example, arbitrarily complex operators may be
built.

.. autoclass:: LinearOperator
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

Simple Common Predefined Linear Operators
-----------------------------------------

A few common operators are predefined, such as the identity, the zero operator,
and a class for diagonal operators.

.. autoclass:: IdentityOperator
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: ZeroOperator
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

Diagonal operators are simply defined by their diagonal as a Numpy array. For
example:

.. code-block:: python

    d = np.random.random(10)
    D = DiagonalOperator(d)

.. autoclass:: DiagonalOperator
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

Matrix operators wraps calls to the dot and tranposed dot product of the
provided Numpy array. For example:

.. code-block:: python

    m = np.arange(12).reshape([4, 3])
    M = MatrixLinearOperator(m)

.. autoclass:: MatrixLinearOperator
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

Convenience Functions
---------------------

Typically, linear operators don't come alone and an operator is often used to
define other operators. An example is reduction. Suppose :math:`A` is a linear
operator from :math:`\mathbb{R}^n` into :math:`\mathbb{R^m}`,
:math:`\mathcal{Z}` is a subspace of :math:`\mathbb{R}^n` and
:math:`\mathcal{Y}` is a subspace of :math:`\mathbb{R}^m`. Sometimes it is
useful to consider :math:`A` restricted to :math:`\mathcal{Z}` and
co-restricted to :math:`\mathcal{Y}`. Assuming that :math:`A` is a matrix
representing the linear operator and :math:`Z` and :math:`Y` are matrices whose
columns form bases of the subspaces :math:`\mathcal{Z}` and
:math:`\mathcal{Y}`, respectively, then the restricted operator may be written
:math:`Y^T A Z`.

A simple version of this type of reduction is where we only consider a subset
of the rows and columns of the matrix :math:`A`, which corresponds to subspaces
:math:`\mathcal{Z}` and :math:`\mathcal{Y}` aligned with the axes of
coordinates.

Note that by default, the reduced linear operator is considered to be
non-symmetric even if the original operator was symmetric.

.. autofunction:: ReducedLinearOperator

A special case of this type of reduction is when ``row_indices`` and
``col_indices`` are the same. This is often useful in combination with square
symmetric operators. In this case, the reduced operator possesses the same
symmetry as the original operator.

.. autofunction:: SymmetricallyReducedLinearOperator

An obvious use case of linear operators is matrices themselves! The following
convenience functions allows to build linear operators from various
matrix-like input, such as `Pysparse <http://pysparse.sf.net>`_ sparse
matrices or Numpy arrays.

.. autofunction:: PysparseLinearOperator

.. autofunction:: linop_from_ndarray

.. autofunction:: aslinearoperator

Aliases
-------

.. versionadded:: 0.5

Shorter aliases to some linear operators are now available and listed below:

* `MatrixOperator` for :class:`MatrixLinearOperator`
* `aslinop` for :func:`aslinearoperator`


Exceptions
----------

.. autoexception:: ShapeError

Operations with operators
-------------------------

Linear operators, whether defined by blocks or not, may be added together or
composed following the usual rules of linear algebra. An operator may be
multiplied by a scalar or by another operator. Operators of the same shape may
be added or subtracted. Those operations are essentially free in the sense that
a new linear operator results of them, which encapsulates the appropriate rules
for multiplication by a vector. It is only when the resulting operator is
applied to a vector that the appropriate chain of operations is applied. For
example:

.. code-block:: python

    AB = A * B
    AA = A * A.T
    G  = E + 2 * B.T * B
