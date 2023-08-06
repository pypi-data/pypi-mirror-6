try:
    from setuptools import setup
    use_setuptools = True
except ImportError:
    from distutils.core import setup
    use_setuptools = False

if use_setuptools:
    extra_setup_args = dict(
        tests_require=['nose', 'numpy', 'scipy'],
        test_suite="nose.collector",
        use_2to3=True,
        zip_safe=False
    )
else:
    extra_setup_args = dict()

f = open('README.txt')
try:
    README = f.read()
finally:
    f.close()

setup(
    name='linop',
    version='0.8.2',
    author='Ghislain Vaillant',
    author_email='ghisvail@gmail.com',
    description='A pythonic abstraction for linear mathematical operators',
    long_description=README,
    license='BSD',
    url='https://github.com/ghisvail/linop',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development',
    ],
    keywords=['linear', 'operator', 'mathematics'],
    packages=['linop'],
    **extra_setup_args
)
