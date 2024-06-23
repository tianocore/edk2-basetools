import re
import os
import sys
import yaml
import logging
import shutil
import subprocess
import time
import argparse
from antlr4 import *
from edk2basetools.VfrCompiler.VfrSyntaxParser import *
from edk2basetools.VfrCompiler.VfrSyntaxVisitor import *
from edk2basetools.VfrCompiler.VfrSyntaxLexer import *
from edk2basetools.VfrCompiler.IfrCommon import *
from edk2basetools.VfrCompiler.IfrTree import *
from edk2basetools.VfrCompiler.IfrPreProcess import *
from edk2basetools.VfrCompiler.IfrError import *
from edk2basetools.Common.LongFilePathSupport import LongFilePath


class COMPILER_RUN_STATUS(Enum):
    STATUS_STARTED = 0
    STATUS_INITIALIZED = 1
    STATUS_VFR_PREPROCESSED = 2
    STATUS_VFR_COMPILEED = 3
    STATUS_VFR_GENBINARY = 4
    STATUS_YAML_GENERATED = 5
    STATUS_YAML_PREPROCESSED = 6
    STATUS_YAML_COMPILED = 7
    STATUS_YAML_DLT_CONSUMED = 8
    STATUS_YAML_GENBINARY = 9
    STATUS_FINISHED = 10
    STATUS_FAILED = 11
    STATUS_DEAD = 12


"""
 This is how we invoke the C preprocessor on the VFR source file
 to resolve #defines, #includes, etc. To make C source files
 shareable between VFR and drivers, define VFRCOMPILE so that
 #ifdefs can be used in shared .h files.
"""
PREPROCESSOR_COMMAND = "cl "
PREPROCESSOR_OPTIONS = "/nologo /E /TC /DVFRCOMPILE "

# Specify the filename extensions for the files we generate.
VFR__FILENAME_EXTENSION = ".vfr"
VFR_PREPROCESS_FILENAME_EXTENSION = ".i"
VFR_PACKAGE_FILENAME_EXTENSION = ".hpk"
VFR_RECORDLIST_FILENAME_EXTENSION = ".lst"
VFR_YAML_FILENAME_EXTENSION = ".yml"
VFR_JSON_FILENAME_EXTENSION = ".json"

WARNING_LOG_LEVEL = 15
UTILITY_NAME = "VfrCompiler"

parser = argparse.ArgumentParser(
    description="VfrCompiler",
    epilog="VfrCompile version {} \
                               Build {} Copyright (c) 2004-2016 Intel Corporation.\
                               All rights reserved.".format(
        VFR_COMPILER_VERSION, BUILD_VERSION
    ),
)
parser.add_argument("InputFileName", help="Input source file name")
parser.add_argument("--vfr", dest="LaunchVfrCompiler", action="store_true", help="Launch VfrCompiler")
parser.add_argument(
    "--version",
    action="version",
    version="VfrCompile version {} Build {}".format(VFR_COMPILER_VERSION, BUILD_VERSION),
    help="prints version info",
)
parser.add_argument("-l", dest="CreateRecordListFile", help="create an output IFR listing file")
parser.add_argument("-c", dest="CreateYamlFile", help="create Yaml file")
parser.add_argument("-j", dest="CreateJsonFile", help="create Json file")
parser.add_argument("-w", dest="Workspace", help="workspace")
parser.add_argument(
    "-o",
    "--output-directory",
    "-od",
    dest="OutputDirectory",
    help="deposit all output files to directory OutputDir, \
                    default is current directory",
)
parser.add_argument(
    "-oo",
    "--old-output-directory",
    "-ood",
    dest="OldOutputDirectory",
    help="Former directory OutputDir of output files, \
                    default is current directory",
)
parser.add_argument(
    "-b",
    "--create-ifr-package",
    "-ibin",
    dest="CreateIfrPkgFile",
    help="create an IFR HII pack file",
)
parser.add_argument(
    "-n",
    "--no-pre-processing",
    "-nopp",
    dest="SkipCPreprocessor",
    help="do not preprocessing input file",
)
parser.add_argument(
    "-f",
    "--pre-processing-flag",
    "-ppflag",
    dest="CPreprocessorOptions",
    help="C-preprocessor argument",
)  #
parser.add_argument("-s", "--string-db", dest="StringFileName", help="input uni string package file")
parser.add_argument(
    "-g",
    "--guid",
    dest="OverrideClassGuid",
    help="override class guid input,\
                    format is xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
)
parser.add_argument("-wae", "--warning-as-error", dest="WarningAsError", help="treat warning as an error")
parser.add_argument(
    "-a",
    "--autodefault",
    dest="AutoDefault",
    help="generate default value for question opcode if some default is missing",
)
parser.add_argument(
    "-d",
    "--checkdefault",
    dest="CheckDefault",
    help="check the default information in a question opcode",
)
parser.add_argument("-m", "--modulename", dest="ModuleName", help="Module name")


