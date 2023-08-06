#!/usr/bin/env python
"""
persona_idp
==================

TODO: description

:copyright: (c) 2014 Department of Parks & Wildlife, see AUTHORS
            for more details.
:license: BSD 3-Clause, see LICENSE for more details.
"""
from setuptools import setup, find_packages

# Hack to prevent stupid "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when running `python
# setup.py test` (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
for m in ('multiprocessing', 'billiard'):
    try:
        __import__(m)
    except ImportError:
        pass

tests_require = [
    'requests',     # for the examples.json_ws
]

install_requires = [
    'PyCrypto',
]

version = __import__('persona_idp').get_version()

setup(
    name='persona_idp',
    version=version,
    author='Tomas Krajca',
    author_email=('tomas.krajca@DPaW.wa.gov.au'),
    url='https://github.com/dpaw2/persona-idp',
    description=('This is a generic and reusable python implementation of '
                 'Mozilla Persona Identity Provider '
                 '<https://developer.mozilla.org/en-US/Persona/Identity_'
                 'Provider_Overview>.'),
    packages=find_packages(exclude=['docs']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='tests',
    test_loader='unittest:TestLoader',
    scripts=[],
    license='BSD License',
    include_package_data=True,
    keywords=("persona identity provider IDP mozilla dpaw single-sign-on "
              "authentication"),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: Mozilla',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
)
