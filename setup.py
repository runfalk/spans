#!/usr/bin/env python
import re
import sys
import os

from setuptools import setup

def cheeseshopify(rst):
    """Since PyPI doesn't support the RST `code-block` directive or the
    :code: role, replace all `code-block` directives with `::` and
    `:code:` with "".
    """

    ret = rst.replace(".. code-block:: python", "::").replace(":code:", "")
    return ret

with open("README.rst") as fp:
    long_desc = cheeseshopify(fp.read())

with open("LICENSE") as fp:
    license = fp.read()

with open("spans/__init__.py") as fp:
    version = re.search('__version__\s+=\s+"([^"]+)', fp.read()).group(1)

requirements = []
if os.path.exists("requirements.txt"):
    with open("requirements.txt") as fp:
        requirements = fp.read().split("\n")

setup(
    name="Spans",
    version=version,
    description="Continuous set support for Python",
    long_description=long_desc,
    license=license,
    author="Andreas Runfalk",
    author_email="andreas@runfalk.se",
    url="https://www.github.com/runfalk/spans", # TODO: Fix
    packages=["spans"],
    install_requires=requirements,
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Topic :: Utilities"
    ),
    zip_safe=False,
    test_suite="spans.tests.suite"
)
