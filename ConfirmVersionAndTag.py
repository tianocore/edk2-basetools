## @file
# Quick script to check that the wheel/package created is has a good version
# Official releases should not be made from non-tagged code.
#
# Copyright (c) Microsoft Corporation
#
# SPDX-License-Identifier: BSD-2-Clause-Patent
##

import glob
import os
import sys


# confirm the tag
p = os.path.join(os.getcwd(), "dist")
whl_files = glob.glob(os.path.join(p, "*.whl"))
if(len(whl_files) == 0):
    raise Exception("Couldn't find the wheel file")
if(len(whl_files) != 1):
    for filename in whl_files:
        print(filename)
    raise Exception("Too many wheel files")
rfn = os.path.relpath(whl_files[0], os.getcwd())
v = rfn.split("-")[1]
if v.count(".") != 2:
    raise Exception("Version %s not in format major.minor.patch" % v)
if "dev" in v:
    raise Exception("No Dev versions allowed to be published.")
version = str(v)
print("version: " + version)

# create a git tag at this point if we are running this on the server
if "AGENT_ID" in os.environ or "SYSTEM_JOBID" in os.environ:  # check if we're actually running on the server
    from edk2toollib.utility_functions import RunCmd
    print("Creating tag and pushing")
    ret = RunCmd("git", f"tag v{version}")
    if ret != 0:
        print("error creating tag")
        sys.exit(0)
    ret = RunCmd("git", "push origin --tags")
    if ret != 0:
        print("error pushing")
        sys.exit(0)

sys.exit(0)
