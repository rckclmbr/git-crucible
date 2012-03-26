#!/usr/bin/env python2.6

import sys
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from distutils.command.install_data import install_data
try:
    from pypi2rpm.command.bdist_rpm2 import bdist_rpm2
except:
    from distutils.command.bdist_rpm import bdist_rpm as bdist_rpm2

class osx_install_data(install_data):
    # On MacOS, the platform-specific lib dir is /System/Library/Framework/Python/.../
    # which is wrong. Python 2.5 supplied with MacOS 10.5 has an Apple-specific fix
    # for this in distutils.command.install_data#306. It fixes install_lib but not
    # install_data, which is why we roll our own install_data class.

    def finalize_options(self):
        # By the time finalize_options is called, install.install_lib is set to the
        # fixed directory, so we set the installdir to install_lib. The
        # install_data class uses ('install_data', 'install_dir') instead.
        self.set_undefined_options('install', ('install_lib', 'install_dir'))
        install_data.finalize_options(self)

if sys.platform == "darwin":
    cmdclasses = {'install_data': osx_install_data}
else:
    cmdclasses = {'install_data': install_data}
cmdclasses["bdist_rpm2"] = bdist_rpm2

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

def is_not_module(filename):
    return os.path.splitext(f)[1] not in ['.py', '.pyc', '.pyo']

packages = []
data_files = []
for git_dir in ['crucible']:
    for dirpath, dirnames, filenames in os.walk(git_dir):
        # Ignore dirnames that start with '.'
        for i, dirname in enumerate(dirnames):
            if dirname.startswith('.') and not dirname.startswith(".git"): del dirnames[i]
        if '__init__.py' in filenames:
            packages.append('.'.join(fullsplit(dirpath)))
            data = [f for f in filenames if is_not_module(f)]
            if data:
                data_files.append([dirpath, [os.path.join(dirpath, f) for f in data]])
        elif filenames:
            data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

args = {
    'name': 'git-crucible',
    'version': __import__("crucible").__version__,
    'url' : "http://github.com/rckclmbr/git-crucible",
    'description': "Git extension that creates reviews in Crucible straight from the command line.",
    'long_description': """Git extension that creates reviews in Crucible straight from the command line.""",
    'author': 'Josh Braegger',
    'author_email': 'rckclmbr@gmail.com',
    'maintainer': 'Josh Braegger',
    'maintainer_email': 'rckclmbr@gmail.com',
    'license': 'BSD',
    'packages': packages,
    'data_files': data_files,
    'scripts': ["bin/git-crucible"],
    'cmdclass': cmdclasses,
    'tests_require': ["nose", "mock"],
    'test_suite': "nose.collector",
    'install_requires': "argparse",
    'classifiers': [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
}

setup(**args)
