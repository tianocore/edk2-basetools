*** Settings ***
Documentation     A test suite to test Platform CI on edk2 repo
#
# Copyright (c), Microsoft Corporation
# SPDX-License-Identifier: BSD-2-Clause-Patent

Library  Process
Library  OperatingSystem
Library  String

Resource  Shared_Keywords.robot

Suite Setup  One time setup  ${repo_url}  ${ws_dir}

# Suite Setup

*** Variables ***
${repo_url}           https://github.com/tianocore/edk2.git
${default_branch}     not_yet_set
${ws_dir}             edk2
${ws_root}            ${TEST_OUTPUT}${/}${ws_dir}
${tool_chain}         VS2019


*** Keywords ***
One time setup
    [Arguments]  ${url}  ${folder}
    ## Dump pip versions
    ${result}=   Run Process    python  -m  pip   list  shell=True
    Log  ${result.stdout}

    ## Make output directory if doesn't already exist
    Create Directory  ${TEST_OUTPUT}

    ## Clone repo
    Run Keyword  Clone the git repo  ${url}  ${folder}

    ## Figure out default branch
    ${branch}=  Get default branch from remote  ${ws_root}
    Set Suite Variable  ${default_branch}  ${branch}


*** Test Cases ***
Run Edk2 Ovmf IA32 DEBUG
    [Documentation]  This test will run IA32 DEBUG build for OvmfPkg
    [Tags]           PlatformCI  OvmfPkg  IA32  VS2019  Windows  Qemu  Edk2
    ${arch}=              Set Variable  IA32
    ${target}=            Set Variable  DEBUG
    ${package}=           Set Variable  OvmfPkg
    ${ci_file}=           Set Variable  ${package}${/}PlatformCI${/}PlatformBuild.py

    # make sure on default branch
    Reset git repo to default branch  ${ws_root}  ${default_branch}

    Stuart setup           ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Stuart update          ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Build BaseTools        ${tool_chain}  ${ws_root}
    Stuart platform build  ${ci_file}  ${arch}  ${target}  ${tool_chain}  ${ws_root}
    Stuart platform run    ${ci_file}  ${arch}  ${target}  ${tool_chain}  MAKE_STARTUP_NSH\=TRUE  ${ws_root}

Run Edk2 Ovmf IA32 RELEASE
    [Documentation]  This test will run IA32 RELEASE build for OvmfPkg
    [Tags]           PlatformCI  OvmfPkg  IA32  VS2019  Windows  Qemu  Edk2
    ${arch}=              Set Variable  IA32
    ${target}=            Set Variable  RELEASE
    ${package}=           Set Variable  OvmfPkg
    ${ci_file}=           Set Variable  ${package}${/}PlatformCI${/}PlatformBuild.py

    # make sure on default branch
    Reset git repo to default branch  ${ws_root}  ${default_branch}

    Stuart setup           ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Stuart update          ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Build BaseTools        ${tool_chain}  ${ws_root}
    Stuart platform build  ${ci_file}  ${arch}  ${target}  ${tool_chain}  ${ws_root}
    Stuart platform run    ${ci_file}  ${arch}  ${target}  ${tool_chain}  MAKE_STARTUP_NSH\=TRUE  ${ws_root}

Run Edk2 Ovmf X64 DEBUG
    [Documentation]  This test will run X64 DEBUG build for OvmfPkg
    [Tags]           PlatformCI  OvmfPkg  X64  VS2019  Windows  Qemu  Edk2
    ${arch}=              Set Variable  X64
    ${target}=            Set Variable  DEBUG
    ${package}=           Set Variable  OvmfPkg
    ${ci_file}=           Set Variable  ${package}${/}PlatformCI${/}PlatformBuild.py

    # make sure on default branch
    Reset git repo to default branch  ${ws_root}  ${default_branch}

    Stuart setup           ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Stuart update          ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Build BaseTools        ${tool_chain}  ${ws_root}
    Stuart platform build  ${ci_file}  ${arch}  ${target}  ${tool_chain}  ${ws_root}
    Stuart platform run    ${ci_file}  ${arch}  ${target}  ${tool_chain}  MAKE_STARTUP_NSH\=TRUE  ${ws_root}

