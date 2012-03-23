from distutils.core import setup

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
    'install_requires': ['restkit'],
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
