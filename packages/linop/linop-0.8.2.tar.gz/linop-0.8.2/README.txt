=====
linop
=====

This project provides a standalone set of classes to abstract the creation 
and management of linear operators, to be used as a common basis for the 
development of advanced mathematical frameworks.

The code base was originally forked from the `pykrylov project 
<https://github.com/dpo/pykrylov>`_ developed by Dominique Orban. This 
project has added missing features such as Python 3 support, a comprehensive 
test suite, bug fixes and feature enhancements.


Requirements
============

* Python 2 (>=2.6) or 3 (>=3.2)
* NumPy


Installation
============

Using pip / easy_install (recommended)::
    
    pip install linop

From the cloned repository or unpacked source distribution::

    python setup.py install


Documentation
=============

The package documentation can be found `here 
<http://pythonhosted.org/linop>`_. The documentation can be built using 
Sphinx. Within the root location of the source directory, run::

    python setup.py build_sphinx

The html documentation will be available in doc/build/html.


Changelog
=========

See the CHANGES.txt file.


Thanks to
=========

A list of contributors to the project is kept updated in the AUTHORS.txt file.


Contributing
============

The code source is released under a permissive license. Anyone is welcome 
to contribute to the improvement of the existing code base.

Please feel free to submit an issue to the bug tracker, clone the repository 
and submit your changes by pull-request.  

The test suite uses `nose <http://nose.readthedocs.org>`_ and can be run with::

    python setup.py test