class CmdParser:
    def __init__(self, Args, Argc):
        self.Options = Options()
        self.RunStatus = COMPILER_RUN_STATUS.STATUS_STARTED
        self.PreProcessCmd = PREPROCESSOR_COMMAND
        self.PreProcessOpt = PREPROCESSOR_OPTIONS
        self.OptionIntialization(Args, Argc)

    def OptionIntialization(self, Args, Argc):
        Status = EFI_SUCCESS

        if Argc == 1:
            parser.print_help()
            self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD)
            return

        if Args.LaunchVfrCompiler:
            self.Options.LaunchVfrCompiler = True

        if Args.CreateRecordListFile:
            self.Options.CreateRecordListFile = True

        if Args.ModuleName:
            self.Options.ModuleName = Args.ModuleName

        if Args.OutputDirectory:
            self.Options.OutputDirectory = Args.OutputDirectory
            if self.Options.OutputDirectory == None:
                EdkLogger.error("VfrCompiler", OPTION_MISSING, "-o missing output directory name")
                self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD)
                return
            LastChar = self.Options.OutputDirectory[len(self.Options.OutputDirectory) - 1]
            if LastChar != "/" and LastChar != "\\":
                if self.Options.OutputDirectory.find("/") != -1:
                    self.Options.OutputDirectory += "/"
                    self.Options.DebugDirectory = os.path.dirname(os.path.dirname(self.Options.OutputDirectory)) + "/DEBUG/"
                else:
                    self.Options.OutputDirectory += "\\"
                    self.Options.DebugDirectory = os.path.dirname(os.path.dirname(self.Options.OutputDirectory)) + "\\DEBUG\\"
            EdkLogger.debug(9, "Output Directory {}".format(self.Options.OutputDirectory))

        if Args.Workspace:
            self.Options.Workspace  = Args.Workspace
            IsInCludePathLine = False
            HasVFRPPLine = False
            self.Options.IncludePaths = []
            MakeFile = os.path.join(os.path.dirname(os.path.dirname(self.Options.OutputDirectory)), 'Makefile')
            with open(MakeFile, 'r') as File:
                for Line in File:
                    if Line.find("INC =  \\") != -1:
                        IsInCludePathLine = True
                        continue
                    if Line.find("VFRPP = ") != -1:
                        HasVFRPPLine = True
                        self.Options.VFRPP = Line.split('=')[1].strip()
                        continue
                    if IsInCludePathLine:
                        Line = Line.lstrip().rstrip(" \\\n\r")
                        if Line.startswith('/IC'):
                            InCludePath = Line.replace('/IC', 'C', 1)
                            self.Options.IncludePaths.append(InCludePath)
                        elif Line.startswith('/Ic'):
                            InCludePath = Line.replace('/Ic', 'C', 1)
                            self.Options.IncludePaths.append(InCludePath)
                        elif Line.startswith('/I$(WORKSPACE)'):
                            InCludePath = Line.replace('/I$(WORKSPACE)', self.Options.Workspace, 1)
                            self.Options.IncludePaths.append(InCludePath)
                        elif Line.startswith('/I$(DEBUG_DIR)'):
                            InCludePath = self.Options.DebugDirectory
                            self.Options.IncludePaths.append(InCludePath)
                        elif HasVFRPPLine == False:
                            IsInCludePathLine = False
                        else:
                            break

        if Args.OldOutputDirectory:
            self.Options.OldOutputDirectory = Args.OldOutputDirectory
            if self.Options.OldOutputDirectory == None:
                EdkLogger.error("VfrCompiler", OPTION_MISSING, "-oo missing output directory name")
                self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD)
                return
            EdkLogger.debug(9, "Old Output Directory {}".format(self.Options.OldOutputDirectory))

        if Args.CreateIfrPkgFile:
            self.Options.CreateIfrPkgFile = True

        if Args.CreateYamlFile:
            self.Options.CreateYamlFile = True

        if Args.CreateJsonFile:
            self.Options.CreateJsonFile = True

        if Args.SkipCPreprocessor:
            self.Options.SkipCPreprocessor = True

        if Args.CPreprocessorOptions:
            Options = Args.CPreprocessorOptions
            if Options == None:
                EdkLogger.error(
                    "VfrCompiler",
                    OPTION_MISSING,
                    "-od - missing C-preprocessor argument",
                )
                self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD)
                return
            self.Options.CPreprocessorOptions += " " + Options

        if Args.StringFileName:
            StringFileName = Args.StringFileName
            if StringFileName == None:
                EdkLogger.error("VfrCompiler", OPTION_MISSING, "-s missing input string file name")
                self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD)
                return
            gVfrStringDB.SetStringFileName(StringFileName)
            EdkLogger.debug(9, "Input string file path {}".format(StringFileName))

        if Args.OverrideClassGuid:
            res = StringToGuid(Args.OverrideClassGuid, self.Options.OverrideClassGuid)
            if type(res) == "int":
                Status = res
            else:
                Status = res[0]
                self.Options.OverrideClassGuid = res[1]

            if EFI_ERROR(Status):
                EdkLogger.error(
                    "VfrCompiler",
                    FORMAT_INVALID,
                    "Invalid format: {}".format(Args.OverrideClassGuid),
                )
                self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD)
                return

            self.Options.HasOverrideClassGuid = True

        if Args.WarningAsError:
            self.Options.WarningAsError = True

        if Args.AutoDefault:
            self.Options.AutoDefault = True

        if Args.CheckDefault:
            self.Options.CheckDefault = True

        if Args.InputFileName:
            self.Options.InputFileName = Args.InputFileName
            if self.Options.InputFileName == None:
                EdkLogger.error("VfrCompiler", OPTION_MISSING, "Input file name is not specified.")
                self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD)
                return

            if self.Options.OutputDirectory == None:
                self.Options.OutputDirectory = ""

        if self.SetBaseFileName() != 0:
            self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD)
            return

        if self.SetPkgOutputFileName() != 0:
            self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD)
            return

        if self.SetCOutputFileName() != 0:
            self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD)
            return

        if self.SetPreprocessorOutputFileName() != 0:
            self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD)
            return

        if self.SetRecordListFileName() != 0:
            self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD)
            return

        if self.SetSourceYamlFileName() != 0:
            self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD)
            return

        if self.SetJsonFileName() != 0:
            self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD)
            return

    def SetBaseFileName(self):
        if self.Options.InputFileName == None:
            return -1
        pFileName = self.Options.InputFileName
        while (pFileName.find("\\") != -1) or (pFileName.find("/") != -1):
            if pFileName.find("\\") != -1:
                i = pFileName.find("\\")
            else:
                i = pFileName.find("/")

            if i == len(pFileName) - 1:
                return -1

            pFileName = pFileName[i + 1 :]

        if pFileName == "" or pFileName.find(".") == -1:
            return -1

        self.Options.BaseFileName = pFileName[: pFileName.find(".")]
        return 0

    def SetPkgOutputFileName(self):
        if self.Options.BaseFileName == None:
            return -1
        if self.Options.LaunchVfrCompiler:
            self.Options.PkgOutputFileName = self.Options.OutputDirectory + "PyVfr_" + self.Options.BaseFileName + ".hpk"
        return 0

    def SetCOutputFileName(self):
        if self.Options.BaseFileName == None:
            return -1
        if self.Options.LaunchVfrCompiler:
            self.Options.COutputFileName = self.Options.DebugDirectory + "PyVfr_" + self.Options.BaseFileName + ".c"
        return 0

    def SetPreprocessorOutputFileName(self):
        if self.Options.BaseFileName == None:
            return -1
        self.Options.CProcessedVfrFileName = self.Options.OutputDirectory +  self.Options.BaseFileName + ".i"
        return 0

    def SetRecordListFileName(self):
        if self.Options.BaseFileName == None:
            return -1
        if self.Options.LaunchVfrCompiler:
            self.Options.RecordListFileName = self.Options.DebugDirectory + "PyVfr_" + self.Options.BaseFileName + ".lst"
        return 0

    def SetSourceYamlFileName(self):
        if self.Options.BaseFileName == None:
            return -1
        self.Options.YamlFileName = self.Options.DebugDirectory + self.Options.BaseFileName + ".yml"
        return 0

    def SetJsonFileName(self):
        if self.Options.BaseFileName == None:
            return -1
        self.Options.JsonFileName = self.Options.DebugDirectory + self.Options.BaseFileName + ".json"
        return 0

    def FindIncludeHeaderFile(self, Start, Name):
        FileList = []
        for Relpath, Dirs, Files in os.walk(Start):
            if Name in Files:
                FullPath = os.path.join(Start, Relpath, Name)
                FileList.append(os.path.normpath(os.path.abspath(FullPath)))
        return FileList

    def SET_RUN_STATUS(self, Status):
        self.RunStatus = Status

    def IS_RUN_STATUS(self, Status):
        return self.RunStatus == Status

