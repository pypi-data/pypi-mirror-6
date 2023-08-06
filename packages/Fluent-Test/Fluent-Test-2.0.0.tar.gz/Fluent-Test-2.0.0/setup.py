#!/usr/bin/env python
import os.path

from setuptools import find_packages, setup

from fluenttest import __version__
from setupext import read_requirements_from_file


root_dir = os.path.dirname(__file__)

# read runtime requirements from a pip formatted requirements.txt
required_packages = read_requirements_from_file(
    os.path.join(root_dir, 'requirements.txt'))

# additional components used for testing are added in here
test_requirements = required_packages[:]
test_requirements.extend(read_requirements_from_file(
    os.path.join(root_dir, 'test-requirements.txt')))

# and the top-level README becomes our packages long description
f = open('README.rst')
readme = f.read()
f.close()


# let setuptools.setup do the real work
setup(
    name='Fluent-Test',
    version=__version__,
    license='BSD',
    author='Dave Shawley',
    author_email='daveshawley@gmail.com',
    url='http://github.com/dave-shawley/fluent-test/',
    description='Fluent testing for Python',
    long_description=readme,
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=required_packages,
    tests_require=test_requirements,
    test_suite='tests',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
