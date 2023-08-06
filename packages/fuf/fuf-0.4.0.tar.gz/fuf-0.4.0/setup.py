#!/bin/env python
# -*- coding: utf8 -*-

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

version = "0.4.0"

setup(
    name="fuf",
    version=version,
    description="Funced-Up Functions",
    classifiers=[],
    keywords="",
    author="Matt Soucy",
    author_email="msoucy@csh.rit.edu",
    url="http://github.com/msoucy/fuf",
    license="MIT",
    packages=find_packages(
    ),
    scripts=[
        "distribute_setup.py",
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "",
    ],
    #TODO: Deal with entry_points
    #entry_points="""
    #[console_scripts]
    #pythong = pythong.util:parse_args
    #"""
)
