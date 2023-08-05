#!/usr/bin/env python

#-----------------------------------------------------------------------------
# Copyright (c) 2013, Allen B. Riddell
#
# This file is licensed under Version 3.0 of the GNU General Public
# License. See LICENSE for a text of the license.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# This file is part of PyStan.
#
# PyStan is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# PyStan is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyStan.  If not, see <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
import os
import sys

LONG_DESCRIPTION = open('README.rst').read()
NAME         = 'pystan'
DESCRIPTION  = 'Python interface to Stan, a package for Bayesian inference'
AUTHOR       = 'Allen B. Riddell'
AUTHOR_EMAIL = 'abr@ariddell.org'
URL          = 'https://github.com/stan-dev/pystan'
LICENSE      = 'GPLv3'
CLASSIFIERS = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Programming Language :: Cython',
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Operating System :: OS Independent',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Information Analysis'
]
MAJOR = 2
MINOR = 0
MICRO = 1
NANO = 2
ISRELEASED = True
VERSION = '%d.%d.%d.%d' % (MAJOR, MINOR, MICRO, NANO)

FULLVERSION = VERSION
if not ISRELEASED:
    FULLVERSION += '.dev'

# try bootstrapping setuptools if it doesn't exist
try:
    import pkg_resources
    try:
        pkg_resources.require("setuptools>=0.6.37")
    except pkg_resources.VersionConflict:
        from ez_setup import use_setuptools
        use_setuptools(version="0.6.37")
    from setuptools import setup
    _have_setuptools = True
except ImportError:
    # no setuptools installed and bootstrap failed
    from distutils.core import setup
    _have_setuptools = False

min_numpy_ver = '1.7.1' if sys.version_info[0] >= 3 else '1.6'
setuptools_kwargs = {'install_requires': ['Cython >= 0.19',
                                          'numpy >= %s' % min_numpy_ver],
                     'zip_safe': False}

if not _have_setuptools:
    ## exit if attempting to install without Cython or numpy
    try:
        import Cython
        import numpy
    except ImportError:
        raise SystemExit("Cython>=0.19 and NumPy are required.")
    setuptools_kwargs = {}

import distutils.core
from distutils.errors import CCompilerError, DistutilsError
from distutils.extension import Extension


## static libraries
stan_include_dirs = ["pystan/stan/src",
                     "pystan/stan/lib/eigen_3.2.0",
                     "pystan/stan/lib/boost_1.54.0"]

stan_macros = [('BOOST_RESULT_OF_USE_TR1', None),
               ('BOOST_NO_DECLTYPE', None),
               ('BOOST_DISABLE_ASSERTS', None)]

libstan_sources = [
    "pystan/stan/src/stan/agrad/rev/var_stack.cpp",
    "pystan/stan/src/stan/math/matrix.cpp",
    "pystan/stan/src/stan/agrad/matrix.cpp"
]

libstan_extra_compile_args = ['-O3', '-ftemplate-depth-256']

libstan = ('stan', {'sources': libstan_sources,
                    'include_dirs': stan_include_dirs,
                    'extra_compile_args': libstan_extra_compile_args,
                    'macros': stan_macros})

## extensions
extensions_extra_compile_args = ['-O0', '-ftemplate-depth-256']

stanc_sources = [
    "pystan/stan/src/stan/gm/grammars/var_decls_grammar_inst.cpp",
    "pystan/stan/src/stan/gm/grammars/expression_grammar_inst.cpp",
    "pystan/stan/src/stan/gm/grammars/statement_2_grammar_inst.cpp",
    "pystan/stan/src/stan/gm/grammars/statement_grammar_inst.cpp",
    "pystan/stan/src/stan/gm/grammars/term_grammar_inst.cpp",
    "pystan/stan/src/stan/gm/grammars/program_grammar_inst.cpp",
    "pystan/stan/src/stan/gm/grammars/whitespace_grammar_inst.cpp",
    "pystan/stan/src/stan/gm/ast_def.cpp"
]

extensions = [Extension("pystan._api",
                        ["pystan/_api.pyx"] + stanc_sources,
                        language='c++',
                        define_macros=stan_macros,
                        include_dirs=stan_include_dirs,
                        extra_compile_args=extensions_extra_compile_args),
              Extension("pystan._chains",
                        ["pystan/_chains.pyx"],
                        language='c++',
                        define_macros=stan_macros,
                        include_dirs=stan_include_dirs,
                        extra_compile_args=extensions_extra_compile_args)]


## package data
package_data_pats = ['*.hpp', '*.pxd', '*.pyx', 'tests/data/*.csv']

# get every file under pystan/stan/src and pystan/stan/lib
stan_files_all = sum(
    [[os.path.join(path.replace('pystan/', ''), fn) for fn in files]
     for path, dirs, files in os.walk('pystan/stan/src/')], [])

lib_files_all = sum(
    [[os.path.join(path.replace('pystan/', ''), fn) for fn in files]
     for path, dirs, files in os.walk('pystan/stan/lib/')], [])

package_data_pats += stan_files_all
package_data_pats += lib_files_all

if _have_setuptools:
    setuptools_kwargs["test_suite"] = "nose.collector"

## setup
if __name__ == '__main__':
    distutils.core._setup_stop_after = 'commandline'
    metadata = dict(
        name=NAME,
        version=FULLVERSION,
        maintainer=AUTHOR,
        maintainer_email=AUTHOR_EMAIL,
        packages=['pystan',
                  'pystan.tests',
                  'pystan.external',
                  'pystan.external.pymc',
                  'pystan.external.enum',
                  'pystan.external.scipy'],
        ext_modules=extensions,
        libraries=[libstan],
        package_data={'pystan': package_data_pats},
        description=DESCRIPTION,
        license=LICENSE,
        url=URL,
        long_description=LONG_DESCRIPTION,
        classifiers=CLASSIFIERS,
        **setuptools_kwargs
    )
    if len(sys.argv) >= 2 and ('--help' in sys.argv[1:] or sys.argv[1]
                               in ('--help-commands', 'egg_info', '--version', 'clean')):
        # For these actions, neither Numpy nor Cython is required.
        #
        # They are required to succeed when pip is used to install PyStan
        # when, for example, Numpy is not yet present.
        dist = setup(**metadata)
    else:
        from Cython.Build import cythonize
        from numpy.distutils.command import install, install_clib
        from numpy.distutils.misc_util import InstallableLib

        metadata['ext_modules'] = cythonize(extensions)

        # use numpy.distutils machinery to install libstan.a
        metadata['cmdclass'] = {'install': install.install,
                                'install_clib': install_clib.install_clib}
        dist = setup(**metadata)
        dist.installed_libraries = [InstallableLib(libstan[0],
                                                   libstan[1],
                                                   'pystan/bin/')]
    try:
        dist.run_commands()
    except KeyboardInterrupt:
        raise SystemExit("Interrupted")
    except (IOError, os.error) as exc:
        from distutils.util import grok_environment_error
        error = grok_environment_error(exc)
    except (DistutilsError, CCompilerError) as msg:
            raise SystemExit("error: " + str(msg))
