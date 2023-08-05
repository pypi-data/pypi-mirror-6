from setuptools import setup, find_packages
import os

version = '0.1.2'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

tests_require = [
    'nose',
    'coverage',
    'mock',
    'ipdb',
]

setup(name='requests_extensions.adapters',
    version=version,
    description="Adds dynamic loading and selection of adapters to requests",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
    ],
    keywords='',
    author='Robert Pyke',
    author_email='developer.robert.j.pyke@gmail.com',
    url='https://github.com/robertpyke/requests_extensions.adapters',
    license='MIT',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['requests_extensions', 'requests_extensions.adapters'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'requests',
    ],
    extras_require={
        'test': tests_require,
        'release': ['zest.releaser'],
    },
    entry_points="""
    # -*- Entry points: -*-
    [console_scripts]
    release = zest.releaser.release:main
    prerelease = zest.releaser.prerelease:main
    postrelease = zest.releaser.postrelease:main
    fullrelease = zest.releaser.fullrelease:main
    """,
    test_suite = 'nose.collector',
)

