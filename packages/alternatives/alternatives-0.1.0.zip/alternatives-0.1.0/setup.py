import os
from setuptools import setup, find_packages

setup(
    name='alternatives',
    version='0.1.0',
    packages=find_packages(exclude=("test.*",)),

    url='',
    license='MIT',
    author='Aleksandr Rudakov',
    author_email='ribozz@gmail.com',
    description='Alternatives api is just a syntax sugar for selecting alternative variants from some set of values',
    long_description=open('README.rst').read(),

    # cmdclass={'test': PyTest},

    extras_require={
        'dev': ['pytest==2.3.5', 'coverage', 'pytest-cov', 'mock'],
        'travis': ['coveralls'],
    }
)
