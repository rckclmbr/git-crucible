#!/usr/bin/env python

import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from distutils.command.install_data import install_data

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
    'packages': ["crucible"],
    'scripts': ["bin/git-crucible"],
    'cmdclass': cmdclasses,
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
