
import os
import sys
import subprocess

from setuptools import setup
#from distutils.extension import Extension

version = '1.38'

def build_ext(*args, **kwargs):
    from Cython.Distutils import build_ext
    return build_ext(*args, **kwargs)


def is_newer(filename1, filename2):
    '''Return True if filename1 is newer than filename2'''
    time1 = os.stat(filename1).st_mtime
    time2 = os.stat(filename2).st_mtime

    if time1 > time2:
        return True
    else:
        return False


def m4_it(infilename, outfilename, define):
    '''
    This is make-like.
    If outfilename doesn't exit, create it using m4.
    If outfilename exists but is older than infilename, recreate it using m4.
    '''
    build_it = False
    if os.path.exists(outfilename):
        if is_newer(infilename, outfilename):
            # outfilename exists, but is older than infilename, build it
            build_it = True
    else:
        # outfilename does not exist, build it
        build_it = True

    if build_it:
        try:
            #subprocess.check_call('m4 -Dpy=1 < m4_treap.m4 > py_treap.py', shell=True)
            subprocess.check_call('m4 -D"%s"=1 < "%s" > "%s"' % (define, infilename, outfilename), shell=True)
        except subprocess.CalledProcessError:
            sys.stderr.write('You need m4 on your path to build this code\n')
            sys.exit(1)


m4_it('m4_treap.m4', 'py_treap.py', 'py')
m4_it('m4_treap.m4', 'pyx_treap.pyx', 'pyx')

#from distutils.core import setup
#from Cython.Build import cythonize

setup(
    name='treap',
    py_modules=[ 
        'treap',
        'py_treap',
        'nest',
        ],
    cmdclass = {'build_ext': build_ext},
    setup_requires=[
        'Cython'
    ],
    version=version,
    description='Python implementation of treaps',
    long_description='''
A set of python modules implementing treaps is provided.

Treaps perform most operations in O(log2(n)) time, and are innately sorted.
They're very nice for keeping a collection of values that needs to
always be sorted, or for optimization problems in which you need to find
the p best values out of q, when p is much smaller than q.

A module is provided for treaps that enforce uniqueness.

A pure python version is included, as is a Cython-enhanced version for performance.

Release 1.38 is pylint'd and is known to run on at least CPython 2.x, CPython 3.x
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

