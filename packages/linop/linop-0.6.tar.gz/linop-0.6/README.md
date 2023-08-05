=====
linop
=====

linop: a Pythonic abstraction for linear mathematical operators

A friendy fork from the linop module of the 
[pykrylov](https://github.com/dpo/pykrylov) package, developped by 
Dominique Orban <dominique.orban@gmail.com>.

This project means to provde a standalone set of classes to abstract the 
creation and management of linear operators, to be used as a common basis for 
the development of advanced mathematical frameworks.


Requirements
============

* [Python](http://www.python.org>) 2 (>=2.6) or 3 (>=3.2)
* [NumPy](http://www.scipy.org/NumPy)


Installation
============

Using pip / easy_install (recommended):
    
    pip install linop

From the cloned sources:

    python setup.py install


Documentation
=============

The package documentation can be found 
[here](http://pythonhosted.org/linop/). The documentation can be built 
using Sphinx. From the root of the source directory, do:

    python setup.py build_sphinx

The html documentation will be available in doc/build/html.


Changelog
=========

See the [CHANGELOG](./CHANGELOG) file.


Contributing
============

The code source is released under a free software license. Anyone is welcome 
to contribute to the improvement of the existing code base, ideally by filing 
an issue to the bug tracker, cloning the repository and submitting a pull 
request.

The test suite uses [nose](http://nose.readthedocs.org/) and can be run with:

    python setup.py test
    
A list of contributors will be updated in the [AUTHORS](./AUTHORS) file.
