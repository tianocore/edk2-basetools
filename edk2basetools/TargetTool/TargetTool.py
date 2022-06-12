# @file
# Target Tool Parser
#
#  Copyright (c) 2007 - 2021, Intel Corporation. All rights reserved.<BR>
#
#  SPDX-License-Identifier: BSD-2-Clause-Patent
#

from __future__ import print_function
import edk2basetools.Common.LongFilePathOs as os
import sys
import traceback
from argparse import ArgumentParser

import edk2basetools.Common.EdkLogger as EdkLogger
import edk2basetools.Common.BuildToolError as BuildToolError
from edk2basetools.Common.DataType import *
from edk2basetools.Common.BuildVersion import gBUILD_VERSION
from edk2basetools.Common.LongFilePathSupport import OpenLongFilePath as open
from edk2basetools.Common.TargetTxtClassObject import gDefaultTargetTxtFile

# To Do 1.set clean, 2. add item, if the line is disabled.


class TargetTool():
    def __init__(self, args):
        self.WorkSpace = os.path.normpath(os.getenv('WORKSPACE'))
        self.Arguments = args
        self.Arg = args.Arg
        self.FileName = os.path.normpath(os.path.join(self.WorkSpace, 'Conf', gDefaultTargetTxtFile))
        if os.path.isfile(self.FileName) == False:
            print("%s does not exist." % self.FileName)
            sys.exit(1)
        self.TargetTxtDictionary = {
            TAB_TAT_DEFINES_ACTIVE_PLATFORM: None,
            TAB_TAT_DEFINES_TOOL_CHAIN_CONF: None,
            TAB_TAT_DEFINES_MAX_CONCURRENT_THREAD_NUMBER: None,
            TAB_TAT_DEFINES_TARGET: None,
            TAB_TAT_DEFINES_TOOL_CHAIN_TAG: None,
            TAB_TAT_DEFINES_TARGET_ARCH: None,
            TAB_TAT_DEFINES_BUILD_RULE_CONF: None,
        }
        self.LoadTargetTxtFile(self.FileName)

    def LoadTargetTxtFile(self, filename):
        if os.path.exists(filename) and os.path.isfile(filename):
            return self.ConvertTextFileToDict(filename, '#', '=')
        else:
            raise ParseError('LoadTargetTxtFile() : No Target.txt file exists.')
            return 1

#
# Convert a text file to a dictionary
#
    def ConvertTextFileToDict(self, FileName, CommentCharacter, KeySplitCharacter):
        """Convert a text file to a dictionary of (name:value) pairs."""
        try:
            f = open(FileName, 'r')
            for Line in f:
                if Line.startswith(CommentCharacter) or Line.strip() == '':
                    continue
                LineList = Line.split(KeySplitCharacter, 1)
                if len(LineList) >= 2:
                    Key = LineList[0].strip()
                    if Key.startswith(CommentCharacter) == False and Key in self.TargetTxtDictionary:
                        if Key == TAB_TAT_DEFINES_ACTIVE_PLATFORM or Key == TAB_TAT_DEFINES_TOOL_CHAIN_CONF \
                                or Key == TAB_TAT_DEFINES_MAX_CONCURRENT_THREAD_NUMBER \
                                or Key == TAB_TAT_DEFINES_ACTIVE_MODULE:
                            self.TargetTxtDictionary[Key] = LineList[1].replace('\\', '/').strip()
                        elif Key == TAB_TAT_DEFINES_TARGET or Key == TAB_TAT_DEFINES_TARGET_ARCH \
                                or Key == TAB_TAT_DEFINES_TOOL_CHAIN_TAG or Key == TAB_TAT_DEFINES_BUILD_RULE_CONF:
                            self.TargetTxtDictionary[Key] = LineList[1].split()
            f.close()
            return 0
        except:
            last_type, last_value, last_tb = sys.exc_info()
            traceback.print_exception(last_type, last_value, last_tb)

    def Print(self):
        errMsg = ''
        for Key in self.TargetTxtDictionary:
            if isinstance(self.TargetTxtDictionary[Key], type([])):
                print("%-30s = %s" % (Key, ''.join(elem + ' ' for elem in self.TargetTxtDictionary[Key])))
            elif self.TargetTxtDictionary[Key] is None:
                errMsg += "  Missing %s configuration information, please use TargetTool to set value!" % Key + os.linesep
            else:
                print("%-30s = %s" % (Key, self.TargetTxtDictionary[Key]))

        if errMsg != '':
            print(os.linesep + 'Warning:' + os.linesep + errMsg)

    def RWFile(self, CommentCharacter, KeySplitCharacter, Num):
        try:
            fr = open(self.FileName, 'r')
            fw = open(os.path.normpath(os.path.join(self.WorkSpace, 'Conf\\targetnew.txt')), 'w')

            existKeys = []
            for Line in fr:
                if Line.startswith(CommentCharacter) or Line.strip() == '':
                    fw.write(Line)
                else:
                    LineList = Line.split(KeySplitCharacter, 1)
                    if len(LineList) >= 2:
                        Key = LineList[0].strip()
                        if Key.startswith(CommentCharacter) == False and Key in self.TargetTxtDictionary:
                            if Key not in existKeys:
                                existKeys.append(Key)
                            else:
                                print("Warning: Found duplicate key item in original configuration files!")

                            if Num == 0:
                                Line = "%-30s = \n" % Key
                            else:
                                ret = GetConfigureKeyValue(self, Key)
                                if ret is not None:
                                    Line = ret
                            fw.write(Line)
            for key in self.TargetTxtDictionary:
                if key not in existKeys:
                    print("Warning: %s does not exist in original configuration file" % key)
                    Line = GetConfigureKeyValue(self, key)
                    if Line is None:
                        Line = "%-30s = " % key
                    fw.write(Line)

            fr.close()
            fw.close()
            os.remove(self.FileName)
            os.rename(os.path.normpath(os.path.join(self.WorkSpace, 'Conf\\targetnew.txt')), self.FileName)

        except:
            last_type, last_value, last_tb = sys.exc_info()
            traceback.print_exception(last_type, last_value, last_tb)


