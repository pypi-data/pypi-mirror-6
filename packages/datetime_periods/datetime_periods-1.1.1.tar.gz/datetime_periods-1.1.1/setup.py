# -*- encoding: utf-8 -*-
from setuptools import setup

setup(
    name='datetime_periods',
    version='1.1.1',
    url='https://github.com/gaqzi/datetime_periods',
    author='Björn Andersson',
    author_email='ba@sanitarium.se',
    description='Easily create time periods from timestamps',
    license='BSD',
    long_description=open('README.rst').read(),
    packages=['datetime_periods'],
    package_data={
        '': ['README.rst']
    },
    include_package_data=True,
    install_requires=[
        'python-dateutil>=2.1',
        'datetime_truncate>=1.0.0',
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose>=1.2.1',
        'pytz'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
)
