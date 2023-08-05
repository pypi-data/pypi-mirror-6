#!/usr/bin/env python

"""Setup Eggsac"""

import re

# Do not 'import eggsac' to get version
version = re.search("__version__ = '([^']+)'",
                    open('eggsac/__init__.py').read()).group(1)

from setuptools import setup, find_packages

setup(
    name='Eggsac',
    version=version,
    author='George V. Reilly',
    author_email='george@reilly.org',
    packages=find_packages(),
    description='Package Python applications in a virtualenv for deployment',
    long_description=open('README.rst').read(),
    url='https://github.com/cozi/eggsac',
    install_requires=[
        'argparse',
        'virtualenv >= 1.10',
    ],
    zip_safe=False,
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Software Distribution',
    ],
    platforms='any',
    entry_points={
        'console_scripts': [
            'eggsac = eggsac.eggsac:eggsac',
            ]
    },
)
