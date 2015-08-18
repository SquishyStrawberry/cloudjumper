#!/usr/bin/env python3
import setuptools

setuptools.setup(
    name="cloudjumper",
    version="1.0.0", # TODO Add __version__
    description="A modular IRC Bot",
    author="SquishyStrawberry",
    install_requires=[
        "beautifulsoup4",
        "requests"
    ],
    packages=setuptools.find_packages()
)
