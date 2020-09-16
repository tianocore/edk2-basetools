# @file setup.py
# This contains setup info for edk2-pytool-library pip module
#
##
# Copyright (c) Microsoft Corporation
#
# SPDX-License-Identifier: BSD-2-Clause-Patent
##

import setuptools
from setuptools.command.sdist import sdist
from setuptools.command.install import install
from setuptools.command.develop import develop


with open("readme.md", "r") as fh:
    long_description = fh.read()


class PostSdistCommand(sdist):
    """Post-sdist."""

    def run(self):
        sdist.run(self)


class PostInstallCommand(install):
    """Post-install."""

    def run(self):
        install.run(self)


class PostDevCommand(develop):
    """Post-develop."""

    def run(self):
        develop.run(self)


setuptools.setup(
    name="edk2-basetools",
    version=version,
    author="Tianocore Edk2-BaseTool team",
    author_email="edk2-bugs@lists.01.org",
    description="Python BaseTools supporting UEFI EDK2 firmware development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tianocore/edk2-basetools",
    license='BSD-2-Clause-Patent',
    packages=setuptools.find_packages(),
    cmdclass={
        'sdist': PostSdistCommand,
        'install': PostInstallCommand,
        'develop': PostDevCommand,
    },
    include_package_data=True,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=[
        'antlr4-python3-runtime'
    ],
    entry_points={
        'console_scripts': [
            'edk2_build=edk2basetools.build.build:Main',
            'edk2_ecc=edk2basetools.Ecc.EccMain:Main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers"
    ]
)
