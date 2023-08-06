#!/usr/bin/env python
"""
django-memoize
--------------

**django-memoize** is an implementation
of `memoization <http://en.wikipedia.org/wiki/Memoization>`_ technique
for Django. You can think of it as a cache for function or method results.

"""

from setuptools import setup

setup(
    name='django-memoize',
    version='1.0.0',
    url='https://github.com/tvavrys/django-memoize',
    license='BSD',
    author='Tom Vavrys',
    author_email='tvavrys@sleio.com',
    description='An implementation of memoization technique for Django.',
    long_description=__doc__,
    packages=[
        'memoize',
    ],
    zip_safe=False,
    install_requires=[
        'django'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
