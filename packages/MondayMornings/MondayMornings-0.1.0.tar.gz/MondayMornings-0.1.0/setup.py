#!/bin/env python
# -*- coding: utf8 -*-

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

version = "0.1.0"

setup(
    name="MondayMornings",
    version=version,
    description=("A project that combines an alarm and weather updates for "
        "those annoying monday mornings."),
    classifiers=[],
    keywords="alarm Monday Mornings MondayMornings",
    author="Ryan Stush",
    author_email="ramstush@gmail.com",
    url="https://github.com/ramstush/MondayMornings",
    license="GPL",
    packages=find_packages(
    ),
    scripts=[
        "distribute_setup.py",
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "pygame",
        "datetime",
    ],
    #TODO: Deal with entry_points
    #entry_points="""
    #[console_scripts]
    #pythong = pythong.util:parse_args
    #"""
)
