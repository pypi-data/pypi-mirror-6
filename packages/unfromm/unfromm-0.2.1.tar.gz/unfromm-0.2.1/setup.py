#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='unfromm',
    description='Simple profanity filter.',
    author='Christopher Grebs',
    author_email='cg@webshox.org',
    url='https://github.com/EnTeQuAk/unfromm/',
    license='BSD',
    version='0.2.1',
    packages=find_packages(exclude=['tests*']),
    tests_require=['nose'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Topic :: Text Processing :: Filters',
    ],
    zip_safe=False,
    include_package_data=True,
    test_suite='nose.collector',
)
