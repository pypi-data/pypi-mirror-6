#!/usr/bin/env python
import os
from setuptools import setup

def read(filen):
    with open(os.path.join(os.path.dirname(__file__), filen), "r") as fp:
        return fp.read()

setup (
    name = "HieraPy",
    version = "0.0.1",
    description="Shy implementation of Puppet's Hiera configuration tool.",
    long_description=read("README.md"),
    author="Ivan N. (based on previous work by Alec Elton)",
    author_email="",
    url="https://github.com/ivannpaz/HieraPy",
    packages=["hierapy"],
    install_requires=[]
)
