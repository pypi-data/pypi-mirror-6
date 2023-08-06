# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import kambo


setup(
    name="kambo",
    version=kambo.__version__,
    description="Kambo web framework",
    author="Ilya Strukov",
    author_email="iley@iley.ru",
    packages=find_packages(exclude=["*.tests"]),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3.3"
    ]
)