Run Edk2 Ovmf X64 RELEASE
    [Documentation]  This test will run X64 RELEASE build for OvmfPkg
    [Tags]           PlatformCI  OvmfPkg  X64  VS2019  Windows  Qemu  Edk2
    ${arch}=              Set Variable  X64
    ${target}=            Set Variable  RELEASE
    ${package}=           Set Variable  OvmfPkg
    ${ci_file}=           Set Variable  ${package}${/}PlatformCI${/}PlatformBuild.py

    # make sure on default branch
    Reset git repo to default branch  ${ws_root}  ${default_branch}

    Stuart setup           ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Stuart update          ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Build BaseTools        ${tool_chain}  ${ws_root}
    Stuart platform build  ${ci_file}  ${arch}  ${target}  ${tool_chain}  ${ws_root}
    Stuart platform run    ${ci_file}  ${arch}  ${target}  ${tool_chain}  MAKE_STARTUP_NSH\=TRUE  ${ws_root}

Run Edk2 Emulator IA32 DEBUG
    [Documentation]  This test will run IA32 DEBUG build for EmulatorPkg
    [Tags]           PlatformCI  EmulatorPkg  IA32  VS2019  Windows  Qemu  Edk2
    ${arch}=              Set Variable  IA32
    ${target}=            Set Variable  DEBUG
    ${package}=           Set Variable  EmulatorPkg
    ${ci_file}=           Set Variable  ${package}${/}PlatformCI${/}PlatformBuild.py

    # make sure on default branch
    Reset git repo to default branch  ${ws_root}  ${default_branch}

    Stuart setup           ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Stuart update          ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Build BaseTools        ${tool_chain}  ${ws_root}
    Stuart platform build  ${ci_file}  ${arch}  ${target}  ${tool_chain}  ${ws_root}
    Stuart platform run    ${ci_file}  ${arch}  ${target}  ${tool_chain}  MAKE_STARTUP_NSH\=TRUE  ${ws_root}

Run Edk2 Emulator IA32 RELEASE
    [Documentation]  This test will run IA32 RELEASE build for EmulatorPkg
    [Tags]           PlatformCI EmulatorPkg  IA32  VS2019  Windows  Qemu  Edk2
    ${arch}=              Set Variable  IA32
    ${target}=            Set Variable  RELEASE
    ${package}=           Set Variable  EmulatorPkg
    ${ci_file}=           Set Variable  ${package}${/}PlatformCI${/}PlatformBuild.py

    # make sure on default branch
    Reset git repo to default branch  ${ws_root}  ${default_branch}

    Stuart setup           ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Stuart update          ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Build BaseTools        ${tool_chain}  ${ws_root}
    Stuart platform build  ${ci_file}  ${arch}  ${target}  ${tool_chain}  ${ws_root}
    Stuart platform run    ${ci_file}  ${arch}  ${target}  ${tool_chain}  MAKE_STARTUP_NSH\=TRUE  ${ws_root}

Run Edk2 Emulator X64 DEBUG
    [Documentation]  This test will run X64 DEBUG build for EmulatorPkg
    [Tags]           PlatformCI EmulatorPkg  X64  VS2019  Windows  Qemu  Edk2
    ${arch}=              Set Variable  X64
    ${target}=            Set Variable  DEBUG
    ${package}=           Set Variable  EmulatorPkg
    ${ci_file}=           Set Variable  ${package}${/}PlatformCI${/}PlatformBuild.py

    # make sure on default branch
    Reset git repo to default branch  ${ws_root}  ${default_branch}

    Stuart setup           ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Stuart update          ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Build BaseTools        ${tool_chain}  ${ws_root}
    Stuart platform build  ${ci_file}  ${arch}  ${target}  ${tool_chain}  ${ws_root}
    Stuart platform run    ${ci_file}  ${arch}  ${target}  ${tool_chain}  MAKE_STARTUP_NSH\=TRUE  ${ws_root}

Run Edk2 Emulator X64 RELEASE
    [Documentation]  This test will run X64 RELEASE build for EmulatorPkg
    [Tags]           PlatformCI EmulatorPkg  X64  VS2019  Windows  Qemu  Edk2
    ${arch}=              Set Variable  X64
    ${target}=            Set Variable  RELEASE
    ${package}=           Set Variable  EmulatorPkg
    ${ci_file}=           Set Variable  ${package}${/}PlatformCI${/}PlatformBuild.py

    # make sure on default branch
    Reset git repo to default branch  ${ws_root}  ${default_branch}

    Stuart setup           ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Stuart update          ${ci_file}  ${arch}  ${target}  ${package}  ${tool_chain}  ${ws_root}
    Build BaseTools        ${tool_chain}  ${ws_root}
    Stuart platform build  ${ci_file}  ${arch}  ${target}  ${tool_chain}  ${ws_root}
    Stuart platform run    ${ci_file}  ${arch}  ${target}  ${tool_chain}  MAKE_STARTUP_NSH\=TRUE  ${ws_root}
