# @file
# Patch value into the binary file.
#
# Copyright (c) 2010 - 2018, Intel Corporation. All rights reserved.<BR>
# SPDX-License-Identifier: BSD-2-Clause-Patent
#

##
# Import Modules
#
import edk2basetools.Common.LongFilePathOs as os
from edk2basetools.Common.LongFilePathSupport import OpenLongFilePath as open
import sys

from argparse import ArgumentParser
from edk2basetools.Common.BuildToolError import *
import edk2basetools.Common.EdkLogger as EdkLogger
from edk2basetools.Common.BuildVersion import gBUILD_VERSION
import array
from edk2basetools.Common.DataType import *

# Version and Copyright
__version_number__ = ("0.10" + " " + gBUILD_VERSION)
__version__ = "%(prog)s Version " + __version_number__
__copyright__ = "Copyright (c) 2010 - 2018, Intel Corporation. All rights reserved."


# PatchBinaryFile method
#
# This method mainly patches the data into binary file.
#
# @param FileName    File path of the binary file
# @param ValueOffset Offset value
# @param TypeName    DataType Name
# @param Value       Value String
# @param MaxSize     MaxSize value
#
# @retval 0     File is updated successfully.
# @retval not 0 File is updated failed.
#
def PatchBinaryFile(FileName, ValueOffset, TypeName, ValueString, MaxSize=0):
    #
    # Length of Binary File
    #
    FileHandle = open(FileName, 'rb')
    FileHandle.seek(0, 2)
    FileLength = FileHandle.tell()
    FileHandle.close()
    #
    # Unify string to upper string
    #
    TypeName = TypeName.upper()
    #
    # Get PCD value data length
    #
    ValueLength = 0
    if TypeName == 'BOOLEAN':
        ValueLength = 1
    elif TypeName == TAB_UINT8:
        ValueLength = 1
    elif TypeName == TAB_UINT16:
        ValueLength = 2
    elif TypeName == TAB_UINT32:
        ValueLength = 4
    elif TypeName == TAB_UINT64:
        ValueLength = 8
    elif TypeName == TAB_VOID:
        if MaxSize == 0:
            return OPTION_MISSING, "PcdMaxSize is not specified for VOID* type PCD."
        ValueLength = int(MaxSize)
    else:
        return PARAMETER_INVALID, "PCD type %s is not valid." % (CommandOptions.PcdTypeName)
    #
    # Check PcdValue is in the input binary file.
    #
    if ValueOffset + ValueLength > FileLength:
        return PARAMETER_INVALID, "PcdOffset + PcdMaxSize(DataType) is larger than the input file size."
    #
    # Read binary file into array
    #
    FileHandle = open(FileName, 'rb')
    ByteArray = array.array('B')
    ByteArray.fromfile(FileHandle, FileLength)
    FileHandle.close()
    OrigByteList = ByteArray.tolist()
    ByteList = ByteArray.tolist()
    #
    # Clear the data in file
    #
    for Index in range(ValueLength):
        ByteList[ValueOffset + Index] = 0
    #
    # Patch value into offset
    #
    SavedStr = ValueString
    ValueString = ValueString.upper()
    ValueNumber = 0
    if TypeName == 'BOOLEAN':
        #
        # Get PCD value for BOOLEAN data type
        #
        try:
            if ValueString == 'TRUE':
                ValueNumber = 1
            elif ValueString == 'FALSE':
                ValueNumber = 0
            ValueNumber = int(ValueString, 0)
            if ValueNumber != 0:
                ValueNumber = 1
        except:
            return PARAMETER_INVALID, "PCD Value %s is not valid dec or hex string." % (ValueString)
        #
        # Set PCD value into binary data
        #
        ByteList[ValueOffset] = ValueNumber
    elif TypeName in TAB_PCD_CLEAN_NUMERIC_TYPES:
        #
        # Get PCD value for UINT* data type
        #
        try:
            ValueNumber = int(ValueString, 0)
        except:
            return PARAMETER_INVALID, "PCD Value %s is not valid dec or hex string." % (ValueString)
        #
        # Set PCD value into binary data
        #
        for Index in range(ValueLength):
            ByteList[ValueOffset + Index] = ValueNumber % 0x100
            ValueNumber = ValueNumber // 0x100
    elif TypeName == TAB_VOID:
        ValueString = SavedStr
        if ValueString.startswith('L"'):
            #
            # Patch Unicode String
            #
            Index = 0
            for ByteString in ValueString[2:-1]:
                #
                # Reserve zero as unicode tail
                #
                if Index + 2 >= ValueLength:
                    break
                #
                # Set string value one by one/ 0x100
                #
                ByteList[ValueOffset + Index] = ord(ByteString)
                Index = Index + 2
        elif ValueString.startswith("{") and ValueString.endswith("}"):
            #
            # Patch {0x1, 0x2, ...} byte by byte
            #
            ValueList = ValueString[1: len(ValueString) - 1].split(',')
            Index = 0
            try:
                for ByteString in ValueList:
                    ByteString = ByteString.strip()
                    if ByteString.upper().startswith('0X'):
                        ByteValue = int(ByteString, 16)
                    else:
                        ByteValue = int(ByteString)
                    ByteList[ValueOffset + Index] = ByteValue % 0x100
                    Index = Index + 1
                    if Index >= ValueLength:
                        break
            except:
                return PARAMETER_INVALID, "PCD Value %s is not valid dec or hex string array." % (ValueString)
        else:
            #
            # Patch ascii string
            #
            Index = 0
            for ByteString in ValueString[1:-1]:
                #
                # Reserve zero as string tail
                #
                if Index + 1 >= ValueLength:
                    break
                #
                # Set string value one by one
                #
                ByteList[ValueOffset + Index] = ord(ByteString)
                Index = Index + 1
    #
    # Update new data into input file.
    #
    if ByteList != OrigByteList:
        ByteArray = array.array('B')
        ByteArray.fromlist(ByteList)
        FileHandle = open(FileName, 'wb')
        ByteArray.tofile(FileHandle)
        FileHandle.close()
    return 0, "Patch Value into File %s successfully." % (FileName)