class VfrCompiler:
    def __init__(self, Cmd: CmdParser):
        self.Clear()
        self.Options = Cmd.Options
        self.RunStatus = Cmd.RunStatus
        self.VfrRoot = IfrTreeNode()
        self.PreProcessDB = PreProcessDB(self.Options)
        self.VfrTree = IfrTree(self.VfrRoot, self.PreProcessDB, self.Options)
        if (not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_FAILED)) \
            and (not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD)):
            self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_INITIALIZED)

    def Clear(self):
        gVfrVarDataTypeDB.Clear()
        gVfrDefaultStore.Clear()
        gVfrDataStorage.Clear()
        gFormPkg.Clear()
        gIfrFormId.Clear()

    def PreProcess(self):
        if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_INITIALIZED):
            if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD):
                self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_FAILED)
        else:
            if self.Options.SkipCPreprocessor == False:
                # call C precessor first in the tool itself, but currently not support here
                self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_FAILED)
            else:
                # makefile will call cl commands to generate .i file
                # do not need to run C preprocessor in this tool itself
                self.PreProcessDB.Preprocess()
                self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_VFR_PREPROCESSED)

    def Compile(self):
        InFileName = self.Options.CProcessedVfrFileName
        if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_VFR_PREPROCESSED):
            EdkLogger.error(
                "VfrCompiler",
                FILE_PARSE_FAILURE,
                "compile error in file %s" % InFileName,
                InFileName,
            )
            self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_FAILED)
        else:
            gVfrErrorHandle.SetInputFile(self.Options.InputFileName)
            gVfrErrorHandle.SetWarningAsError(self.Options.WarningAsError)

            try:
                InputStream = FileStream(InFileName)
                VfrLexer = VfrSyntaxLexer(InputStream)
                VfrStream = CommonTokenStream(VfrLexer)
                VfrParser = VfrSyntaxParser(VfrStream)
            except:
                EdkLogger.error(
                    "VfrCompiler",
                    FILE_OPEN_FAILURE,
                    "File open failed for %s" % InFileName,
                    InFileName,
                )
                if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD):
                    self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_FAILED)
                return
            self.Visitor = VfrSyntaxVisitor(self.PreProcessDB, self.VfrRoot, self.Options.OverrideClassGuid)
            self.Visitor.visit(VfrParser.vfrProgram())

            if self.Visitor.ParserStatus != 0:
                if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD):
                    EdkLogger.error(
                        "VfrCompiler",
                        FILE_PARSE_FAILURE,
                        "compile error in file %s" % InFileName,
                        InFileName,
                    )
                    self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_FAILED)
                return

            if gFormPkg.HavePendingUnassigned() == True:
                gFormPkg.PendingAssignPrintAll()
                if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD):
                    EdkLogger.error(
                        "VfrCompiler",
                        FILE_PARSE_FAILURE,
                        "compile error in file %s" % InFileName,
                        InFileName,
                    )
                    self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_FAILED)
                return

            self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_VFR_COMPILEED)
            if self.Options.CreateJsonFile:
                self.VfrTree.DumpJson()

    def GenBinary(self):
        if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_VFR_COMPILEED):
            if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD):
                self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_FAILED)
        else:
            if self.Options.CreateIfrPkgFile:
                self.VfrTree.GenBinary()

    def GenCFile(self):
        if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_VFR_COMPILEED):
            if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD):
                self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_FAILED)
        else:
            if self.Options.CreateIfrPkgFile:
                self.VfrTree.GenCFile()

    def GenRecordListFile(self):
        if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_VFR_COMPILEED):
            if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD):
                self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_FAILED)
        else:
            if self.Options.CreateRecordListFile:
                self.VfrTree.GenRecordListFile()

    def GenBinaryFiles(self):
        if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_VFR_COMPILEED):
            if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD):
                self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_FAILED)
        else:
            self.VfrTree.GenBinaryFiles()
            self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_FINISHED)

    def DumpSourceYaml(self):
        if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_VFR_COMPILEED) \
            and not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_FINISHED):
            if not self.IS_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_DEAD):
                self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_FAILED)
        else:
            if self.Options.CreateYamlFile:
                self.VfrTree.DumpSourceYaml()
            self.SET_RUN_STATUS(COMPILER_RUN_STATUS.STATUS_FINISHED)

    def SET_RUN_STATUS(self, Status):
        self.RunStatus = Status

    def IS_RUN_STATUS(self, Status):
        return self.RunStatus == Status


def main():
    Args = parser.parse_args()
    Argc = len(sys.argv)
    EdkLogger.SetLevel(WARNING_LOG_LEVEL)
    Cmd = CmdParser(Args, Argc)
    if Cmd.Options.LaunchVfrCompiler:
        Compiler = VfrCompiler(Cmd)
        Compiler.PreProcess()
        Compiler.Compile()
        Compiler.GenBinaryFiles()
        Compiler.DumpSourceYaml()

    Status = Compiler.RunStatus
    if Status == COMPILER_RUN_STATUS.STATUS_DEAD or Status == COMPILER_RUN_STATUS.STATUS_FAILED:
        return 2

    return EFI_SUCCESS


if __name__ == "__main__":
    exit(main())