def GetConfigureKeyValue(self, Key):
    Line = None
    if Key == TAB_TAT_DEFINES_ACTIVE_PLATFORM and self.Opt.DSCFILE is not None:
        dscFullPath = os.path.join(self.WorkSpace, self.Opt.DSCFILE)
        if os.path.exists(dscFullPath):
            Line = "%-30s = %s\n" % (Key, self.Opt.DSCFILE)
        else:
            EdkLogger.error("TargetTool", BuildToolError.FILE_NOT_FOUND,
                            "DSC file %s does not exist!" % self.Opt.DSCFILE, RaiseError=False)
    elif Key == TAB_TAT_DEFINES_TOOL_CHAIN_CONF and self.Opt.TOOL_DEFINITION_FILE is not None:
        tooldefFullPath = os.path.join(self.WorkSpace, self.Opt.TOOL_DEFINITION_FILE)
        if os.path.exists(tooldefFullPath):
            Line = "%-30s = %s\n" % (Key, self.Opt.TOOL_DEFINITION_FILE)
        else:
            EdkLogger.error("TargetTool", BuildToolError.FILE_NOT_FOUND,
                            "Tooldef file %s does not exist!" % self.Opt.TOOL_DEFINITION_FILE, RaiseError=False)

    elif self.Opt.NUM >= 2:
        Line = "%-30s = %s\n" % (Key, 'Enable')
    elif self.Opt.NUM <= 1:
        Line = "%-30s = %s\n" % (Key, 'Disable')
    elif Key == TAB_TAT_DEFINES_MAX_CONCURRENT_THREAD_NUMBER and self.Opt.NUM is not None:
        Line = "%-30s = %s\n" % (Key, str(self.Opt.NUM))
    elif Key == TAB_TAT_DEFINES_TARGET and self.Opt.TARGET is not None:
        Line = "%-30s = %s\n" % (Key, ''.join(elem + ' ' for elem in self.Opt.TARGET))
    elif Key == TAB_TAT_DEFINES_TARGET_ARCH and self.Opt.TARGET_ARCH is not None:
        Line = "%-30s = %s\n" % (Key, ''.join(elem + ' ' for elem in self.Opt.TARGET_ARCH))
    elif Key == TAB_TAT_DEFINES_TOOL_CHAIN_TAG and self.Opt.TOOL_CHAIN_TAG is not None:
        Line = "%-30s = %s\n" % (Key, self.Opt.TOOL_CHAIN_TAG)
    elif Key == TAB_TAT_DEFINES_BUILD_RULE_CONF and self.Opt.BUILD_RULE_FILE is not None:
        buildruleFullPath = os.path.join(self.WorkSpace, self.Opt.BUILD_RULE_FILE)
        if os.path.exists(buildruleFullPath):
            Line = "%-30s = %s\n" % (Key, self.Opt.BUILD_RULE_FILE)
        else:
            EdkLogger.error("TagetTool", BuildToolError.FILE_NOT_FOUND,
                            "Build rule file %s does not exist!" % self.Opt.BUILD_RULE_FILE, RaiseError=False)
    return Line


