# Tianocore Edk2 Python BaseTools (edk2basetools)

This is a Tianocore maintained project consisting of a the python source files that make up EDK2 basetools. This package's intent is to provide an easy way to organize and share python code to facilitate reuse across environments, tools, and scripts.  Inclusion of this package and dependency management is best managed using Pip/Pypi.

This is a fundamental package and is required to be used for edk2 builds.

## Current Release
[![PyPI](https://img.shields.io/pypi/v/edk2_basetools.svg)](https://pypi.org/project/edk2-basetools/)

All release information is now tracked with Github
 [tags](https://github.com/tianocore/edk2-basetools/tags),
  [releases](https://github.com/tianocore/edk2-basetools/releases) and
  [milestones](https://github.com/tianocore/edk2-basetools/milestones).


## How to use it

You have three options, install it from pypi, install it from GitHub directly, or install it locally.

### Install from PyPi

1. Run `pip install edk2-basetools`
2. In all likely hood, the project you're using has a pip requirements file. Just run `pip install -r {requirements file}`.

### Install from Git

1. Run `pip install git+https://github.com/tianocore/edk2-basetools.git`

Alternatively, you can check out a specific commit like so

1. Run `pip install git+https://github.com/tianocore/edk2-basetools.git@45dfb3641aa4d9828a7c5448d11aa67c7cbd7966` of course replacing the hash with the one you want

### Install it locally

1. Clone the repo locally
2. Run `pip install -e .` (you might need do this from an admin prompt in windows)
4. Run edk2_build to make sure it works
3. Switch to an EDK2 that has the necessary hooks

The advantage of this approach is that any changes you make to your cloned repo will be reflected.

## Content

The package contains classes and modules that can be used as the building blocks of tools that are relevant to UEFI firmware developers.
Previous this lived under `BaseTools/Source/Python` in the [EDK2 project on Github](https://github.com/tianocore/edk2).

## License

All content in this repository is licensed under [BSD-2-Clause Plus Patent License](license.txt).

[![PyPI - License](https://img.shields.io/pypi/l/edk2_basetools.svg)](https://pypi.org/project/edk2-basetools/)

## Usage

NOTE: It is strongly recommended that you use python virtual environments.  Virtual environments avoid changing the global python workspace and causing conflicting dependencies.  Virtual environments are lightweight and easy to use.  [Learn more](https://docs.python.org/3/library/venv.html)

* To install run `pip install --upgrade edk2-basetools`
* To use in your python code

    ```python
    from edk2basetools.<module> import <class>
    ```

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

See the [github team](https://github.com/orgs/tianocore/teams/edk-ii-tool-maintainers) for more details.

## Documentation

See the github repo __docs__ folder
