#!/usr/bin/env python

__author__ = 'Jason Corbett'

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

requirements = []
with open('requirements.txt', 'r') as reqfile:
    requirements.extend(reqfile.read().split())

setup(
    name="slickqa-narc",
    description="A program responsible for responding to Slick events",
    version="1.0" + open("build.txt").read(),
    license="License :: OSI Approved :: Apache Software License",
    long_description=open('README.txt').read(),
    packages=find_packages(exclude=['ez_setup']),
    package_data={'': ['*.txt', '*.rst', '*.html']},
    include_package_data=True,
    install_requires=requirements,
    author="Slick Developers",
    url="http://code.google.com/p/slickqa",
    entry_points={
        'console_scripts': ['narc = narc.main:main', 'narcctl = narc.main:ctlmain'],
        'narc.response' : ['emailresponder = narc.plugins.email:EmailResponder',
                           'shutdownrestart = narc.plugins.internal:ShutdownRestartPlugin',
                           'autotestrungroup = narc.plugins.testrungroup:AutomaticTestrunGroupPlugin']
    }
)