VersionNumber = ("0.01" + " " + gBUILD_VERSION)
__version__ = "%(prog)s Version " + VersionNumber
__copyright__ = "Copyright (c) 2007 - 2018, Intel Corporation  All rights reserved."
__usage__ = "%(prog)s [options] {args} \
\nArgs:                                                  \
\n Clean  clean the all default configuration of target.txt. \
\n Print  print the all default configuration of target.txt. \
\n Set    replace the default configuration with expected value specified by option."


def MyOptionParser():
    parser = ArgumentParser(prog="TargetTool.exe", usage=__usage__, description=__copyright__)

    parser.add_argument("Arg", metavar="ARG", type=str, choices=['clean', 'print', 'set'])

    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument("-a", "--arch", action="append", dest="TARGET_ARCH", type=str, choices=['IA32', 'X64', 'ARM', 'AARCH64', 'EBC'],
                        help="ARCHS is one of list: IA32, X64, ARM, AARCH64 or EBC, which replaces target.txt's TARGET_ARCH definition. To specify more archs, please repeat this option. 0 will clear this setting in target.txt and can't combine with other value.")
    parser.add_argument("-p", "--platform", type=str, dest="DSCFILE",
                        help="Specify a DSC file, which replace target.txt's ACTIVE_PLATFORM definition. 0 will clear this setting in target.txt and can't combine with other value.")
    parser.add_argument("-c", "--tooldef", type=str, dest="TOOL_DEFINITION_FILE",
                        help="Specify the WORKSPACE relative path of tool_def.txt file, which replace target.txt's TOOL_CHAIN_CONF definition. 0 will clear this setting in target.txt and can't combine with other value.")
    parser.add_argument("-t", "--target", action="append", type=str, choices=['DEBUG', 'RELEASE', '0'], dest="TARGET",
                        help="TARGET is one of list: DEBUG, RELEASE, which replaces target.txt's TARGET definition. To specify more TARGET, please repeat this option. 0 will clear this setting in target.txt and can't combine with other value.")
    parser.add_argument("-n", "--tagname", type=str, dest="TOOL_CHAIN_TAG",
                        help="Specify the Tool Chain Tagname, which replaces target.txt's TOOL_CHAIN_TAG definition. 0 will clear this setting in target.txt and can't combine with other value.")
    parser.add_argument("-r", "--buildrule", type=str, dest="BUILD_RULE_FILE",
                        help="Specify the build rule configure file, which replaces target.txt's BUILD_RULE_CONF definition. If not specified, the default value Conf/build_rule.txt will be set.")
    parser.add_argument("-m", "--multithreadnum", type=int, choices=range(1, 9), dest="NUM", metavar="[1-8]",
                        help="Specify the multi-thread number which replace target.txt's MAX_CONCURRENT_THREAD_NUMBER. If the value is less than 2, MULTIPLE_THREAD will be disabled. If the value is larger than 1, MULTIPLE_THREAD will be enabled.")
    return parser.parse_args()


if __name__ == '__main__':
    EdkLogger.Initialize()
    EdkLogger.SetLevel(EdkLogger.QUIET)
    if os.getenv('WORKSPACE') is None:
        print("ERROR: WORKSPACE should be specified or edksetup script should be executed before run TargetTool")
        sys.exit(1)

    arguments = MyOptionParser()
    if arguments.TARGET is not None and len(arguments.TARGET) > 1:
        if '0' in arguments.TARGET:
            print("0 will clear the TARGET setting in target.txt and can't combine with other value.")
            sys.exit(1)
    if arguments.TARGET_ARCH is not None and len(arguments.TARGET_ARCH) > 1:
        if '0' in arguments.TARGET_ARCH:
            print("0 will clear the TARGET_ARCH setting in target.txt and can't combine with other value.")
            sys.exit(1)

    try:
        FileHandle = TargetTool(arguments)
        if FileHandle.Arg.lower() == 'print':
            FileHandle.Print()
            sys.exit(0)
        elif FileHandle.Arg.lower() == 'clean':
            FileHandle.RWFile('#', '=', 0)
        else:
            FileHandle.RWFile('#', '=', 1)
    except Exception as e:
        last_type, last_value, last_tb = sys.exc_info()
        traceback.print_exception(last_type, last_value, last_tb)