# Parse command line options
#
# Using standard Python module optparse to parse command line option of this tool.
#
# @retval Options   A optparse.Values object containing the parsed options
# @retval InputFile Path of file to be trimmed
#


def Options():
    # use clearer usage to override default usage message
    UsageString = "%(prog)s -f Offset -u Value -t Type [-s MaxSize] <input_file>"

    Parser = ArgumentParser(description=__copyright__, usage=UsageString)

    Parser.add_argument("input_file", metavar="INPUT FILE", type=str)

    Parser.add_argument('--version', action='version', version=__version__)
    Parser.add_argument("-f", "--offset", dest="PcdOffset", type=int, required=True,
                        help="Start offset to the image is used to store PCD value."),
    Parser.add_argument("-u", "--value", dest="PcdValue", type=str, required=True,
                        help="PCD value will be updated into the image."),
    Parser.add_argument("-t", "--type", dest="PcdTypeName", type=str.upper, required=True, choices=TAB_PCD_NUMERIC_TYPES_VOID,
                        help="The name of PCD data type may be one of VOID*,BOOLEAN, UINT8, UINT16, UINT32, UINT64."),
    Parser.add_argument("-s", "--maxsize", dest="PcdMaxSize", type=int,
                        help="Max size of data buffer is taken by PCD value.It must be set when PCD type is VOID*."),
    Parser.add_argument("-v", "--verbose", dest="LogLevel", action="store_const", const=EdkLogger.VERBOSE,
                        help="Run verbosely"),
    Parser.add_argument("-d", "--debug", dest="LogLevel", type=int,
                        help="Run with debug information"),
    Parser.add_argument("-q", "--quiet", dest="LogLevel", action="store_const", const=EdkLogger.QUIET,
                        help="Run quietly"),
    Parser.add_argument("-?", action="help", help="show this help message and exit"),

    Parser.set_defaults(LogLevel=EdkLogger.INFO)

    Arguments = Parser.parse_args()

    InputFile = Arguments.input_file
    return Options, InputFile

# Entrance method
#
# This method mainly dispatch specific methods per the command line options.
# If no error found, return zero value so the caller of this tool can know
# if it's executed successfully or not.
#
# @retval 0     Tool was successful
# @retval 1     Tool failed
#


def Main():
    try:
        #
        # Check input parameter
        #
        EdkLogger.Initialize()
        CommandOptions, InputFile = Options()
        if CommandOptions.LogLevel < EdkLogger.DEBUG_9:
            EdkLogger.SetLevel(CommandOptions.LogLevel + 1)
        else:
            EdkLogger.SetLevel(CommandOptions.LogLevel)
        if not os.path.exists(InputFile):
            EdkLogger.error("PatchPcdValue", FILE_NOT_FOUND, ExtraData=InputFile)
            return 1
        if CommandOptions.PcdTypeName == TAB_VOID and CommandOptions.PcdMaxSize is None:
            EdkLogger.error("PatchPcdValue", OPTION_MISSING,
                            ExtraData="PcdMaxSize is not specified for VOID* type PCD.")
            return 1
        #
        # Patch value into binary image.
        #
        ReturnValue, ErrorInfo = PatchBinaryFile(
            InputFile, CommandOptions.PcdOffset, CommandOptions.PcdTypeName, CommandOptions.PcdValue, CommandOptions.PcdMaxSize)
        if ReturnValue != 0:
            EdkLogger.error("PatchPcdValue", ReturnValue, ExtraData=ErrorInfo)
            return 1
        return 0
    except:
        return 1


if __name__ == '__main__':
    r = Main()
    sys.exit(r)
