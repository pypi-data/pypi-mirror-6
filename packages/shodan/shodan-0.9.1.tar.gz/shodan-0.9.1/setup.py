#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'shodan',
    version = '0.9.1',
    description = 'Python library for Shodan (http://www.shodanhq.com)',
    author = 'John Matherly',
    author_email = 'jmath@shodan.io',
    url = 'http://github.com/achillean/shodan-python/tree/master',
    packages = ['shodan'],
    install_requires=["simplejson"],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
