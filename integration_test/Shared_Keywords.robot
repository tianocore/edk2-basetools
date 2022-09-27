*** Settings ***
Documentation     A shared set of common keywords for stuart operations and git operations
#
# Copyright (c), Microsoft Corporation
# SPDX-License-Identifier: BSD-2-Clause-Patent

Library  Process
Library  OperatingSystem

# Suite Setup

*** Variables ***

#Test output location
${TEST_OUTPUT}          ${TEST_OUTPUT_BASE}

*** Keywords ***

### Git operations ###
Clone the git repo
    [Arguments]    ${git_url}   ${ws_name}

    Log To console    cloning ${git_url} to ${TEST_OUTPUT}
    ${result}=  Run Process       git   clone   ${git_url}   ${ws_name}
    ...  cwd=${TEST_OUTPUT}  stdout=stdout.txt  stderr=stderr.txt
    Log Many  stdout: ${result.stdout}  stderr: ${result.stderr}

    ${result}=  Run Process  git  fetch  --all  --prune
    ...  cwd=${TEST_OUTPUT}${/}${ws_name}  stdout=stdout.txt  stderr=stderr.txt
    Log Many  stdout: ${result.stdout}  stderr: ${result.stderr}
    Should Be Equal As Integers  ${result.rc}  0

Reset git repo to default branch
    [Arguments]     ${ws}  ${default_branch_name}

    # checkout remote tag for origin/<default branch>
    ${result}=  Run Process  git  checkout  origin/${default_branch_name}
    ...  cwd=${ws}  stdout=stdout.txt  stderr=stderr.txt
    Log Many	stdout: ${result.stdout}  stderr: ${result.stderr}
    Should Be Equal As Integers  ${result.rc}  0

    # clean non ignored files quietly to avoid log overflow
    ${result}=  Run Process  git  clean  -qfd  cwd=${ws}
    Log Many  stdout: ${result.stdout}  stderr: ${result.stderr}
    Should Be Equal As Integers  ${result.rc}  0

    # reset to restore files
    ${result}=  Run Process  git  reset  --hard
    ...  cwd=${ws}  stdout=stdout.txt  stderr=stderr.txt
    Log Many  stdout: ${result.stdout}  stderr: ${result.stderr}
    Should Be Equal As Integers  ${result.rc}  0

Get default branch from remote
    [Arguments]     ${ws}

    # Set origin head to auto
    ${result}=  Run Process  git  remote  set-head  origin  --auto
    ...  cwd=${ws}
    Log Many	stdout: ${result.stdout}  stderr: ${result.stderr}
    Should Be Equal As Integers  ${result.rc}  0

    # get the head
    ${result}=  Run Process  git  rev-parse  --abbrev-ref  origin/HEAD
    ...  cwd=${ws}
    Log Many	stdout: ${result.stdout}  stderr: ${result.stderr}
    Should Be Equal As Integers  ${result.rc}  0

    # Strip off origin/ from the branch because all other commands
    # add the remote name.
    ${branch}=  Get Substring  ${result.stdout}  7

    [Return]  ${branch}

### Stuart operations ###
Stuart setup
    [Arguments]  ${setting_file}  ${arch}  ${target}  ${packages}  ${tool_chain}  ${ws}
    Log to console  Stuart Setup
    ${result}=   Run Process    stuart_setup
    ...  -c  ${setting_file}  -a  ${arch}  TOOL_CHAIN_TAG\=${tool_chain}  -t  ${target}  -p  ${packages}  TARGET\=${target}
    ...  cwd=${ws}  stdout=stdout.txt  stderr=stderr.txt
    Log Many	stdout: ${result.stdout}  stderr: ${result.stderr}
    Should Be Equal As Integers  ${result.rc}  0

Stuart update
    [Arguments]  ${setting_file}  ${arch}  ${target}  ${packages}  ${tool_chain}  ${ws}
    Log to console  Stuart Update
    ${result}=   Run Process    stuart_update
    ...  -c  ${setting_file}  -a  ${arch}  TOOL_CHAIN_TAG\=${tool_chain}  -t  ${target}  -p  ${packages}  TARGET\=${target}
    ...  cwd=${ws}  stdout=stdout.txt  stderr=stderr.txt
    Log Many	stdout: ${result.stdout}  stderr: ${result.stderr}
    Should Be Equal As Integers  ${result.rc}  0

Stuart platform build
    [Arguments]  ${setting_file}  ${arch}  ${target}  ${tool_chain}  ${ws}
    Log to console  Stuart Build
    ${result}=   Run Process    stuart_build
    ...  -c  ${setting_file}  -a  ${arch}  TOOL_CHAIN_TAG\=${tool_chain}  TARGET\=${target}
    ...  cwd=${ws}  stdout=stdout.txt  stderr=stderr.txt
    Log Many	stdout: ${result.stdout}  stderr: ${result.stderr}
    Should Be Equal As Integers  ${result.rc}  0

Stuart platform run
    [Arguments]  ${setting_file}  ${arch}  ${target}  ${tool_chain}  ${addtional_flags}  ${ws}
    Log to console  Stuart Build Run
    ${result}=   Run Process    stuart_build
    ...  -c  ${setting_file}  -a  ${arch}  TOOL_CHAIN_TAG\=${tool_chain}  TARGET\=${target}  --FlashOnly  ${addtional_flags}
    ...  cwd=${ws}  stdout=stdout.txt  stderr=stderr.txt
    Log Many	stdout: ${result.stdout}  stderr: ${result.stderr}
    Should Be Equal As Integers  ${result.rc}  0

### Edk2 BaseTools Build operations ###
Build BaseTools
    [Arguments]  ${tool_chain}  ${ws}
    Log to console  Compile basetools
    ${result}=   Run Process    python
    ...  BaseTools/Edk2ToolsBuild.py  -t  ${tool_chain}
    ...  cwd=${ws}  shell=True  stdout=stdout.txt  stderr=stderr.txt
    Log Many	stdout: ${result.stdout}  stderr: ${result.stderr}
    Should Be Equal As Integers  ${result.rc}  0
