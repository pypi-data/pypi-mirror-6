#!/usr/bin/env python

from setuptools import setup

setup(
    name="drive-casa",
    version="0.4.0",
    packages=['drivecasa'],
    description="""Interfacing package for scripting CASA from within a larger pipeline.""",
    author="Tim Staley",
    author_email="timstaley337@gmail.com",
    url="https://github.com/timstaley/drivecasa",
    install_requires=['pexpect'],
)
