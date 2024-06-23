import re
import os
import subprocess
import CppHeaderParser
from antlr4 import *
from edk2basetools.VfrCompiler.IfrFormPkg import *
from edk2basetools.VfrCompiler.IfrCtypes import *
from edk2basetools.Common.LongFilePathSupport import LongFilePath


class Options:
    def __init__(self):
        # open/close VfrCompiler
        self.LanuchVfrCompiler = False
        self.ModuleName = None
        self.Workspace = None
        self.VFRPP = None
        self.InputFileName = None
        self.BaseFileName = None
        self.IncludePaths = []
        self.OutputDirectory = None
        self.DebugDirectory = None
        self.CreateRecordListFile = True
        self.RecordListFileName = None
        self.CreateIfrPkgFile = True
        self.PkgOutputFileName = None
        self.COutputFileName = None
        self.SkipCPreprocessor = True
        self.CPreprocessorOptions = None
        self.CProcessedVfrFileName = None
        self.HasOverrideClassGuid = False
        self.OverrideClassGuid = None
        self.WarningAsError = False
        self.AutoDefault = False
        self.CheckDefault = False
        self.CreateYamlFile = True
        self.YamlFileName = None
        self.CreateJsonFile = True
        self.JsonFileName = None
        self.UniStrDefFileName = None


class KV:
    def __init__(self, Key, Value) -> None:
        self.Key = Key
        self.Value = Value


class ValueDB:
    def __init__(self, PreVal, PostVal) -> None:
        self.PreVal = PreVal
        self.PostVal = PostVal


