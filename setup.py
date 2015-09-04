#!/usr/bin/env python3
import setuptools
from cloudjumper import __version__

setuptools.setup(
    name="cloudjumper",
    version=__version__,
    description="A modular IRC Bot",
    author="SquishyStrawberry",
    install_requires=[
        "beautifulsoup4",
        "requests"
    ],
    packages=setuptools.find_packages()
)
