# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme:
    long_desc = readme.read()


setup(
    # Package info
    name='python_osinfo',
    version='0.2.0',
    description="Python OS information retriever.",
    author='Rodrigo Núñez Mujica',
    author_email='rnunezmujica@icloud.com',
    url='https://github.com/Dalveen84/python-osinfo/',
    long_description=long_desc,

    # Package classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: System :: Operating System',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    # Package structure
    packages=find_packages('src', exclude=['ez_setup',
                           '*.tests', '*.tests.*', 'tests.*', 'tests']),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,

    # Dependencies
    install_requires=[
    ],

    # Tests
    test_suite='osinfo.tests.suite',
    tests_require='docutils >= 0.6',
)
