## @file
# Test the parser rules for the Python version of Vfr generated through Antlr4.
#
import logging

import pytest
import sys
import os
from antlr4 import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from VfrCompiler.IfrTree import IfrTreeNode
from VfrCompiler.IfrPreProcess import PreProcessDB
from VfrCompiler.VfrSyntaxParser import VfrSyntaxParser
from VfrCompiler.VfrSyntaxVisitor import VfrSyntaxVisitor
from VfrCompiler.VfrSyntaxLexer import VfrSyntaxLexer
from VfrCompiler.IfrPreProcess import Options
from VfrCompiler.IfrUtility import *
from VfrCompiler.IfrCtypes import *

from VfrCompiler.IfrFormPkg import (
    gVfrVarDataTypeDB,
    gVfrDataStorage,
    gFormPkg,
    gIfrFormId,
    gVfrDefaultStore
)


#
# All test case inputs are .i files.
#
class TestVfrcompilSyntax:
    def setup_class(self):
        # self.Cmd = CmdParser()
        self.Options = Options()
        # self.VfrRoot = IfrTreeNode()
        # self.PreProcessDB = PreProcessDB(self.Options)

    def ParseVfrSyntax(self, input):
        """
        Parsing Vfr syntax and generating trees
        Display call access nodes through the visit method.
        """
        gVfrVarDataTypeDB.Clear()
        gVfrDataStorage.Clear()
        gVfrBufferConfig.__init__()
        # gVfrDefaultStore.Clear()
        gVfrDataStorage.Clear()
        gFormPkg.Clear()
        gIfrFormId.Clear()
        # Options = Options()
        # self.VfrRoot = IfrTreeNode()
        InputStream = FileStream(input)
        VfrLexer = VfrSyntaxLexer(InputStream)
        VfrStream = CommonTokenStream(VfrLexer)
        VfrParser = VfrSyntaxParser(VfrStream)
        self.Visitor = VfrSyntaxVisitor(
            PreProcessDB(self.Options), IfrTreeNode(),
            self.Options.OverrideClassGuid
        )

        return VfrParser

    def GetFormsetAttr(self, Flags):
        ChildList = self.Visitor.Root.Child
        for Child in ChildList:
            if Child.OpCode == EFI_IFR_FORM_SET_OP:
                if Flags == "GUID":
                    return Child.Data.FormSet.Guid.to_string()
                elif Flags == "CLASSGUID":
                    return Child.Data.ClassGuid[0].to_string()
                elif Flags == "CLASS":
                    for ch in Child.Child:
                        return ch.Data.ClassStr
                elif Flags == "SUBCLASS":
                    for ch in Child.Child:
                        return ch.Data.SubClassStr
                elif Flags == "FORMID":
                    for ch in Child.Child:
                        if ch.OpCode == EFI_IFR_FORM_OP:
                            return ch.Data.Form, ch.Buffer, ch.Child
                elif Flags == "FORMMAP":
                    for ch in Child.Child:
                        if ch.OpCode == EFI_IFR_FORM_MAP_OP:
                            return ch.Data.FormMap, ch.Data.MethodMapList

                elif Flags == "STATIMAGE":
                    for ch in Child.Child:
                        if ch.OpCode == EFI_IFR_IMAGE_OP:
                            return ch.Data.Image.Id

                elif Flags == "STATVARSTORENAMEVALUE":
                    for ch in Child.Child:
                        if ch.OpCode == EFI_IFR_VARSTORE_NAME_VALUE_OP:
                            return ch.Data.VarStoreNameValue, \
                                ch.Data.NameItemList[0], ch.Data.Type
                elif Flags == "VARSTOREEFI":
                    for ch in Child.Child:
                        if ch.OpCode == EFI_IFR_VARSTORE_EFI_OP:
                            return ch.Data.VarStoreEfi, ch.Data.Type
                elif Flags == "VARSTORE":
                    for ch in Child.Child:
                        if ch.OpCode == EFI_IFR_VARSTORE_OP:
                            return ch.Data.Varstore, ch.Data.Type, ch.Buffer

                elif Flags == "DISABLEIF":
                    for ch in Child.Child:
                        if ch.OpCode == EFI_IFR_DISABLE_IF_OP:
                            return ch.Expression

                elif Flags == "SUPPRESSIF":
                    for ch in Child.Child:
                        if ch.OpCode == EFI_IFR_SUPPRESS_IF_OP:
                            return ch.Expression

    def test_PragmaPackStackDef(self, PragmaPackStack):

        # for index in range(len(PackStackInput)):
        exp = None
        try:
            VfrParser = self.ParseVfrSyntax(PragmaPackStack[0])

            self.Visitor.visit(VfrParser.vfrProgram())
        except Exception as e:
            exp = ValueError(
                "\nError: #pragma pack(pop...) : more pops than pushes")
        if exp != None:
            print(exp.args[0])
            return
        PackStack = gVfrVarDataTypeDB.PackStack
        assert PackStack.Identifier == PragmaPackStack[1]
        assert PackStack.Number == PragmaPackStack[2]

    def test_PragmaPackShowDef(self):
        packShowInput = [
            'TestVfrSourceFile/PackShow.i'
        ]
        for index in range(len(packShowInput)):
            try:
                self.ParseVfrSyntax(packShowInput[index])
            except Exception as e:
                pass

    def test_PragmaPackNumber(self, PragmaPackNumber):
        exp = None
        try:
            VfrParser = self.ParseVfrSyntax(PragmaPackNumber[0])
            self.Visitor.visit(VfrParser.vfrProgram())
        except Exception as e:
            exp = ValueError(
                "Expected PackNumber value: 0 < Packnumber < 16")
        if exp != None:
            if exp.args[
                0] == "Expected PackNumber value: 0 < Packnumber < 16":
                print("\nExpected PackNumber value: 0 < Packnumber < 16")
                return
        PackAlign = gVfrVarDataTypeDB.PackAlign
        ExpPackAlign = (PragmaPackNumber[1] + PragmaPackNumber[1] % 2) if (
                PragmaPackNumber[1] > 1) else \
            PragmaPackNumber[1]

        assert PackAlign == ExpPackAlign

    def test_VfrDataStructDefinition(self):
        """
        Test Struct Definition
        """
        structInput = [
            os.path.join(os.path.dirname(__file__),
                         'TestVfrSourceFile/struct.i'),
        ]
        exceptOutput = [
            {
                "structName": 'VLAN_CONFIGURATION',
                "elementNode": [
                    ['UINT16', 'VlanId'],
                    ['UINT8', 'Priority'],
                    ['UINT8', 'VlanList']
                ]
            },
        ]
        for index in range(len(structInput)):
            VfrParser = self.ParseVfrSyntax(structInput[index],
                                            )
            self.Visitor.visit(VfrParser.vfrDataStructDefinition())
            DataTypeList = gVfrVarDataTypeDB.DataTypeList
            exp = exceptOutput[index]
            assert exp['structName'] == DataTypeList.TypeName

            i = 0
            element = DataTypeList.Members
            while element:
                assert exp['elementNode'][i][1] == element.FieldName
                assert exp['elementNode'][i][0] == element.FieldType.TypeName
                element = element.Next
                i += 1

    def test_VfrDataUnionDefinition(self):
        unionStructInput = [
            os.path.join(os.path.dirname(__file__),
                         'TestVfrSourceFile/unionStruct.i'),
        ]
        unionStructOutput = [
            {
                "TypeName": "u8",
                "elementNode": [
                    ["UINT8", "MinValue"],
                    ["UINT8", "MaxValue"],
                    ["UINT8", "Step"],
                ]
            }
        ]

        for index in range(len(unionStructInput)):
            VfrParser = self.ParseVfrSyntax(unionStructInput[index])
            self.Visitor.visit(VfrParser.vfrDataUnionDefinition())
            DataTypeList = gVfrVarDataTypeDB.DataTypeList
            exp = unionStructOutput[index]
            assert exp["TypeName"] == DataTypeList.TypeName
            element = DataTypeList.Members
            i = 0
            while element:
                assert exp['elementNode'][i][1] == element.FieldName
                assert exp['elementNode'][i][0] == element.FieldType.TypeName
                element = element.Next
                i += 1

    def test_VfrFormSetDefinition(self):
        """
        Test formset format.
        """
        formsetList = [
            os.path.join(os.path.dirname(__file__),
                         'TestVfrSourceFile/formset.i'),
        ]
        exceptOutput = [
            [EFI_GUID(0x4b47d616, 0xa8d6, 0x4552,
                      GuidArray(0x9d, 0x44, 0xcc, 0xad, 0x2e, 0xf, 0x4c, 0xf9)),
             '0x0002', '0x0003',
             '0E A7 16 D6 47 4B D6 A8 52 45 9D 44 CC AD 2E 0F 4C F9 02 00 03 00 01 71 99 03 93 45 85 04 4B B4 5E 32 EB 83 26 04 0E'],
        ]
        for index in range(len(formsetList)):
            VfrParser = self.ParseVfrSyntax(formsetList[index])
            self.Visitor.visit(VfrParser.vfrProgram())
            for ch in self.Visitor.Root.Child:
                if ch.OpCode == EFI_IFR_FORM_SET_OP:

                    assert ch.Data.FormSet.Guid.to_string() == \
                           exceptOutput[index][0].to_string()
                    assert ch.Data.FormSet.FormSetTitle == int(
                        exceptOutput[index][1], 16)
                    assert ch.Data.FormSet.Help == int(exceptOutput[index][2],
                                                       16)
                    # compile opcode
                    SrcBufferList = exceptOutput[index][3].split(' ')
                    DestBuffer = ch.Buffer
                    for i in range(len(SrcBufferList)):
                        assert int(SrcBufferList[i], 16) == DestBuffer[i]

    #
    # FormSet element.
    #
    def test_GuidDefinition(self):
        GuidList = [
            os.path.join(os.path.dirname(__file__),
                         'TestVfrSourceFile/formset_guid.i'),
        ]
        ExpGuidList = [
            EFI_GUID(0x4b47d616, 0xa8d6, 0x4552,
                     GuidArray(0x9d, 0x44, 0xcc, 0xad, 0x2e, 0xf, 0x4c, 0xf9)),
        ]

        for index in range(len(GuidList)):
            VfrParser = self.ParseVfrSyntax(GuidList[index])
            self.Visitor.visit(VfrParser.vfrFormSetDefinition())

            guid = self.GetFormsetAttr("GUID")
            assert ExpGuidList[index].to_string() == guid

    def test_ClassguidDefinition(self):
        GuidList = [
            os.path.join(os.path.dirname(__file__),
                         'TestVfrSourceFile/formset_classguid.i'),
        ]
        ExpGuidList = [
            EFI_GUID(0x4b47d616, 0xa8d6, 0x4552,
                     GuidArray(0x9d, 0x44, 0xcc, 0xad, 0x2e, 0xf, 0x4c, 0xf9)),
        ]

        for index in range(len(GuidList)):
            VfrParser = self.ParseVfrSyntax(GuidList[index])
            self.Visitor.visit(VfrParser.vfrFormSetDefinition())

            ClassGuid = self.GetFormsetAttr("CLASSGUID")
            assert ClassGuid == ExpGuidList[index].to_string()

    def test_ClassDefinition(self):
        ClassNameList = [
            os.path.join(os.path.dirname(__file__),
                         'TestVfrSourceFile/formset_class.i'),
        ]
        ExpClassNameList = [
            'DISK_DEVICE',
        ]

        for index in range(len(ClassNameList)):
            VfrParser = self.ParseVfrSyntax(ClassNameList[index])
            self.Visitor.visit(VfrParser.vfrFormSetDefinition())

            ClassName = self.GetFormsetAttr("CLASS")
            assert ExpClassNameList[index] == ClassName

    def test_SubClassDefinition(self):
        SubClassNameList = [
            os.path.join(os.path.dirname(__file__),
                         "TestVfrSourceFile/formset_subclass.i"),
        ]

        ExpSubClassNameList = [
            'SETUP_APPLICATION'
        ]

        for index in range(len(SubClassNameList)):
            VfrParser = self.ParseVfrSyntax(SubClassNameList[index])
            self.Visitor.visit(VfrParser.vfrFormSetDefinition())

            SubClass = self.GetFormsetAttr("SUBCLASS")
            assert ExpSubClassNameList[index] == SubClass

    def test_VfrStatementVarStoreLinear(self):
        VarStoreListInput = [
            os.path.join(os.path.dirname(__file__),
                         "TestVfrSourceFile/formset_varstore.i"),
        ]
        VarStoreListOutput = [
            ['ISCSI_CONFIG_IFR_NVDATA', '0x6666',
             EFI_GUID(0x4b47d616, 0xa8d6, 0x4552,
                      GuidArray(0x9d, 0x44, 0xcc, 0xad, 0x2e, 0xf, 0x4c, 0xf9)),
             '24 2E 16 D6 47 4B D6 A8 52 45 9D 44 CC AD 2E 0F 4C F9 66 66 3C 45 49 53 43 53 49 5F 43 4F 4E 46 49 47 5F 49 46 52 5F 4E 56 44 41 54 41 00']
        ]

        for index in range(len(VarStoreListInput)):
            # try:
            VfrParser = self.ParseVfrSyntax(VarStoreListInput[index])
            self.Visitor.visit(VfrParser.vfrProgram())
            # except Exception as e:
            #     pass

            VarStore, Type, Buffer = self.GetFormsetAttr("VARSTORE")
            assert Type == VarStoreListOutput[index][0]
            assert VarStore.VarStoreId == int(VarStoreListOutput[index][1],
                                              16)
            assert VarStore.Guid.to_string() == VarStoreListOutput[index][
                2].to_string()

            # compile Opcode
            SrcBufferList = VarStoreListOutput[index][3].split(' ')
            for i in range(len(SrcBufferList)):
                assert int(SrcBufferList[i], 16) == Buffer[i]

    def test_vfrFormDefinition(self):
        FormIdListInput = [
            os.path.join(os.path.dirname(__file__),
                         "TestVfrSourceFile/formset_formid.i"),
        ]
        ExpFormIdList = [
            ['0x0002', '0x0005',
             [
                 '01 86 02 00 05 00',
                 [
                     '5F 15 35 17 0B 0F A0 87 93 41 B2 66 53 8C 38 AF 48 CE 00 00 30',
                     '5F 15 35 17 0B 0F A0 87 93 41 B2 66 53 8C 38 AF 48 CE 00 FF FF',
                     '29 02'
                 ]
             ],
             ],
        ]

        for index in range(len(FormIdListInput)):
            VfrParser = self.ParseVfrSyntax(FormIdListInput[index])
            self.Visitor.visit(VfrParser.vfrProgram())

            Form, FormChildBuffer, FormChilds = self.GetFormsetAttr("FORMID")
            assert int(ExpFormIdList[index][0], 16) == Form.FormId
            assert int(ExpFormIdList[index][1], 16) == Form.FormTitle

            # compile OpCode
            FormSrcBufferList = ExpFormIdList[index][2][0].split(' ')

            for i in range(len(FormSrcBufferList)):
                assert int(FormSrcBufferList[i], 16) == FormChildBuffer[i]

            # Compile FormId child Opcode
            FormChildSrcList = ExpFormIdList[index][2][1]
            for j in range(len(FormChildSrcList)):
                ChildSrcList = FormChildSrcList[j].split(' ')
                ChildDest = FormChilds[j].Buffer
                for k in range(len(ChildSrcList)):
                    assert int(ChildSrcList[k], 16) == ChildDest[k]

    def test_vfrFormMapDefinition(self):
        FormMapList = [
            os.path.join(os.path.dirname(__file__),
                         'TestVfrSourceFile/formset_formmap.i'),
        ]
        ExpFormMapList = [
            ['0x0001', '0x0001', EFI_GUID(0xe58809f8, 0xfbc1, 0x48e2,
                                          GuidArray(0x88, 0x3a, 0xa3, 0x0f,
                                                    0xdc, 0x4b, 0x44, 0x1e))]
        ]

        for index in range(len(FormMapList)):
            VfrParser = self.ParseVfrSyntax(FormMapList[index])
            self.Visitor.visit(VfrParser.vfrProgram())

            FormMap, MethodMapList = self.GetFormsetAttr("FORMMAP")
            assert FormMap.FormId == int(ExpFormMapList[index][0], 16)
            for MethodMap in MethodMapList:
                assert MethodMap.MethodTitle == int(ExpFormMapList[index][1],
                                                    16)
                assert MethodMap.MethodIdentifier.to_string() == \
                       ExpFormMapList[index][2].to_string()

    def test_vfrStatementImage(self):
        StatementImageList = [
            os.path.join(os.path.dirname(__file__),
                         "TestVfrSourceFile/formset_StatImage.i")
        ]
        ExpStatImageList = [
            '0x0001',
        ]

        for index in range(len(StatementImageList)):
            VfrParser = self.ParseVfrSyntax(StatementImageList[index])
            self.Visitor.visit(VfrParser.vfrFormSetDefinition())

            StatImageToken = self.GetFormsetAttr("STATIMAGE")
            assert StatImageToken == int(ExpStatImageList[index], 16)

    def test_vfrStatementVarStoreNameValue(self):
        DeafultStoreList = [
            os.path.join(os.path.dirname(__file__),
                         'TestVfrSourceFile/formset_StatVarStoreNameValue.i'),
        ]
        ExpDeafultStoreList = [
            ['0x0001', 'ISCSI_CONFIG_IFR_NVDATA', '0x0002',
             EFI_GUID(0x4b47d616, 0xa8d6, 0x4552,
                      GuidArray(0x9d, 0x44, 0xcc, 0xad, 0x2e, 0xf, 0x4c, 0xf9))]
        ]

        for index in range(len(DeafultStoreList)):
            VfrParser = self.ParseVfrSyntax(DeafultStoreList[index])

            self.Visitor.visit(VfrParser.vfrProgram())

            StatVarStoreNameValue, Name, Type = self.GetFormsetAttr(
                "STATVARSTORENAMEVALUE")
            assert StatVarStoreNameValue.VarStoreId == int(
                ExpDeafultStoreList[index][0], 16)
            assert Type == ExpDeafultStoreList[index][1]
            assert Name == int(ExpDeafultStoreList[index][2], 16)
            assert StatVarStoreNameValue.Guid.to_string() == \
                   ExpDeafultStoreList[index][3].to_string()

    def test_vfrStatementVarStoreEfi(self):
        VarStoreEfiList = [
            os.path.join(os.path.dirname(__file__),
                         'TestVfrSourceFile/formset_statementvarstoreefi.i'),
        ]
        ExpVarStoreEfiList = [
            ['0x0001', '0x0007', 'PCH_SETUP',
             EFI_GUID(0x4570b7f1, 0xade8, 0x4943,
                      GuidArray(0x8d, 0xc3, 0x40, 0x64, 0x72, 0x84, 0x23,
                                0x84))]
        ]
        for index in range(len(VarStoreEfiList)):
            VfrParser = self.ParseVfrSyntax(VarStoreEfiList[index])

            self.Visitor.visit(VfrParser.vfrProgram())

            VarStoreEfi, Type = self.GetFormsetAttr("VARSTOREEFI")
            assert Type == ExpVarStoreEfiList[index][2]
            assert VarStoreEfi.VarStoreId == int(ExpVarStoreEfiList[index][0],
                                                 16)
            assert VarStoreEfi.Attributes == int(ExpVarStoreEfiList[index][1],
                                                 16)
            assert VarStoreEfi.Guid.to_string() == ExpVarStoreEfiList[index][
                3].to_string()

    def test_vfrStatementDisableIfFormSet(self):
        DisableIfList = [
            os.path.join(os.path.dirname(__file__),
                         'TestVfrSourceFile/formset_disableif.i'),
        ]
        ExpDisableIfList = [
            'TRUE'
        ]

        for index in range(len(DisableIfList)):
            VfrParser = self.ParseVfrSyntax(DisableIfList[index])
            self.Visitor.visit(VfrParser.vfrProgram())
            Expression = self.GetFormsetAttr("DISABLEIF")
            assert Expression == ExpDisableIfList[index]

    def test_vfrStatementSuppressIfFormSet(self):
        SuppressIfList = [
            os.path.join(os.path.dirname(__file__),
                         'TestVfrSourceFile/formset_suppressif.i'),
        ]

        ExpSuppressIfList = [
            'TRUE'
        ]

        for index in range(len(SuppressIfList)):
            VfrParser = self.ParseVfrSyntax(SuppressIfList[index])

            self.Visitor.visit(VfrParser.vfrProgram())
            Expression = self.GetFormsetAttr("SUPPRESSIF")
            assert Expression == ExpSuppressIfList[index]


if __name__ == '__main__':
    pytest.main(['-v', 'test_vfr_syntax.py'])
