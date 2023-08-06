try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='READemption',
    version='0.2.0',
    packages=['reademptionlib', 'tests'],
    author='Konrad U. Foerstner',
    author_email='konrad@foerstner.org',
    description='READemption - A RNA-Seq Analysis Pipeline',
    url='',
    install_requires=[
        "pysam >= 0.7.7"
    ],
    scripts=['bin/reademption'],
    license='ISCL (see LICENSE.txt)',
    long_description=open('README.rst').read(),
    classifiers=[
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ]
)
