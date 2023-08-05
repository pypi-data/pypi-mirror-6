from __future__ import (print_function, absolute_import,
                        unicode_literals, division)


import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import patois


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with open('README.rst', 'r') as readme:
    patois_long_description = readme.read()

with open('LICENSE', 'r') as license:
    patois_license = license.read()

patois_classifiers = (
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: BSD',
    'Operating System :: POSIX :: Linux',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
    'Topic :: Utilities',
)

setup(
    name='patois',
    version=patois.__version__,
    description='Python VM compatibility library',
    long_description=patois_long_description,
    author='Hank Gay',
    author_email='hank@realultimateprogramming.com',
    url="http://pypi.python.org/pypi/patois/",
    py_modules=['patois',],
    license=patois_license,
    zip_safe=False,
    classifiers=patois_classifiers,
)
