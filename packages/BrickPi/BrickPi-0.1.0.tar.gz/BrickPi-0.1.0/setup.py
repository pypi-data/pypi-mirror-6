"""
Creative Commons Attribution-ShareAlike 3.0
http://creativecommons.org/licenses/by-sa/3.0/
"""

from distutils.core import setup
from setuptools import setup

classifiers = ['Development Status :: 3 - Alpha',
               'Operating System :: POSIX :: Linux',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 2.6',
               'Programming Language :: Python :: 2.7',
               'Topic :: Software Development',
               'Topic :: Home Automation',
               'Topic :: System :: Hardware']

setup(
    name='BrickPi',
    version='0.1.0',
    author='W. H. Bell',
    author_email='whbqcd1@gmail.com',
    packages=['BrickPi'],
    url='http://pypi.python.org/pypi/BrickPi/',
    license='Creative Commons Attribution-ShareAlike 3.0',
    description='BrickPi interfaces for Python and Scratch',
    long_description=open('README.txt').read(),
    keywords='Raspberry Pi BrickPi Scratch',
    classifiers=classifiers,
    install_requires=[
        "RpiScratchIO >= 0.1.5",
    ],
)
