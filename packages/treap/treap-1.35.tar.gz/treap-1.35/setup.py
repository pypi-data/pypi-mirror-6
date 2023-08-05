
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

version = '1.35'

from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='treap',
    py_modules=[ 
        'treap',
        'py_treap',
        'nest',
        ],
    cmdclass = {'build_ext': build_ext},
    ext_modules = [
        Extension("pyx_treap", ["pyx_treap.c"]), 
        ],
    version=version,
    description='Python implementation of treaps',
    long_description='''
A set of python modules implementing treaps is provided.

Treaps perform most operations in O(log2n) time, and are innately sorted.
They're very nice for keeping a collection of values that needs to
always be sorted, or for optimization problems in which you need to find
the p best values out of q, when p is much smaller than q.

A module is provided for treaps that enforce uniqueness.

Pure python versions are included, as are Cython-enhanced versions for performance.

Release 1.31 is pylint'd and is known to run on at least CPython 2.x, CPython 3.x
and Pypy, Pypy3 (beta) and Jython.
''',
    author='Daniel Richard Stromberg',
    author_email='strombrg@gmail.com',
    url='http://stromberg.dnsalias.org/~dstromberg/treap/',
    platforms='Cross platform',
    license='Apache v2',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        ],
    )

