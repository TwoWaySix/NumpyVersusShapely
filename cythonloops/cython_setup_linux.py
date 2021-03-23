from distutils.core import Extension, setup
from Cython.Build import cythonize

setup(ext_modules=cythonize('cython_loops.pyx'))  # works on linux, but not on windows
