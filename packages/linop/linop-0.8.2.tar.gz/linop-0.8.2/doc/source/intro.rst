Introduction
============

When working towards a solution of a linear system :math:`Ax=b`, Krylov methods
do not need to know anything structural about the matrix :math:`A`; all they
require is the ability to form matrix-vector products :math:`v \mapsto Av` and,
possibly, products with the transpose :math:`u \mapsto A^T u`. In essence, we
do not even need the *operator* :math:`A` to be represented by a matrix at all;
we simply consider it as a linear function.

In PyKrylov, such linear functions can be conveniently packaged as
``LinearOperator`` objects. If ``A`` is an instance of ``LinearOperator`` and
represents the "matrix" :math:`A` above, we may computes matrix-vector products
by simply writing ``A*v``, where ``v`` is a Numpy array of appropriate size.

Similarly, if a Krylov method requires access to the transpose operator
:math:`A^T`, it is conveniently available as ``A.T`` and products may be
computed using, e.g., ``A.T * u``. If ``A`` represents a symmetric operator
:math:`A = A^T`, then ``A.T`` is simply a reference to ``A`` itself.

More generally, since :math:`(A^T)^T = A`, the Python statement ``A.T.T is A``
always evaluates to ``True``, which means that they are the *same* object.

In the next two sections, we describe generic linear operators and linear
operators constructed by blocks.
