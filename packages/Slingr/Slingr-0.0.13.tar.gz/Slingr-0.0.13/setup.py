#!/usr/bin/env python

"""Setup Slingr"""

import re

# Do not 'import slingr' to get version
version = re.search("__version__ = '([^']+)'",
                    open('slingr/__init__.py').read()).group(1)

from setuptools import setup, find_packages

setup(
    name='Slingr',
    version=version,
    author='George V. Reilly',
    author_email='george@reilly.org',
    packages=find_packages(),
    description='Web development framework that builds and serves Cobs '
    '(deployable web applications), running on top of Flask',
    long_description=open('README.txt').read(),
    url='https://github.com/cozi/slingr',
    install_requires=[
        'Flask',
        'Flask-Script',
        'Flask-Assets',
        'PyYAML',
        'pystache',
        'ua-parser',
        'mock',
        'Pycco',
        'Eggsac',
        'argparse',
    ],
    entry_points={
        'console_scripts': [
            'sling = slingr.manage:sling',
        ],
    },
    zip_safe=False,
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    platforms='any',
)
