#!/usr/bin/env python

# Python
import os

# Setuptools
from setuptools import setup

setup(
    name='lmiapi',
    version='0.1',
    author='Nine More Minutes, Inc.',
    author_email='support@ninemoreminutes.com',
    description='Basic Python interface to the LogMeIn Central REST API.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README'),
                          'rb').read().decode('utf-8'),
    license='BSD',
    keywords='logmein api requests rest',
    url='https://projects.ninemoreminutes.com/projects/lmiapi/',
    packages=['lmiapi'],
    include_package_data=False,
    zip_safe=False,
    install_requires=[
        'requests>=2.0',
    ],
    setup_requires=[],
    #tests_require=tests_require,
    #test_suite='test_suite.TestSuite',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Systems Administration',
    ],
    options={
        'egg_info': {
            'tag_build': '.dev',
        },
        'aliases': {
            'dev_build': 'egg_info sdist',
            'release_build': 'egg_info -b "" -R sdist',
        },
    },
)
