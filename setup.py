# @file setup.py
# This contains setup info for edk2-pytool-library pip module
#
##
# Copyright (c) Microsoft Corporation
#
# SPDX-License-Identifier: BSD-2-Clause-Patent
##

import setuptools
import subprocess
import sys
from setuptools.command.sdist import sdist
from setuptools.command.install import install
from setuptools.command.develop import develop


# figure out what the current version is
version_parts = ["0", "1"]
# query pypi to see what the 
pip_cmds = [sys.executable, '-m', 'pip', 'search', 'edk2-basetools']
pypi_results = str(subprocess.check_output(pip_cmds).decode('UTF-8')).strip().splitlines()
short_version = "0"
for pypi_package in pypi_results:
    if not pypi_package.strip().lower().startswith("edk2-basetools "):
        continue
    package_parts = pypi_package.split()
    package_version = package_parts[1].strip("() ")
    package_ver_parts = package_version.split(".")
    if len(package_ver_parts) < 2:
        print(f"The previous version didn't have a second element {package_version}")
        raise RuntimeError()
    elif int(package_ver_parts[0]) != int(version_parts[0]) or int(package_ver_parts[1]) != int(version_parts[1]):
        print("Upgrading the version")
        short_version = 0
    elif len(package_ver_parts) != 3:
        print(f"The previous version didn't have a third element {package_version}")
    else:
        short_version = int(package_ver_parts[2]) + 1
if short_version is None:
    raise ValueError("Unable to query pypi for the latest version of edk2-basetools")
version_parts.append(str(short_version))
version = ".".join(version_parts)
print(f"Version selected: {version}")


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


with open("readme.md", "r") as fh:
    long_description = fh.read()

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
    use_scm_version=False,
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
