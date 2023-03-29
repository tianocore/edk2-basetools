# Tianocore Edk2 Python BaseTools (edk2basetools)

This is a Tianocore maintained project consisting of a the python source files that make up EDK2 basetools. This package's intent is to provide an easy way to organize and share python code to facilitate reuse across environments, tools, and scripts.  Inclusion of this package and dependency management is best managed using Pip/Pypi.

## Current Release

[![PyPI](https://img.shields.io/pypi/v/edk2_basetools.svg)](https://pypi.org/project/edk2-basetools/)

A minor release occurs for each merged Pull Request, which can be tracked via [commits](https://github.com/tianocore/edk2-basetools/commits/master) or [closed pull requests](https://github.com/tianocore/edk2-basetools/pulls?q=is%3Apr+is%3Aclosed).

## Content

The package contains all python source files necessary to build an EDK2 project. This is a fundamental package and is required for edk2 builds. These tools are typically called by the build system, however each is independently callable.

Examples:

* Build.py
* Split.py
* Trim.py
* AmlToC.py

## License

All content in this repository is licensed under [BSD-2-Clause Plus Patent License](license.txt).

[![PyPI - License](https://img.shields.io/pypi/l/edk2_basetools.svg)](https://pypi.org/project/edk2-basetools/)

## Usage

NOTE: It is strongly recommended that you use python virtual environments.  Virtual environments avoid changing the global python workspace and causing conflicting dependencies.  Virtual environments are lightweight and easy to use.  [Learn more](https://docs.python.org/3/library/venv.html)

* To install run `pip install --upgrade edk2-basetools`
* To use in your python code

### Building with edk2-pytool-extensions

To perform a build using [edk2-pytool-extensions](https://pypi.org/project/edk2-pytool-extensions/) invocables, add the *pipbuild-win* or *pipbuild-unix* scope to the platform build file.

### Building with edk2

Follow the normal build process; it will automatically detect and use edk2-basetools pip module if available.

### Custom

BaseTools/Bin**Pip**Wrappers/WindowsLike or BaseTools/Bin**Pip**Wrappers/PosixLike path must be set instead of BaseTools/BinWrappers/WindowsLike or BaseTools/BinWrappers/UnixLike

## Contribution Process

This project welcomes all types of contributions.
For issues, bugs, and questions it is best to open a [github issue](https://github.com/tianocore/edk2-basetools/issues).

### Code Contributions

For code contributions this project leverages github pull requests.  See github tutorials, help, and documentation for complete descriptions.
For best success please follow the below process.

1. Contributor opens an issue describing problem or new desired functionality
2. Contributor forks repository in github
3. Contributor creates branch for work in their fork
4. Contributor makes code changes, writes relevant unit tests, authors documentation and release notes as necessary.
5. Contributor runs tests locally
6. Contributor submits PR to master branch of tianocore/edk2-basetools
    1. PR reviewers will provide feedback on change.  If any modifications are required, contributor will make changes and push updates.
    2. PR automation will run and validate tests pass
    3. If all comments resolved, maintainers approved, and tests pass the PR will be squash merged and closed by the maintainers.

## Maintainers

[Liming Gao <gaoliming@byosoft.com.cn>](mailto:gaoliming@byosoft.com.cn)
[Rebecca Cran <rebecca@bsdio.com>](mailto:rebecca@bsdio.com)

### Developers/Reviewers

See the [github team](https://github.com/orgs/tianocore/teams/edk-ii-tool-maintainers) for more details.

## Documentation

See the github repo **docs** folder