class PreProcessDB:
    def __init__(self, Options: Options) -> None:
        self.Options = Options
        self.VfrVarDataTypeDB = VfrVarDataTypeDB()
        self.Preprocessed = False

    def Preprocess(self):
        self.HeaderFiles = self._ExtractHeaderFiles()
        # Read Guid definitions in Header files
        self.HeaderDict = self._GetHeaderDicts(self.HeaderFiles)
        # Read Uni string token/id definitions in StrDef.h file
        self.UniDict = self._GetUniDicts()
        # Read definitions in vfr file
        self.VfrDict = self._GetVfrDicts()
        self.Preprocessed = True

    def TransValue(self, Value):
        if type(Value) == EFI_GUID:
            return Value
        else:
            StrValue = str(Value)
            if self._IsDigit(StrValue):
                return self._ToDigit(StrValue)
            else:
                GuidList = re.findall(r"0x[0-9a-fA-F]+", StrValue)
                GuidList = [int(num, 16) for num in GuidList]
                Guid = EFI_GUID()
                Guid.from_list(GuidList)
                return Guid

    def RevertValue(self, Value) -> str:
        if type(Value) == EFI_GUID:
            return Value.to_string()
        else:
            if ("0x" in Value) or ("0X" in Value):
                StrValue = hex(Value)
            else:
                StrValue = str(Value)
        return StrValue

    def DisplayValue(self, Value, Flag=False):
        if type(Value) == EFI_GUID:
            return Value.to_string()
        else:
            StrValue = str(Value)
            if self._IsDigit(StrValue):
                if Flag:
                    return "STRING_TOKEN" + "(" + StrValue + ")"
                else:
                    return int(StrValue, 0)

            return StrValue

    def GetKey(self, Value):
        if type(Value) == EFI_GUID:
            Value = Value.to_string()
            if Value in self.UniDict.keys():
                return self.UniDict[Value]
            if Value in self.VfrDict.keys():
                return self.VfrDict[Value]
            if Value in self.HeaderDict.keys():
                return self.HeaderDict[Value]
        else:
            Value = "0x%04x" % Value
            if Value in self.UniDict.keys():
                return self.UniDict[Value]
        return Value

    def _ExtractHeaderFiles(self):
        FileName = self.Options.InputFileName
        try:
            fFile = open(LongFilePath(FileName), mode="r")
            line = fFile.readline()
            IsHeaderLine = False
            HeaderFiles = []
            while line:
                if "#include" in line:
                    IsHeaderLine = True
                    if line.find("<") != -1:
                        HeaderFile = line[line.find("<") + 1 : line.find(">")]
                        HeaderFiles.append(HeaderFile)
                    if line.find('"') != -1:
                        l = line.find('"') + 1
                        r = l + line[l:].find('"')
                        HeaderFile = line[l:r]
                        HeaderFiles.append(HeaderFile)
                line = fFile.readline()
                if IsHeaderLine == True and "#include" not in line:
                    break
            fFile.close()
        except:
            EdkLogger.error("VfrCompiler", FILE_PARSE_FAILURE, "File parse failed for %s" % FileName, None)
        return HeaderFiles

    def _GetUniDicts(self):
        if self.Options.UniStrDefFileName == None:
            self.Options.UniStrDefFileName = self.Options.DebugDirectory + self.Options.ModuleName + "StrDefs.h"
        # find UniFile
        FileName = self.Options.UniStrDefFileName
        with open(FileName, "r") as File:
            Content = File.read()
        UniDict = {}
        self._ParseDefines(FileName, UniDict)

        return UniDict

    def _GetHeaderDicts(self, HeaderFiles):
        HeaderDict = {}
        VFRrespPath  = os.path.join(self.Options.OutputDirectory, "vfrpp_resp.txt")
        if os.path.exists(VFRrespPath):
            Command = [
                rf"{self.Options.VFRPP}",
                "/showIncludes",
                f"@{VFRrespPath}",
                self.Options.InputFileName
            ]
            try:
                Process = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                _, Error = Process.communicate()
            except subprocess.CalledProcessError as e:
                print(f"Error executing command: {e}")
                EdkLogger.error("VfrCompiler", COMMAND_FAILURE, ' '.join(Command))
            Pattern = r'Note: including file:\s+(.*)'
            IncludePaths = re.findall(Pattern, Error)
            for IncludePath in IncludePaths:
                self._ParseDefines(IncludePath, HeaderDict)
        else:
            for HeaderFile in HeaderFiles:
                FileList = self._FindIncludeHeaderFile(self.Options.IncludePaths, HeaderFile)
                CppHeader = None
                for File in FileList:
                    if File.find(HeaderFile.replace("/", "\\")) != -1:
                        CppHeader = CppHeaderParser.CppHeader(File)
                        self._ParseDefines(File, HeaderDict)
                if CppHeader == None:
                    EdkLogger.error("VfrCompiler", FILE_NOT_FOUND, "File/directory %s not found in workspace" % (HeaderFile), None)
                self._ParseRecursiveHeader(CppHeader, HeaderDict)

        return HeaderDict

    def _ParseRecursiveHeader(self, CppHeader, HeaderDict):
        if CppHeader != None:
            for Include in CppHeader.includes:
                Include = Include[1:-1]
                IncludeHeaderFileList = self._FindIncludeHeaderFile(self.Options.IncludePaths, Include)
                Flag = False
                for File in IncludeHeaderFileList:
                    if File.find(Include.replace("/", "\\")) != -1:
                        NewCppHeader = CppHeaderParser.CppHeader(File)
                        self._ParseRecursiveHeader(NewCppHeader, HeaderDict)
                        self._ParseDefines(File, HeaderDict)
                        Flag = True
                if Flag == False:
                    EdkLogger.error("VfrCompiler", FILE_NOT_FOUND, "File/directory %s not found in workspace" % Include, None)


    def _GetVfrDicts(self):
        VfrDict = {}
        if self.Options.LanuchVfrCompiler:
            FileName = self.Options.InputFileName
            self._ParseDefines(FileName, VfrDict, True)
        return VfrDict

    def _IsDigit(self, String):
        if String.isdigit():
            return True
        elif (String.startswith('0x') or String.startswith('0X')) and all(char in "0123456789ABCDEFabcdef" for char in String[2:]):
            return True
        else:
            return False

    def _ToDigit(self, String):
        if String.startswith("0x") or String.startswith("0X"):
            return int(String, 16)
        else:
            return int(String)

    def _ParseDefines(self, FileName, Dict, IsVfrDef = False):
        Pattern = r"#define\s+(\w+)\s+(.*?)(?:(?<!\\)\n|$)"
        with open(FileName, "r") as File:
            Content = File.read()

        Matches = re.findall(Pattern, Content, re.DOTALL)
        for Match in Matches:
            Key = Match[0]
            Value = re.sub(r"\s+", " ", Match[1].replace("\\\n", "").strip())
            SubDefineMatches = re.findall(r"#define\s+(\w+)\s+(.*?)(?:(?<!\\)\n|$)", Value, re.DOTALL)
            if SubDefineMatches:
                for SubMatch in SubDefineMatches:
                    SubKey = SubMatch[0]
                    SubValue = re.sub(r"\s+", " ", SubMatch[1].replace("\\\n", "").strip())
                    if SubValue.find("//") != -1:
                        SubValue = SubValue.split("//")[0].strip()

                    if SubValue.find("{") != -1:
                        GuidList = re.findall(r"0x[0-9a-fA-F]+", SubValue)
                        GuidList = [int(num, 16) for num in GuidList]
                        SubValue = EFI_GUID()
                        if len(GuidList) == 11:
                            SubValue.from_list(GuidList)

                    if self.Options.LanuchVfrCompiler:
                        # GUID is unique, to transfer GUID Parsed Value -> GUID Defined Key.
                        if IsVfrDef:
                            # Save def info for yaml generation
                            Dict[SubKey] = SubValue
                            # tranfer value to key for yaml generation
                            if type(SubValue) == EFI_GUID:
                                Dict[SubValue.to_string()] = SubKey
                        else:
                            SubValue = str(SubValue) if type(SubValue) != EFI_GUID else SubValue.to_string()
                            if self._IsDigit(SubValue):
                                SubValue = "0x%04x" % self._ToDigit(SubValue)
                            Dict[SubValue] = SubKey
            else:
                if Value.find("//") != -1:
                    Value = Value.split("//")[0].strip()
                if Value.find("{") != -1:
                    GuidList = re.findall(r"0x[0-9a-fA-F]+", Value)
                    GuidList = [int(num, 16) for num in GuidList]
                    Value = EFI_GUID()
                    if len(GuidList) == 11:
                        Value.from_list(GuidList)

                if self.Options.LanuchVfrCompiler:
                    # GUID is unique, to transfer GUID Parsed Value -> GUID Defined Key.
                    if IsVfrDef:
                        Dict[Key] = Value
                        if type(Value) == EFI_GUID:
                            Dict[Value.to_string()] = Key
                    else:
                        Value = str(Value) if type(Value) != EFI_GUID else Value.to_string()
                        if self._IsDigit(Value):
                            Value = "0x%04x" % self._ToDigit(Value)
                        Dict[Value] = Key

    def _FindIncludeHeaderFile(self, IncludePaths, File):
        Name = File.split("/")[-1]
        FileList = []
        for Start in IncludePaths:
            for Relpath, Dirs, Files in os.walk(Start):
                if Name in Files:
                    FullPath = os.path.join(Start, Relpath, Name)
                    FullPath = FullPath.replace("\\", "/")
                    if FullPath.find(File) != -1:
                        FileList.append(os.path.normpath(os.path.abspath(FullPath)))

        return list(set(FileList))
