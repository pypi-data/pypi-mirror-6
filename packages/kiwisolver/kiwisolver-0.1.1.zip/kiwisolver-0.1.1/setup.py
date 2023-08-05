#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from setuptools import setup, Extension


ext_modules = [
    Extension(
        'kiwisolver',
        ['constraint.cpp',
         'expression.cpp',
         'kiwisolver.cpp',
         'solver.cpp',
         'strength.cpp',
         'term.cpp',
         'variable.cpp'],
        include_dirs=['.'],
        language='c++',
    ),
]


setup(
    name='kiwisolver',
    version='0.1.1',
    author='The Nucleic Development Team',
    author_email='sccolbert@gmail.com',
    url='https://github.com/nucleic/kiwi',
    description='A fast implementation of the Cassowary constraint solver',
    long_description=open('README.rst').read(),
    install_requires=['distribute'],
    ext_modules=ext_modules,
)
