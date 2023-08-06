"""Utilities for writing tests with Python"""
from setuptools import setup

setup(
    name="testil",
    version="1.0",
    author="Daniel Miller",
    author_email="millerdev@gmail.com",
    description=__doc__,
    url="https://github.com/millerdev/testil.git",
    license="MIT",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
    py_modules=["testil"],
)
