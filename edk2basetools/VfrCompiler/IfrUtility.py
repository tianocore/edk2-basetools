## @file
# Vfr common library functions.
#
# Copyright (c) 2022-, Intel Corporation. All rights reserved.<BR>
# SPDX-License-Identifier: BSD-2-Clause-Patent
##
import os
from enum import Enum
from VfrCompiler.IfrCtypes import *
from VfrCompiler.IfrError import gVfrErrorHandle, VfrReturnCode
from VfrCompiler.IfrCommon import EFI_SUCCESS, EFI_NOT_FOUND, RETURN_SUCCESS
from abc import ABCMeta, abstractmethod
from Common.LongFilePathSupport import LongFilePath

VFR_PACK_SHOW = 0x02
VFR_PACK_ASSIGN = 0x01
VFR_PACK_PUSH = 0x04
VFR_PACK_POP = 0x08
DEFAULT_PACK_ALIGN = 0x8
DEFAULT_ALIGN = 1
ZERO_ALIGN = 0
MAX_PACK_ALIGN = 0x10
MAX_NAME_LEN = 64
MAX_BIT_WIDTH = 32
EFI_VARSTORE_ID_MAX = 0xFFFF
EFI_BITS_SHIFT_PER_UINT32 = 0x5
EFI_BITS_PER_UINT32 = 1 << EFI_BITS_SHIFT_PER_UINT32
EFI_FREE_VARSTORE_ID_BITMAP_SIZE = int((EFI_VARSTORE_ID_MAX + 1) / EFI_BITS_PER_UINT32)


class SVfrPackStackNode:
    def __init__(self, Identifier, Number):
        self.Identifier = Identifier
        self.Number = Number
        self.Next = None

    def Match(self, Identifier):
        if Identifier is None:
            return True
        elif self.Identifier is None:
            return False
        return self.Identifier == Identifier


class SVfrDataType:
    def __init__(self, TypeName=""):
        self.TypeName = TypeName
        self.Type = 0
        self.Align = 1
        self.TotalSize = 0
        self.HasBitField = False
        self.Members = None
        self.Next = None


class SVfrDataField:
    def __init__(self, FieldName=None):
        self.FieldName = FieldName
        self.FieldType = None
        self.Offset = 0
        self.ArrayNum = 0
        self.IsBitField = False
        self.BitWidth = 0
        self.BitOffset = 0
        self.Next = None


class InternalTypes:
    def __init__(self, TypeName, Type, Size, Align):
        self.TypeName = TypeName
        self.Type = Type
        self.Size = Size
        self.Align = Align


gInternalTypesTable = [
    InternalTypes("UINT64", EFI_IFR_TYPE_NUM_SIZE_64, sizeof(c_ulonglong), sizeof(c_ulonglong)),
    InternalTypes("UINT32", EFI_IFR_TYPE_NUM_SIZE_32, sizeof(c_ulong), sizeof(c_ulong)),
    InternalTypes("UINT16", EFI_IFR_TYPE_NUM_SIZE_16, sizeof(c_ushort), sizeof(c_ushort)),
    InternalTypes("UINT8", EFI_IFR_TYPE_NUM_SIZE_8, sizeof(c_ubyte), sizeof(c_ubyte)),
    InternalTypes("BOOLEAN", EFI_IFR_TYPE_BOOLEAN, sizeof(c_ubyte), sizeof(c_ubyte)),
    InternalTypes("EFI_GUID", EFI_IFR_TYPE_OTHER, sizeof(EFI_GUID), sizeof(c_ubyte * 8)),
    InternalTypes("EFI_HII_DATE", EFI_IFR_TYPE_DATE, sizeof(EFI_HII_DATE), sizeof(c_ushort)),
    InternalTypes("EFI_STRING_ID", EFI_IFR_TYPE_STRING, sizeof(c_ushort), sizeof(c_ushort)),
    InternalTypes("EFI_HII_TIME", EFI_IFR_TYPE_TIME, sizeof(EFI_HII_TIME), sizeof(c_ubyte)),
    InternalTypes("EFI_HII_REF", EFI_IFR_TYPE_REF, sizeof(EFI_HII_REF), sizeof(EFI_GUID)),
]


class VfrVarDataTypeDB:
    def __init__(self):
        self.PackAlign = DEFAULT_PACK_ALIGN
        self.PackStack = None
        self.DataTypeList = None
        self.NewDataType = None
        self.CurrDataType = None
        self.CurrDataField = None
        self.FirstNewDataTypeName = None
        self.InternalTypesListInit()

    def Clear(self):
        self.PackAlign = DEFAULT_PACK_ALIGN
        self.PackStack = None
        self.DataTypeList = None
        self.NewDataType = None
        self.CurrDataType = None
        self.CurrDataField = None
        self.FirstNewDataTypeName = None
        self.InternalTypesListInit()

    def InternalTypesListInit(self):
        for i in range(0, len(gInternalTypesTable)):
            pNewType = SVfrDataType()
            pNewType.TypeName = gInternalTypesTable[i].TypeName
            pNewType.Type = gInternalTypesTable[i].Type
            pNewType.Align = gInternalTypesTable[i].Align
            pNewType.TotalSize = gInternalTypesTable[i].Size

            if gInternalTypesTable[i].TypeName == "EFI_HII_DATE":
                pYearField = SVfrDataField()
                pMonthField = SVfrDataField()
                pDayField = SVfrDataField()

                pYearField.FieldName = "Year"
                pYearField.FieldType, _ = self.GetDataType("UINT16")
                pYearField.Offset = 0
                pYearField.Next = pMonthField
                pYearField.ArrayNum = 0
                pYearField.IsBitField = False

                pMonthField.FieldName = "Month"
                pMonthField.FieldType, _ = self.GetDataType("UINT8")
                pMonthField.Offset = 2
                pMonthField.Next = pDayField
                pMonthField.ArrayNum = 0
                pMonthField.IsBitField = False

                pDayField.FieldName = "Day"
                pDayField.FieldType, _ = self.GetDataType("UINT8")
                pDayField.Offset = 3
                pDayField.Next = None
                pDayField.ArrayNum = 0
                pDayField.IsBitField = False

                pNewType.Members = pYearField

            elif gInternalTypesTable[i].TypeName == "EFI_HII_TIME":
                pHoursField = SVfrDataField()
                pMinutesField = SVfrDataField()
                pSecondsField = SVfrDataField()

                pHoursField.FieldName = "Hours"
                pHoursField.FieldType, _ = self.GetDataType("UINT8")
                pHoursField.Offset = 0
                pHoursField.Next = pMinutesField
                pHoursField.ArrayNum = 0
                pHoursField.IsBitField = False

                pMinutesField.FieldName = "Minutes"
                pMinutesField.FieldType, _ = self.GetDataType("UINT8")
                pMinutesField.Offset = 1
                pMinutesField.Next = pSecondsField
                pMinutesField.ArrayNum = 0
                pMinutesField.IsBitField = False

                pSecondsField.FieldName = "Seconds"
                pSecondsField.FieldType, _ = self.GetDataType("UINT8")
                pSecondsField.Offset = 2
                pSecondsField.Next = None
                pSecondsField.ArrayNum = 0
                pSecondsField.IsBitField = False

                pNewType.Members = pHoursField

            elif gInternalTypesTable[i].TypeName == "EFI_HII_REF":
                pQuestionIdField = SVfrDataField()
                pFormIdField = SVfrDataField()
                pFormSetGuidField = SVfrDataField()
                pDevicePathField = SVfrDataField()

                pQuestionIdField.FieldName = "QuestionId"
                pQuestionIdField.FieldType, _ = self.GetDataType("UINT16")
                pQuestionIdField.Offset = 0
                pQuestionIdField.Next = pFormIdField
                pQuestionIdField.ArrayNum = 0
                pQuestionIdField.IsBitField = False

                pFormIdField.FieldName = "FormId"
                pFormIdField.FieldType, _ = self.GetDataType("UINT16")
                pFormIdField.Offset = 2
                pFormIdField.Next = pFormSetGuidField
                pFormIdField.ArrayNum = 0
                pFormIdField.IsBitField = False

                pFormSetGuidField.FieldName = "FormSetGuid"
                pFormSetGuidField.FieldType, _ = self.GetDataType("EFI_GUID")
                pFormSetGuidField.Offset = 4
                pFormSetGuidField.Next = pDevicePathField
                pFormSetGuidField.ArrayNum = 0
                pFormSetGuidField.IsBitField = False

                pDevicePathField.FieldName = "DevicePath"
                pDevicePathField.FieldType, _ = self.GetDataType("EFI_STRING_ID")
                pDevicePathField.Offset = 20
                pDevicePathField.Next = None
                pDevicePathField.ArrayNum = 0
                pDevicePathField.IsBitField = False

                pNewType.Members = pQuestionIdField

            pNewType.Next = None
            pNewType.Next = self.DataTypeList
            self.DataTypeList = pNewType
            pNewType = None

    def GetDataTypeList(self):
        return self.DataTypeList

    def Pack(self, LineNum, Action, Identifier=None, Number=DEFAULT_PACK_ALIGN):
        if Action & VFR_PACK_SHOW:
            Msg = str.format("value of pragma pack(show) == %d" % (self.PackAlign))
            gVfrErrorHandle.PrintMsg(LineNum, "Warning", Msg)

        if Action & VFR_PACK_PUSH:
            pNew = SVfrPackStackNode(Identifier, self.PackAlign)
            if pNew is None:
                return VfrReturnCode.VFR_RETURN_FATAL_ERROR
            pNew.Next = self.PackStack
            self.PackStack = pNew

        if Action & VFR_PACK_POP:
            pNode = None
            if self.PackStack is None:
                gVfrErrorHandle.PrintMsg(LineNum, "Error", "#pragma pack(pop...) : more pops than pushes")

            pNode = self.PackStack
            while pNode is not None:
                if pNode.Match(Identifier) is True:
                    self.PackAlign = pNode.Number
                    self.PackStack = pNode.Next
                pNode = pNode.Next

        if Action & VFR_PACK_ASSIGN:
            PackAlign = (Number + Number % 2) if (Number > 1) else Number
            if PackAlign == ZERO_ALIGN or PackAlign > MAX_PACK_ALIGN:
                gVfrErrorHandle.PrintMsg(LineNum, "Error", "expected pragma parameter to be '1', '2', '4', '8', or '16'")
            else:
                self.PackAlign = PackAlign

        return VfrReturnCode.VFR_RETURN_SUCCESS

    def DeclareDataTypeBegin(self):
        pNewType = SVfrDataType()

        pNewType.TypeName = ""
        pNewType.Type = EFI_IFR_TYPE_OTHER
        pNewType.Align = DEFAULT_ALIGN
        pNewType.TotalSize = 0
        pNewType.HasBitField = False
        pNewType.Members = None
        pNewType.Next = None
        self.NewDataType = pNewType

    def SetNewTypeType(self, Type):
        if self.NewDataType is None:
            return VfrReturnCode.VFR_RETURN_ERROR_SKIPED

        if Type is None:
            return VfrReturnCode.VFR_RETURN_FATAL_ERROR
        # need to limit the value of the type
        self.NewDataType.Type = Type

        return VfrReturnCode.VFR_RETURN_SUCCESS

    def SetNewTypeTotalSize(self, Size):
        self.NewDataType.TotalSize = Size

    def SetNewTypeAlign(self, Align):
        self.NewDataType.Align = Align

    def SetNewTypeName(self, TypeName):
        if self.NewDataType is None:
            return VfrReturnCode.VFR_RETURN_ERROR_SKIPED

        if TypeName is None:
            return VfrReturnCode.VFR_RETURN_FATAL_ERROR

        if len(TypeName) >= MAX_NAME_LEN:
            return VfrReturnCode.VFR_RETURN_INVALID_PARAMETER

        pType = self.DataTypeList
        while pType is not None:
            if pType.TypeName == TypeName:
                return VfrReturnCode.VFR_RETURN_REDEFINED
            pType = pType.Next

        self.NewDataType.TypeName = TypeName
        return VfrReturnCode.VFR_RETURN_SUCCESS

    def AlignStuff(self, Size, Align):
        return Align - (Size) % (Align)

    def DeclareDataTypeEnd(self):
        if self.NewDataType.TypeName == "":
            return

        if self.NewDataType.TotalSize % self.NewDataType.Align != 0:
            self.NewDataType.TotalSize += self.AlignStuff(self.NewDataType.TotalSize, self.NewDataType.Align)
        self.NewDataType.Next = self.DataTypeList
        self.DataTypeList = self.NewDataType
        if self.FirstNewDataTypeName is None:
            self.FirstNewDataTypeName = self.NewDataType.TypeName

        self.NewDataType = None

    # two definitions
    def GetDataTypeSizeByTypeName(self, TypeName):
        Size = 0
        pDataType = self.DataTypeList
        while pDataType is not None:
            if pDataType.TypeName == TypeName:
                Size = pDataType.TotalSize
                return Size, VfrReturnCode.VFR_RETURN_SUCCESS
            pDataType = pDataType.Next

        return Size, VfrReturnCode.VFR_RETURN_UNDEFINED

    def GetDataTypeSizeByDataType(self, DataType):
        Size = 0
        DataType = DataType & 0x0F
        # For user defined data type, the size can't be got by this function.
        if DataType == EFI_IFR_TYPE_OTHER:
            return Size, VfrReturnCode.VFR_RETURN_SUCCESS
        pDataType = self.DataTypeList
        while pDataType is not None:
            if DataType == pDataType.Type:
                Size = pDataType.TotalSize
                return Size, VfrReturnCode.VFR_RETURN_SUCCESS
            pDataType = pDataType.Next

        return Size, VfrReturnCode.VFR_RETURN_UNDEFINED

    def ExtractStructTypeName(self, VarStr):
        try:
            index = VarStr.index(".")
        except ValueError:
            return VarStr, len(VarStr)
        else:
            return VarStr[0:index], index + 1

    def ExtractFieldNameAndArrary(self, VarStr, s):
        ArrayIdx = INVALID_ARRAY_INDEX
        s_copy = s
        while s < len(VarStr) and VarStr[s] != "." and VarStr[s] != "[" and VarStr[s] != "]":
            s += 1

        FName = VarStr[s_copy:s]

        if s == len(VarStr):
            return ArrayIdx, s, FName, VfrReturnCode.VFR_RETURN_SUCCESS

        if VarStr[s] == ".":
            s += 1
            return ArrayIdx, s, FName, VfrReturnCode.VFR_RETURN_SUCCESS

        if VarStr[s] == "[":
            s += 1
            try:
                e = s + VarStr[s:].index("]")

            except ValueError:
                return None, None, None, VfrReturnCode.VFR_RETURN_DATA_STRING_ERROR
            else:
                ArrayStr = VarStr[s:e]
                ArrayIdx = int(ArrayStr)
                if VarStr[e] == "]":
                    e += 1
                if e < len(VarStr) and (VarStr[e] == "."):
                    e += 1
                return ArrayIdx, e, FName, VfrReturnCode.VFR_RETURN_SUCCESS

        if VarStr[s] == "]":
            return None, None, None, VfrReturnCode.VFR_RETURN_DATA_STRING_ERROR

        return ArrayIdx, s, FName, VfrReturnCode.VFR_RETURN_SUCCESS

    def GetTypeField(self, FName, Type):
        if FName is None or Type is None:
            return None, VfrReturnCode.VFR_RETURN_FATAL_ERROR

        pField = Type.Members
        while pField is not None:
            if Type.Type == EFI_IFR_TYPE_TIME:
                if FName == "Hour":
                    FName = "Hours"
                elif FName == "Minute":
                    FName == "Minutes"
                elif FName == "Second":
                    FName = "Seconds"
            if pField.FieldName == FName:
                Field = pField
                return Field, VfrReturnCode.VFR_RETURN_SUCCESS

            pField = pField.Next

        return None, VfrReturnCode.VFR_RETURN_UNDEFINED

    def IsThisBitField(self, VarStrName):
        TName, i = self.ExtractStructTypeName(VarStrName)
        pType, ReturnCode = self.GetDataType(TName)
        if ReturnCode != VfrReturnCode.VFR_RETURN_SUCCESS:
            return None, ReturnCode
        pField = None
        while i < len(VarStrName):
            # i start from field
            _, i, FName, ReturnCode = self.ExtractFieldNameAndArrary(VarStrName, i)
            if ReturnCode != VfrReturnCode.VFR_RETURN_SUCCESS:
                return None, ReturnCode
            pField, ReturnCode = self.GetTypeField(FName, pType)
            if ReturnCode != VfrReturnCode.VFR_RETURN_SUCCESS:
                return None, ReturnCode
            pType = pField.FieldType

        if pField is not None and pField.IsBitField:
            return True, ReturnCode
        return False, ReturnCode

    def GetFieldOffset(self, Field, ArrayIdx, IsBitField):
        if Field is None:
            return None, VfrReturnCode.VFR_RETURN_FATAL_ERROR

        if (ArrayIdx != INVALID_ARRAY_INDEX) and (Field.ArrayNum == 0 or Field.ArrayNum <= ArrayIdx):
            return None, VfrReturnCode.VFR_RETURN_ERROR_ARRARY_NUM

        Idx = 0 if ArrayIdx == INVALID_ARRAY_INDEX else ArrayIdx
        if IsBitField:
            Offset = Field.BitOffset + Field.FieldType.TotalSize * Idx * 8
        else:
            Offset = Field.Offset + Field.FieldType.TotalSize * Idx

        return Offset, VfrReturnCode.VFR_RETURN_SUCCESS

    def GetFieldWidth(self, Field):
        if Field is None:
            return 0
        return Field.FieldType.Type

    def GetFieldSize(self, Field, ArrayIdx, BitField):
        if Field is None:
            return VfrReturnCode.VFR_RETURN_FATAL_ERROR

        if (ArrayIdx == INVALID_ARRAY_INDEX) and (Field.ArrayNum != 0):
            return Field.FieldType.TotalSize * Field.ArrayNum
        elif BitField:
            return Field.BitWidth
        return Field.FieldType.TotalSize

    def GetDataFieldInfo(self, VarStr):
        # VarStr -> Type.Field
        Offset = 0
        Type = EFI_IFR_TYPE_OTHER
        Size = 0
        BitField = False

        TName, i = self.ExtractStructTypeName(VarStr)

        pType, ReturnCode = self.GetDataType(TName)
        if ReturnCode != VfrReturnCode.VFR_RETURN_SUCCESS:
            return Offset, Type, Size, BitField, ReturnCode

        BitField, ReturnCode = self.IsThisBitField(VarStr)

        if ReturnCode != VfrReturnCode.VFR_RETURN_SUCCESS:
            return Offset, Type, Size, BitField, ReturnCode

        # if it is not struct data type
        Type = pType.Type
        Size = pType.TotalSize

        while i < len(VarStr):
            ArrayIdx, i, FName, ReturnCode = self.ExtractFieldNameAndArrary(VarStr, i)
            if ReturnCode != VfrReturnCode.VFR_RETURN_SUCCESS:
                return Offset, Type, Size, BitField, ReturnCode
            pField, ReturnCode = self.GetTypeField(FName, pType)
            if ReturnCode != VfrReturnCode.VFR_RETURN_SUCCESS:
                return Offset, Type, Size, BitField, ReturnCode
            pType = pField.FieldType
            Tmp, ReturnCode = self.GetFieldOffset(pField, ArrayIdx, pField.IsBitField)
            if ReturnCode != VfrReturnCode.VFR_RETURN_SUCCESS:
                return Offset, Type, Size, BitField, ReturnCode

            if BitField and pField.IsBitField is False:
                Offset = int(Offset + Tmp * 8)
            else:
                Offset = int(Offset + Tmp)

            Type = self.GetFieldWidth(pField)
            Size = self.GetFieldSize(pField, ArrayIdx, BitField)

        return Offset, Type, Size, BitField, VfrReturnCode.VFR_RETURN_SUCCESS


    def DataTypeAddField(self, FieldName, TypeName, ArrayNum, FieldInUnion):
        pFieldType, ReturnCode = self.GetDataType(TypeName)

        if ReturnCode != VfrReturnCode.VFR_RETURN_SUCCESS:
            return ReturnCode

        MaxDataTypeSize = self.NewDataType.TotalSize

        if len(FieldName) >= MAX_NAME_LEN:
            return VfrReturnCode.VFR_RETURN_INVALID_PARAMETER

        pTmp = self.NewDataType.Members
        while pTmp is not None:
            if pTmp.FieldName == FieldName:
                return VfrReturnCode.VFR_RETURN_REDEFINED
            pTmp = pTmp.Next

        Align = min(self.PackAlign, pFieldType.Align)
        pNewField = SVfrDataField()
        if pNewField is None:
            return VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES
        pNewField.FieldName = FieldName
        pNewField.FieldType = pFieldType
        pNewField.ArrayNum = ArrayNum
        pNewField.IsBitField = False

        if self.NewDataType.TotalSize % Align == 0:
            pNewField.Offset = self.NewDataType.TotalSize
        else:
            pNewField.Offset = self.NewDataType.TotalSize + self.AlignStuff(self.NewDataType.TotalSize, Align)

        if self.NewDataType.Members is None:
            self.NewDataType.Members = pNewField
            pNewField.Next = None
        else:
            pTmp = self.NewDataType.Members
            while pTmp.Next is not None:
                pTmp = pTmp.Next
            pTmp.Next = pNewField
            pNewField.Next = None

        self.NewDataType.Align = min(self.PackAlign, max(pFieldType.Align, self.NewDataType.Align))

        if FieldInUnion:
            if MaxDataTypeSize < pNewField.FieldType.TotalSize:
                self.NewDataType.TotalSize = pNewField.FieldType.TotalSize
            pNewField.Offset = 0
        else:
            Num = ArrayNum if ArrayNum != 0 else 1
            self.NewDataType.TotalSize = pNewField.Offset + (pNewField.FieldType.TotalSize) * Num

        return VfrReturnCode.VFR_RETURN_SUCCESS

    def DataTypeAddBitField(self, FieldName, TypeName, Width, FieldInUnion):
        pFieldType, ReturnCode = self.GetDataType(TypeName)
        if ReturnCode != VfrReturnCode.VFR_RETURN_SUCCESS:
            return ReturnCode

        if Width > MAX_BIT_WIDTH:
            return VfrReturnCode.VFR_RETURN_BIT_WIDTH_ERROR

        if Width > (pFieldType.TotalSize) * 8:
            return VfrReturnCode.VFR_RETURN_BIT_WIDTH_ERROR

        if (FieldName is not None) and (len(FieldName) >= MAX_NAME_LEN):
            return VfrReturnCode.VFR_RETURN_INVALID_PARAMETER

        if Width == 0 and FieldName is not None:
            return VfrReturnCode.VFR_RETURN_INVALID_PARAMETER

        pTmp = self.NewDataType.Members
        while pTmp is not None:
            if FieldName is not None and pTmp.FieldName == FieldName:
                return VfrReturnCode.VFR_RETURN_REDEFINED
            pTmp = pTmp.Next

        Align = min(self.PackAlign, pFieldType.Align)
        UpdateTotalSize = False

        pNewField = SVfrDataField()
        if pNewField is None:
            return VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        MaxDataTypeSize = self.NewDataType.TotalSize

        pNewField.FieldName = FieldName
        pNewField.FieldType = pFieldType
        pNewField.IsBitField = True
        pNewField.BitWidth = Width
        pNewField.ArrayNum = 0
        pNewField.BitOffset = 0
        pNewField.Offset = 0

        if self.NewDataType.Members is None:
            self.NewDataType.Members = pNewField
            pNewField.Next = None
        else:
            pTmp = self.NewDataType.Members
            while pTmp.Next is not None:
                pTmp = pTmp.Next
            pTmp.Next = pNewField
            pNewField.Next = None

        if FieldInUnion:
            pNewField.Offset = 0
            if MaxDataTypeSize < pNewField.FieldType.TotalSize:
                self.NewDataType.TotalSize = pNewField.FieldType.TotalSize
        else:
            # Check whether the bit fields can be contained within one FieldType.
            cond1 = (pTmp is not None) and (pTmp.IsBitField) and (pTmp.FieldType.TypeName == pNewField.FieldType.TypeName)
            cond2 = (pTmp is not None) and (pTmp.BitOffset - pTmp.Offset * 8 + pTmp.BitWidth + pNewField.BitWidth <= pNewField.FieldType.TotalSize * 8)
            if cond1 and cond2:
                pNewField.BitOffset = pTmp.BitOffset + pTmp.BitWidth
                pNewField.Offset = pTmp.Offset

                if pNewField.BitWidth == 0:
                    pNewField.BitWidth = pNewField.FieldType.TotalSize * 8 - (pNewField.BitOffset - pTmp.Offset * 8)
            else:
                pNewField.BitOffset = self.NewDataType.TotalSize * 8
                UpdateTotalSize = True

        if UpdateTotalSize:
            if self.NewDataType.TotalSize % Align == 0:
                pNewField.Offset = self.NewDataType.TotalSize
            else:
                pNewField.Offset = self.NewDataType.TotalSize + self.AlignStuff(self.NewDataType.TotalSize, Align)
            self.NewDataType.TotalSize = pNewField.Offset + pNewField.FieldType.TotalSize

        self.NewDataType.Align = min(self.PackAlign, max(pFieldType.Align, self.NewDataType.Align))
        self.NewDataType.HasBitField = True
        return VfrReturnCode.VFR_RETURN_SUCCESS

    def GetDataType(self, TypeName):
        if TypeName is None:
            return None, VfrReturnCode.VFR_RETURN_ERROR_SKIPED

        DataType = self.DataTypeList
        while DataType is not None:
            if DataType.TypeName == TypeName:
                return DataType, VfrReturnCode.VFR_RETURN_SUCCESS
            DataType = DataType.Next
        return None, VfrReturnCode.VFR_RETURN_UNDEFINED

    def DataTypeHasBitField(self, TypeName):
        if TypeName is None:
            return False

        pType = self.DataTypeList
        while pType is not None:
            if pType.TypeName == TypeName:
                break
            pType = pType.Next

        if pType is None:
            return False

        pTmp = pType.Members
        while pTmp is not None:
            if pTmp.IsBitField:
                return True
            pTmp = pTmp.Next
        return False

    def Dump(self, f):
        f.write("\n\n*************\n")
        f.write("\t\tPackAlign = " + str(self.PackAlign) + "\n")
        pNode = self.DataTypeList
        while pNode is not None:
            f.write("\t\tstruct {} : Align : [{}]  TotalSize : [{:#x}]\n\n".format(pNode.TypeName, pNode.Align, pNode.TotalSize))
            f.write("\t\tstruct {}".format(str(pNode.TypeName)) + "\t{\n")
            FNode = pNode.Members
            while FNode is not None:
                if FNode.ArrayNum > 0:
                    f.write("\t\t\t+{:0>8d}[{:0>8x}] {}[{}] <{}>\n".format(FNode.Offset, FNode.Offset, FNode.FieldName, FNode.ArrayNum, FNode.FieldType.TypeName))
                    f.write("\t\t\t+{:0>8d}[{:0>8x}] {}[{}] <{}>\n".format(FNode.Offset, FNode.BitOffset, FNode.FieldName, FNode.ArrayNum, FNode.FieldType.TypeName))
                elif FNode.FieldName is not None:
                    f.write("\t\t\t+{:0>8d}[{:0>8x}] {} <{}>\n".format(FNode.Offset, FNode.Offset, FNode.FieldName, FNode.FieldType.TypeName))
                    f.write("\t\t\t+{:0>8d}[{:0>8x}] {} <{}>\n".format(FNode.Offset, FNode.BitOffset, FNode.FieldName, FNode.FieldType.TypeName))
                else:
                    f.write("\t\t\t+{:0>8d}[{:0>8x}] <{}>\n".format(FNode.Offset, FNode.Offset, FNode.FieldType.TypeName))
                    f.write("\t\t\t+{:0>8d}[{:0>8x}] <{}>\n".format(FNode.Offset, FNode.BitOffset, FNode.FieldType.TypeName))
                FNode = FNode.Next
            f.write("\t\t};\n")
            f.write("---------------------------------------------------------------\n")
            pNode = pNode.Next
        f.write("***************************************************************\n")


class SVfrDefaultStoreNode:
    def __init__(self, ObjAddr=None, RefName="", DefaultStoreNameId=0, DefaultId=0):
        self.ObjAddr = ObjAddr
        self.RefName = RefName
        self.DefaultStoreNameId = DefaultStoreNameId
        self.DefaultId = DefaultId
        self.Next = None


class VfrDefaultStore:
    def __init__(self):
        self.DefaultStoreList = None

    def Clear(self):
        self.DefaultStoreList = None

    def RegisterDefaultStore(self, ObjAddr: EFI_IFR_DEFAULTSTORE, RefName, DefaultStoreNameId, DefaultId):
        if RefName == "" or RefName is None:
            return VfrReturnCode.VFR_RETURN_FATAL_ERROR

        pNode = self.DefaultStoreList
        while pNode is not None:
            if pNode.RefName == RefName:
                return VfrReturnCode.VFR_RETURN_REDEFINED
            pNode = pNode.Next

        pNode = SVfrDefaultStoreNode(ObjAddr, RefName, DefaultStoreNameId, DefaultId)

        if pNode is None:
            return VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        pNode.Next = self.DefaultStoreList
        self.DefaultStoreList = pNode

        return VfrReturnCode.VFR_RETURN_SUCCESS

    def UpdateDefaultType(self, DefaultNode):
        pNode = self.DefaultStoreList
        while pNode is not None:
            if pNode.ObjAddr.DefaultId == DefaultNode.Data.GetDefaultId():
                DefaultNode.Data.SetType(pNode.RefName)
            pNode = pNode.Next

    def DefaultIdRegistered(self, DefaultId):
        pNode = self.DefaultStoreList
        while pNode is not None:
            if pNode.DefaultId == DefaultId:
                return True
            pNode = pNode.Next

        return False

    def ReRegisterDefaultStoreById(self, DefaultId, RefName, DefaultStoreNameId):
        pNode = self.DefaultStoreList
        while pNode is not None:
            if pNode.DefaultId == DefaultId:
                break
            pNode = pNode.Next

        if pNode is None:
            return None, VfrReturnCode.VFR_RETURN_UNDEFINED

        if pNode.DefaultStoreNameId == EFI_STRING_ID_INVALID:
            pNode.DefaultStoreNameId = DefaultStoreNameId
            pNode.RefName = RefName
            if pNode.ObjAddr is not None:
                pNode.ObjAddr.DefaultName = DefaultStoreNameId
        else:
            return None, VfrReturnCode.VFR_RETURN_REDEFINED

        return pNode, VfrReturnCode.VFR_RETURN_SUCCESS

    def GetDefaultId(self, RefName):
        pTmp = self.DefaultStoreList
        while pTmp is not None:
            if pTmp.RefName == RefName:
                DefaultId = pTmp.DefaultId
                return DefaultId, VfrReturnCode.VFR_RETURN_SUCCESS
            pTmp = pTmp.Next
        return None, VfrReturnCode.VFR_RETURN_UNDEFINED

    def BufferVarStoreAltConfigAdd(self, DefaultId, BaseInfo, VarStoreName, VarStoreGuid, Type, Value):
        if VarStoreName is None:
            return VfrReturnCode.VFR_RETURN_FATAL_ERROR
        pNode = self.DefaultStoreList
        while pNode is not None:
            if pNode.DefaultId == DefaultId:
                break
            pNode = pNode.Next
        if pNode is None:
            return VfrReturnCode.VFR_RETURN_UNDEFINED
        gVfrBufferConfig.Open()
        if gVfrBufferConfig.Select(VarStoreName, VarStoreGuid) == 0:
            Returnvalue = gVfrBufferConfig.Write(
                "a",
                VarStoreName,
                VarStoreGuid,
                pNode.DefaultId,
                Type,
                BaseInfo.Info.VarOffset,
                BaseInfo.VarTotalSize,
                Value,
            )
            if Returnvalue != 0:
                gVfrBufferConfig.Close()
                return VfrReturnCode(Returnvalue)
        gVfrBufferConfig.Close()
        return VfrReturnCode.VFR_RETURN_SUCCESS


class EFI_VFR_VARSTORE_TYPE(Enum):
    EFI_VFR_VARSTORE_INVALID = 0
    EFI_VFR_VARSTORE_BUFFER = 1
    EFI_VFR_VARSTORE_EFI = 2
    EFI_VFR_VARSTORE_NAME = 3
    EFI_VFR_VARSTORE_BUFFER_BITS = 4


class EfiVar:
    def __init__(self, VarName=0, VarSize=0):
        self.EfiVarName = VarName
        self.EfiVarSize = VarSize


DEFAULT_NAME_TABLE_ITEMS = 1024


class SVfrVarStorageNode:
    def __init__(
        self,
        VarStoreName="",
        VarStoreId=0,
        Guid=None,
        Attributes=0,
        Flag=True,
        EfiValue=None,
        DataType=None,
        BitsVarstore=False,
    ):
        self.Guid = Guid
        self.VarStoreName = VarStoreName
        self.VarStoreId = VarStoreId
        self.AssignedFlag = Flag
        self.Attributes = Attributes
        self.Next = None
        self.EfiVar = EfiValue
        self.DataType = DataType
        self.NameSpace = []

        if EfiValue is not None:
            self.VarstoreType = EFI_VFR_VARSTORE_TYPE.EFI_VFR_VARSTORE_EFI
        elif DataType is not None:
            if BitsVarstore:
                self.VarstoreType = EFI_VFR_VARSTORE_TYPE.EFI_VFR_VARSTORE_BUFFER_BITS
            else:
                self.VarstoreType = EFI_VFR_VARSTORE_TYPE.EFI_VFR_VARSTORE_BUFFER
        else:
            self.VarstoreType = EFI_VFR_VARSTORE_TYPE.EFI_VFR_VARSTORE_NAME


class SConfigItem:
    def __init__(self, Name=None, Guid=None, Id=None, Type=None, Offset=None, Width=None, Value=None):
        self.Name = Name
        self.Guid = Guid
        self.Id = Id
        if Type is not None:
            # list of Offset/Value in the varstore
            self.InfoStrList = SConfigInfo(Type, Offset, Width, Value)
        else:
            self.InfoStrList = None
        self.Next = None


class SConfigInfo:
    def __init__(self, Type, Offset, Width, Value):
        self.Type = Type
        self.Offset = Offset
        self.Width = Width
        self.Next = None
        self.Value = Value


class VfrBufferConfig:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.ItemListHead = None
        self.ItemListTail = None
        self.ItemListPos = None

    def GetVarItemList(self):
        return self.ItemListHead

    @abstractmethod
    def Open(self):
        self.ItemListPos = self.ItemListHead

    @abstractmethod
    def Close(self):
        self.ItemListPos = None

    @abstractmethod
    def Select(self, Name, Guid, Id=None):
        if Name is None or Guid is None:
            self.ItemListPos = self.ItemListHead
            return 0
        p = self.ItemListHead
        while p is not None:
            if p.Name != Name or p.Guid.__cmp__(Guid) is False:
                p = p.Next
                continue
            if Id is not None:
                if p.Id is None or p.Id != Id:
                    p = p.Next
                    continue
            elif p.Id is not None:
                p = p.Next
                continue
            self.ItemListPos = p
            return 0
        return 1

    @abstractmethod
    def Register(self, Name, Guid, Id=None):
        if self.Select(Name, Guid) == 0:
            return 1
        pNew = SConfigItem(Name, Guid, Id)
        if pNew is None:
            return 2
        if self.ItemListHead is None:
            self.ItemListHead = pNew
            self.ItemListTail = pNew
        else:
            self.ItemListTail.Next = pNew
            self.ItemListTail = pNew
        self.ItemListPos = pNew
        return 0

    @abstractmethod
    def Write(self, Mode, Name, Guid, Id, Type, Offset, Width, Value):
        Ret = self.Select(Name, Guid)
        if Ret != 0:
            return Ret

        if Mode == "a":
            if self.Select(Name, Guid, Id) != 0:
                pItem = SConfigItem(Name, Guid, Id, Type, Offset, Width, Value)
                if pItem is None:
                    return 2

                if self.ItemListHead is None:
                    self.ItemListHead = pItem
                    self.ItemListTail = pItem
                else:
                    self.ItemListTail.Next = pItem
                    self.ItemListTail = pItem

                self.ItemListPos = pItem

            else:
                # tranverse the list to find out if there's already the value for the same Offset
                pInfo = self.ItemListPos.InfoStrList
                while pInfo is not None:
                    if pInfo.Offset == Offset:
                        return 0
                    pInfo = pInfo.Next

                pInfo = SConfigInfo(Type, Offset, Width, Value)
                if pInfo is None:
                    return 2

                pInfo.Next = self.ItemListPos.InfoStrList
                self.ItemListPos.InfoStrList = pInfo

        elif Mode == "d":
            if self.ItemListHead == self.ItemListPos:
                self.ItemListHead = self.ItemListPos.Next

            pItem = self.ItemListHead
            while pItem.Next != self.ItemListPos:
                pItem = pItem.Next
            pItem.Next = self.ItemListPos.Next

            if self.ItemListTail == self.ItemListPos:
                self.ItemListTail = pItem

            self.ItemListPos = pItem.Next

        elif Mode == "i":
            if Id is not None:
                self.ItemListPos.Id = Id
        else:
            return 1
        return 0


gVfrBufferConfig = VfrBufferConfig()


class EFI_VARSTORE_INFO(Structure):
    _pack_ = 1
    _fields_ = [
        ("VarStoreId", c_uint16),
        ("Info", VarStoreInfoNode),
        ("VarType", c_uint8),
        ("VarTotalSize", c_uint32),
        ("IsBitVar", c_bool),
    ]

    def __init__(
        self,
        VarStoreId=EFI_VARSTORE_ID_INVALID,
        VarName=EFI_STRING_ID_INVALID,
        VarOffset=EFI_VAROFFSET_INVALID,
        VarType=EFI_IFR_TYPE_OTHER,
        VarTotalSize=0,
        IsBitVar=False,
    ):
        self.VarStoreId = VarStoreId
        self.Info.VarName = VarName
        self.Info.VarOffset = VarOffset
        self.VarTotalSize = VarTotalSize
        self.IsBitVar = IsBitVar
        self.VarType = VarType


class BufferVarStoreFieldInfoNode:
    def __init__(self, BaseInfo: EFI_VARSTORE_INFO):
        self.VarStoreInfo = EFI_VARSTORE_INFO()
        self.VarStoreInfo.VarType = BaseInfo.VarType
        self.VarStoreInfo.VarTotalSize = BaseInfo.VarTotalSize
        self.VarStoreInfo.Info.VarOffset = BaseInfo.Info.VarOffset
        self.VarStoreInfo.VarStoreId = BaseInfo.VarStoreId
        self.Next = None


class VfrDataStorage:
    def __init__(self):
        # SVfrVarStorageNode
        self.BufferVarStoreList = None
        self.EfiVarStoreList = None
        self.NameVarStoreList = None
        self.CurrVarStorageNode = None
        self.NewVarStorageNode = None
        self.BufferFieldInfoListHead = None
        self.mBufferFieldInfoListTail = None
        self.FreeVarStoreIdBitMap = []
        for i in range(0, EFI_FREE_VARSTORE_ID_BITMAP_SIZE):
            self.FreeVarStoreIdBitMap.append(0)
        # Question ID0 is reserved
        self.FreeVarStoreIdBitMap[0] = 0x80000000

    def Clear(self):
        #  SVfrVarStorageNode
        self.BufferVarStoreList = None
        self.EfiVarStoreList = None
        self.NameVarStoreList = None
        self.CurrVarStorageNode = None
        self.NewVarStorageNode = None
        self.BufferFieldInfoListHead = None
        self.mBufferFieldInfoListTail = None
        self.FreeVarStoreIdBitMap = []
        for _ in range(0, EFI_FREE_VARSTORE_ID_BITMAP_SIZE):
            self.FreeVarStoreIdBitMap.append(0)
        #  Question ID0 is reserved
        self.FreeVarStoreIdBitMap[0] = 0x80000000

    def GetBufferVarStoreList(self):
        return self.BufferVarStoreList

    def CheckGuidField(self, pNode, StoreGuid, HasFoundOne, ReturnCode):
        if StoreGuid is not None:
            #  If has guid info, compare the guid field.
            if pNode.Guid.__cmp__(StoreGuid):
                self.CurrVarStorageNode = pNode
                ReturnCode = VfrReturnCode.VFR_RETURN_SUCCESS
                return True, ReturnCode, HasFoundOne
        else:
            #  not has Guid field, check whether this name is the only one.
            if HasFoundOne:
                #  The name has conflict, return name redefined.
                ReturnCode = VfrReturnCode.VFR_RETURN_VARSTORE_NAME_REDEFINED_ERROR
                return True, ReturnCode, HasFoundOne

            self.CurrVarStorageNode = pNode
            HasFoundOne = True
        return False, ReturnCode, HasFoundOne

    def GetVarStoreByDataType(self, DataTypeName, VarGuid):
        MatchNode = None
        pNode = self.BufferVarStoreList
        while pNode is not None:
            if pNode.DataType.TypeName != DataTypeName:
                pNode = pNode.Next
                continue
            if VarGuid is not None:
                if pNode.Guid.__cmp__(VarGuid):
                    return pNode, VfrReturnCode.VFR_RETURN_SUCCESS
            elif MatchNode is None:
                MatchNode = pNode
            else:
                # More than one varstores referred the same data structures
                return None, VfrReturnCode.VFR_RETURN_VARSTORE_DATATYPE_REDEFINED_ERROR
            pNode = pNode.Next

        if MatchNode is None:
            return MatchNode, VfrReturnCode.VFR_RETURN_UNDEFINED

        return MatchNode, VfrReturnCode.VFR_RETURN_SUCCESS

    """
       Base on the input store name and guid to find the varstore id.
       If both name and guid are inputed, base on the name and guid to
       found the varstore. If only name inputed, base on the name to
       found the varstore and go on to check whether more than one varstore
       has the same name. If only has found one varstore, return this
       varstore; if more than one varstore has same name, return varstore
       name redefined error. If no varstore found by varstore name, call
       function GetVarStoreByDataType and use inputed varstore name as
       data type name to search.
       """

    def GetVarStoreId(self, StoreName, StoreGuid=None):
        ReturnCode = None
        HasFoundOne = False
        self.CurrVarStorageNode = None

        pNode = self.BufferVarStoreList
        while pNode is not None:
            if pNode.VarStoreName == StoreName:
                Result, ReturnCode, HasFoundOne = self.CheckGuidField(pNode, StoreGuid, HasFoundOne, ReturnCode)
                if Result:
                    VarStoreId = self.CurrVarStorageNode.VarStoreId
                    return VarStoreId, ReturnCode
            pNode = pNode.Next

        pNode = self.EfiVarStoreList
        while pNode is not None:
            if pNode.VarStoreName == StoreName:
                Result, ReturnCode, HasFoundOne = self.CheckGuidField(pNode, StoreGuid, HasFoundOne, ReturnCode)
                if Result:
                    VarStoreId = self.CurrVarStorageNode.VarStoreId
                    return VarStoreId, ReturnCode
            pNode = pNode.Next

        pNode = self.NameVarStoreList
        while pNode is not None:
            if pNode.VarStoreName == StoreName:
                Result, ReturnCode, HasFoundOne = self.CheckGuidField(pNode, StoreGuid, HasFoundOne, ReturnCode)
                if Result:
                    VarStoreId = self.CurrVarStorageNode.VarStoreId
                    return VarStoreId, ReturnCode
            pNode = pNode.Next

        if HasFoundOne:
            VarStoreId = self.CurrVarStorageNode.VarStoreId
            return VarStoreId, VfrReturnCode.VFR_RETURN_SUCCESS

        VarStoreId = EFI_VARSTORE_ID_INVALID
        pNode, ReturnCode = self.GetVarStoreByDataType(StoreName, StoreGuid)
        if pNode is not None:
            self.CurrVarStorageNode = pNode
            VarStoreId = pNode.VarStoreId

        return VarStoreId, ReturnCode

    def GetFreeVarStoreId(self, VarType):
        Index = 0
        for i in range(0, EFI_FREE_VARSTORE_ID_BITMAP_SIZE):
            if self.FreeVarStoreIdBitMap[i] != 0xFFFFFFFF:
                Index = i
                break
        if Index == EFI_FREE_VARSTORE_ID_BITMAP_SIZE:
            return EFI_VARSTORE_ID_INVALID

        Offset = 0
        Mask = 0x80000000
        while Mask != 0:
            if (self.FreeVarStoreIdBitMap[Index] & Mask) == 0:
                self.FreeVarStoreIdBitMap[Index] |= Mask
                return (Index << EFI_BITS_SHIFT_PER_UINT32) + Offset
            Mask >>= 1
            Offset += 1
        return EFI_VARSTORE_ID_INVALID

    def CheckVarStoreIdFree(self, VarStoreId):
        Index = int(VarStoreId / EFI_BITS_PER_UINT32)
        Offset = VarStoreId % EFI_BITS_PER_UINT32
        return (self.FreeVarStoreIdBitMap[Index] & (0x80000000 >> Offset)) == 0

    def MarkVarStoreIdUsed(self, VarStoreId):
        Index = int(VarStoreId / EFI_BITS_PER_UINT32)
        Offset = VarStoreId % EFI_BITS_PER_UINT32
        self.FreeVarStoreIdBitMap[Index] |= 0x80000000 >> Offset

    def DeclareBufferVarStore(self, StoreName, Guid, DataTypeDB, TypeName, VarStoreId, IsBitVarStore, Attr=0, Flag=True):
        if StoreName is None or Guid is None or DataTypeDB is None:
            return VfrReturnCode.VFR_RETURN_FATAL_ERROR
        _, ReturnCode = self.GetVarStoreId(StoreName, Guid)

        if ReturnCode == VfrReturnCode.VFR_RETURN_SUCCESS:
            return VfrReturnCode.VFR_RETURN_REDEFINED

        DataType, ReturnCode = DataTypeDB.GetDataType(TypeName)

        if ReturnCode != VfrReturnCode.VFR_RETURN_SUCCESS:
            return ReturnCode

        if VarStoreId == EFI_VARSTORE_ID_INVALID:
            VarStoreId = self.GetFreeVarStoreId(EFI_VFR_VARSTORE_TYPE.EFI_VFR_VARSTORE_BUFFER)
        else:
            if self.CheckVarStoreIdFree(VarStoreId) is False:
                return VfrReturnCode.VFR_RETURN_VARSTOREID_REDEFINED
            self.MarkVarStoreIdUsed(VarStoreId)
        pNew = SVfrVarStorageNode(StoreName, VarStoreId, Guid, Attr, Flag, None, DataType, IsBitVarStore)

        if pNew is None:
            return VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        pNew.Next = self.BufferVarStoreList
        self.BufferVarStoreList = pNew

        if gVfrBufferConfig.Register(StoreName, Guid) != 0:
            return VfrReturnCode.VFR_RETURN_FATAL_ERROR

        return VfrReturnCode.VFR_RETURN_SUCCESS

    def DeclareNameVarStoreBegin(self, StoreName, VarStoreId):
        if StoreName is None:
            return VfrReturnCode.VFR_RETURN_FATAL_ERROR

        _, ReturnCode = self.GetVarStoreId(StoreName)
        if ReturnCode == VfrReturnCode.VFR_RETURN_SUCCESS:
            return VfrReturnCode.VFR_RETURN_REDEFINED

        if VarStoreId == EFI_VARSTORE_ID_INVALID:
            VarStoreId = self.GetFreeVarStoreId(EFI_VFR_VARSTORE_TYPE.EFI_VFR_VARSTORE_NAME)
        else:
            if self.CheckVarStoreIdFree(VarStoreId) is False:
                return VfrReturnCode.VFR_RETURN_VARSTOREID_REDEFINED
            self.MarkVarStoreIdUsed(VarStoreId)

        pNode = SVfrVarStorageNode(StoreName, VarStoreId)

        if pNode is None:
            return VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        self.NewVarStorageNode = pNode
        return VfrReturnCode.VFR_RETURN_SUCCESS

    def DeclareNameVarStoreEnd(self, Guid):
        self.NewVarStorageNode.Guid = Guid
        self.NewVarStorageNode.Next = self.NameVarStoreList
        self.NameVarStoreList = self.NewVarStorageNode
        self.NewVarStorageNode = None

    def NameTableAddItem(self, Item):
        self.NewVarStorageNode.NameSpace.append(Item)
        return VfrReturnCode.VFR_RETURN_SUCCESS

    def GetNameVarStoreInfo(self, BaseInfo, Index):
        if BaseInfo is None:
            return VfrReturnCode.VFR_RETURN_FATAL_ERROR

        if self.CurrVarStorageNode is None:
            return VfrReturnCode.VFR_RETURN_GET_NVVARSTORE_ERROR

        BaseInfo.Info.VarName = self.CurrVarStorageNode.NameSpace[Index]

        return VfrReturnCode.VFR_RETURN_SUCCESS

    def GetVarStoreType(self, VarStoreId):
        VarStoreType = EFI_VFR_VARSTORE_TYPE.EFI_VFR_VARSTORE_INVALID

        if VarStoreId == EFI_VARSTORE_ID_INVALID:
            return VarStoreType

        pNode = self.BufferVarStoreList
        while pNode is not None:
            if pNode.VarStoreId == VarStoreId:
                return pNode.VarstoreType
            pNode = pNode.Next

        pNode = self.EfiVarStoreList
        while pNode is not None:
            if pNode.VarStoreId == VarStoreId:
                return pNode.VarstoreType
            pNode = pNode.Next

        pNode = self.NameVarStoreList
        while pNode is not None:
            if pNode.VarStoreId == VarStoreId:
                return pNode.VarstoreType
            pNode = pNode.Next

        return VarStoreType

    def GetVarStoreName(self, VarStoreId):
        pNode = self.BufferVarStoreList
        while pNode is not None:
            if pNode.VarStoreId == VarStoreId:
                return pNode.VarStoreName, VfrReturnCode.VFR_RETURN_SUCCESS
            pNode = pNode.Next

        pNode = self.EfiVarStoreList
        while pNode is not None:
            if pNode.VarStoreId == VarStoreId:
                return pNode.VarStoreName, VfrReturnCode.VFR_RETURN_SUCCESS
            pNode = pNode.Next

        pNode = self.NameVarStoreList
        while pNode is not None:
            if pNode.VarStoreId == VarStoreId:
                return pNode.VarStoreName, VfrReturnCode.VFR_RETURN_SUCCESS
            pNode = pNode.Next

        return None, VfrReturnCode.VFR_RETURN_UNDEFINED

    def GetBufferVarStoreDataTypeName(self, VarStoreId):
        DataTypeName = None
        if VarStoreId == EFI_VARSTORE_ID_INVALID:
            return DataTypeName, VfrReturnCode.VFR_RETURN_FATAL_ERROR

        pNode = self.BufferVarStoreList
        while pNode is not None:
            if pNode.VarStoreId == VarStoreId:
                DataTypeName = pNode.DataType.TypeName
                return DataTypeName, VfrReturnCode.VFR_RETURN_SUCCESS
            pNode = pNode.Next

        return DataTypeName, VfrReturnCode.VFR_RETURN_UNDEFINED

    def GetEfiVarStoreInfo(self, BaseInfo: EFI_VARSTORE_INFO):
        if BaseInfo is None:
            return VfrReturnCode.VFR_RETURN_FATAL_ERROR

        if self.CurrVarStorageNode is None:
            return VfrReturnCode.VFR_RETURN_GET_EFIVARSTORE_ERROR

        BaseInfo.Info.VarName = self.CurrVarStorageNode.EfiVar.EfiVarName
        BaseInfo.VarTotalSize = self.CurrVarStorageNode.EfiVar.EfiVarSize

        if BaseInfo.VarTotalSize == EFI_IFR_TYPE_NUM_8_BIT_SIZE:
            BaseInfo.VarType = EFI_IFR_TYPE_NUM_SIZE_8
        elif BaseInfo.VarTotalSize == EFI_IFR_TYPE_NUM_16_BIT_SIZE:
            BaseInfo.VarType = EFI_IFR_TYPE_NUM_SIZE_16
        elif BaseInfo.VarTotalSize == EFI_IFR_TYPE_NUM_32_BIT_SIZE:
            BaseInfo.VarType = EFI_IFR_TYPE_NUM_SIZE_32
        elif BaseInfo.VarTotalSize == EFI_IFR_TYPE_NUM_64_BIT_SIZE:
            BaseInfo.VarType = EFI_IFR_TYPE_NUM_SIZE_64
        else:
            return VfrReturnCode.VFR_RETURN_FATAL_ERROR

        return VfrReturnCode.VFR_RETURN_SUCCESS

    def GetVarStoreGuid(self, VarStoreId):
        VarGuid = None
        if VarStoreId == EFI_VARSTORE_ID_INVALID:
            return VarGuid

        pNode = self.BufferVarStoreList
        while pNode is not None:
            if pNode.VarStoreId == VarStoreId:
                VarGuid = pNode.Guid
                return VarGuid
            pNode = pNode.Next

        pNode = self.EfiVarStoreList
        while pNode is not None:
            if pNode.VarStoreId == VarStoreId:
                VarGuid = pNode.Guid
                return VarGuid
            pNode = pNode.Next

        pNode = self.NameVarStoreList
        while pNode is not None:
            if pNode.VarStoreId == VarStoreId:
                VarGuid = pNode.Guid
                return VarGuid
            pNode = pNode.Next

        return VarGuid

    def AddBufferVarStoreFieldInfo(self, BaseInfo: EFI_VARSTORE_INFO):
        pNew = BufferVarStoreFieldInfoNode(BaseInfo)
        if pNew is None:
            return VfrReturnCode.VFR_RETURN_FATAL_ERROR

        if self.BufferFieldInfoListHead is None:
            self.BufferFieldInfoListHead = pNew
            self.mBufferFieldInfoListTail = pNew
        else:
            self.mBufferFieldInfoListTail.Next = pNew
            self.mBufferFieldInfoListTail = pNew

        return VfrReturnCode.VFR_RETURN_SUCCESS


class VfrStringDB:
    def __init__(self):
        self.StringFileName = None

    def SetStringFileName(self, StringFileName):
        self.StringFileName = StringFileName

    def GetBestLanguage(self, SupportedLanguages, Language):
        if SupportedLanguages is None or Language is None:
            return False

        LanguageLength = 0
        # Determine the length of the first RFC 4646 language code in Language
        while LanguageLength < len(Language) and Language[LanguageLength] != 0 and Language[LanguageLength] != ";":
            LanguageLength += 1

        Supported = SupportedLanguages
        # Trim back the length of Language used until it is empty
        while LanguageLength > 0:
            # Loop through all language codes in SupportedLanguages
            while len(Supported) > 0:
                # Skip ';' characters in Supported
                while len(Supported) > 0 and Supported[0] == ";":
                    Supported = Supported[1:]

                CompareLength = 0
                # Determine the length of the next language code in Supported
                while CompareLength < len(Supported) and Supported[CompareLength] != 0 and Supported[CompareLength] != ";":
                    CompareLength += 1

                # If Language is longer than the Supported, then skip to the next language
                if LanguageLength > CompareLength:
                    continue

                # See if the first LanguageLength characters in Supported match Language
                if Supported[:LanguageLength] == Language:
                    return True

                Supported = Supported[CompareLength:]

            # Trim Language from the right to the next '-' character
            LanguageLength -= 1
            while LanguageLength > 0 and Language[LanguageLength] != "-":
                LanguageLength -= 1

        # No matches were found
        return False

    def GetUnicodeStringTextSize(self, StringSrc):
        StringSize = sizeof(c_ushort)
        StringStr = cast(StringSrc, POINTER(c_ushort))

        while StringStr.contents.value != "\0":
            StringSize += sizeof(c_ushort)
            StringStr = cast(addressof(StringStr.contents) + sizeof(c_ushort), POINTER(c_ushort))

        return StringSize

    def FindStringBlock(self, string_data, string_id):
        current_string_id = 1
        block_hdr = string_data
        block_size = 0
        offset = 0

        while block_hdr[0] != EFI_HII_SIBT_END:
            block_type = block_hdr[0]

            if block_type == EFI_HII_SIBT_STRING_SCSU:
                offset = sizeof(EFI_HII_STRING_BLOCK)
                string_text_ptr = block_hdr + offset
                block_size += offset + len(str(string_text_ptr)) + 1
                current_string_id += 1

            elif block_type == EFI_HII_SIBT_STRING_SCSU_FONT:
                offset = sizeof(EFI_HII_SIBT_STRING_SCSU_FONT_BLOCK) - sizeof(c_uint8)
                string_text_ptr = block_hdr + offset
                block_size += offset + len(str(string_text_ptr)) + 1
                current_string_id += 1

            elif block_type == EFI_HII_SIBT_STRINGS_SCSU:
                string_count = int.from_bytes(
                    block_hdr[sizeof(EFI_HII_STRING_BLOCK) : sizeof(EFI_HII_STRING_BLOCK) + sizeof(c_uint16)],
                    byteorder="little",
                )
                string_text_ptr = block_hdr + sizeof(EFI_HII_SIBT_STRINGS_SCSU_BLOCK) - sizeof(c_uint8)
                block_size += string_text_ptr - block_hdr

                for _ in range(string_count):
                    block_size += len(str(string_text_ptr)) + 1

                    if current_string_id == string_id:
                        block_type = block_hdr[0]
                        string_text_offset = string_text_ptr - string_data
                        return EFI_SUCCESS

                    string_text_ptr = string_text_ptr + len(str(string_text_ptr)) + 1
                    current_string_id += 1

            elif block_type == EFI_HII_SIBT_STRINGS_SCSU_FONT:
                string_count = int.from_bytes(
                    block_hdr[sizeof(EFI_HII_STRING_BLOCK) + sizeof(c_uint8) : sizeof(EFI_HII_STRING_BLOCK) + sizeof(c_uint8) + sizeof(c_uint16)],
                    byteorder="little",
                )
                string_text_ptr = block_hdr + sizeof(EFI_HII_SIBT_STRINGS_SCSU_FONT_BLOCK) - sizeof(c_uint8)
                block_size += string_text_ptr - block_hdr

                for _ in range(string_count):
                    block_size += len(str(string_text_ptr)) + 1

                    if current_string_id == string_id:
                        block_type = block_hdr[0]
                        string_text_offset = string_text_ptr - string_data
                        return EFI_SUCCESS

                    string_text_ptr = string_text_ptr + len(str(string_text_ptr)) + 1
                    current_string_id += 1

            elif block_type == EFI_HII_SIBT_STRING_UCS2:
                offset = sizeof(EFI_HII_STRING_BLOCK)
                string_text_ptr = block_hdr + offset
                string_size = self.GetUnicodeStringTextSize(string_text_ptr)
                block_size += offset + string_size
                current_string_id += 1

            elif block_type == EFI_HII_SIBT_STRING_UCS2_FONT:
                offset = sizeof(EFI_HII_SIBT_STRING_UCS2_FONT_BLOCK) - sizeof(c_ushort)
                string_text_ptr = block_hdr + offset
                string_size = self.GetUnicodeStringTextSize(string_text_ptr)
                block_size += offset + string_size
                current_string_id += 1

            elif block_type == EFI_HII_SIBT_STRINGS_UCS2:
                offset = len(EFI_HII_SIBT_STRINGS_UCS2_BLOCK) - len(c_ushort)
                string_text_ptr = block_hdr + offset
                block_size += offset
                string_count = int.from_bytes(
                    block_hdr[sizeof(EFI_HII_STRING_BLOCK) : sizeof(EFI_HII_STRING_BLOCK) + sizeof(c_uint16)],
                    byteorder="little",
                )

                for _ in range(string_count):
                    string_size = self.GetUnicodeStringTextSize(string_text_ptr)
                    block_size += string_size

                    if current_string_id == string_id:
                        block_type = block_hdr[0]
                        string_text_offset = string_text_ptr - string_data
                        return EFI_SUCCESS

                    string_text_ptr = string_text_ptr + string_size
                    current_string_id += 1

            elif block_type == EFI_HII_SIBT_STRINGS_UCS2_FONT:
                offset = len(EFI_HII_SIBT_STRINGS_UCS2_FONT_BLOCK) - len(c_ushort)
                string_text_ptr = block_hdr + offset
                block_size += offset
                string_count = int.from_bytes(
                    block_hdr[sizeof(EFI_HII_STRING_BLOCK) + sizeof(c_uint8) : sizeof(EFI_HII_STRING_BLOCK) + sizeof(c_uint8) + sizeof(c_uint16)],
                    byteorder="little",
                )

                for _ in range(string_count):
                    string_size = self.GetUnicodeStringTextSize(string_text_ptr)
                    block_size += string_size

                    if current_string_id == string_id:
                        block_type = block_hdr[0]
                        string_text_offset = string_text_ptr - string_data
                        return EFI_SUCCESS

                    string_text_ptr = string_text_ptr + string_size
                    current_string_id += 1

            elif block_type == EFI_HII_SIBT_DUPLICATE:
                if current_string_id == string_id:
                    string_id = int.from_bytes(
                        block_hdr[sizeof(EFI_HII_STRING_BLOCK) : sizeof(EFI_HII_STRING_BLOCK) + sizeof(c_uint16)],
                        byteorder="little",
                    )
                    current_string_id = 1
                    block_size = 0
                else:
                    block_size += sizeof(EFI_HII_SIBT_DUPLICATE_BLOCK)
                    current_string_id += 1

            elif block_type == EFI_HII_SIBT_SKIP1:
                skip_count = int.from_bytes(block_hdr[sizeof(EFI_HII_STRING_BLOCK)], byteorder="little")
                current_string_id += skip_count
                block_size += sizeof(EFI_HII_SIBT_SKIP1_BLOCK)

            elif block_type == EFI_HII_SIBT_SKIP2:
                skip_count = int.from_bytes(
                    block_hdr[sizeof(EFI_HII_STRING_BLOCK) : sizeof(EFI_HII_STRING_BLOCK) + sizeof(c_uint16)],
                    byteorder="little",
                )
                current_string_id += skip_count
                block_size += sizeof(EFI_HII_SIBT_SKIP2_BLOCK)

            elif block_type == EFI_HII_SIBT_EXT1:
                length8 = int.from_bytes(
                    block_hdr[sizeof(EFI_HII_STRING_BLOCK) + sizeof(c_uint8) : sizeof(EFI_HII_STRING_BLOCK) + sizeof(c_uint8) + sizeof(c_uint8)],
                    byteorder="little",
                )
                block_size += length8

            elif block_type == EFI_HII_SIBT_EXT2:
                length32 = int.from_bytes(
                    block_hdr[sizeof(EFI_HII_STRING_BLOCK) + sizeof(c_uint8) : sizeof(EFI_HII_STRING_BLOCK) + sizeof(c_uint8) + sizeof(c_uint32)],
                    byteorder="little",
                )
                block_size += length32

            if string_id > 0 and string_id != (c_uint16)(-1):
                block_type = block_hdr[0]

                if string_id == current_string_id - 1:
                    if block_type in (EFI_HII_SIBT_SKIP2, EFI_HII_SIBT_SKIP1):
                        return EFI_NOT_FOUND
                    return EFI_SUCCESS

                if string_id < current_string_id - 1:
                    return EFI_NOT_FOUND

            block_hdr = string_data + block_size

        return EFI_NOT_FOUND

    def GetVarStoreNameFormStringId(self, StringId):
        pInFile = None
        NameOffset = 0
        Length = 0
        StringPtr = None
        StringName = None
        UnicodeString = None
        VarStoreName = None
        DestTmp = None
        Current = None
        Status = None
        BlockType = 0
        PkgHeader = None

        if self.StringFileName is None:
            return None

        try:
            with open(LongFilePath(self.StringFileName), "rb") as pInFile:
                # Get file length
                pInFile.seek(0, os.SEEK_END)
                Length = pInFile.tell()
                pInFile.seek(0, os.SEEK_SET)

                # Get file data
                StringPtr = bytearray(pInFile.read())
        except Exception:
            return None

        PkgHeader = EFI_HII_STRING_PACKAGE_HDR.from_buffer(StringPtr)

        # Check the String package
        if PkgHeader.Header.Type != EFI_HII_PACKAGE_STRINGS:
            return None

        # Search the language, get best language based on RFC 4647 matching algorithm
        Current = StringPtr
        while not self.GetBestLanguage("en", PkgHeader.Language):
            Current += PkgHeader.Header.Length
            PkgHeader = EFI_HII_STRING_PACKAGE_HDR.from_buffer(Current)

            # If can't find string package based on language, just return the first string package
            if Current - StringPtr >= Length:
                Current = StringPtr
                PkgHeader = EFI_HII_STRING_PACKAGE_HDR.from_buffer(StringPtr)
                break

        Current += PkgHeader.HdrSize

        # Find the string block according to the stringId
        Status, NameOffset, BlockType = self.FindStringBlock(Current, StringId)
        if Status != RETURN_SUCCESS:
            return None

        # Get varstore name according to the string type
        if BlockType in [
            EFI_HII_SIBT_STRING_SCSU,
            EFI_HII_SIBT_STRING_SCSU_FONT,
            EFI_HII_SIBT_STRINGS_SCSU,
            EFI_HII_SIBT_STRINGS_SCSU_FONT,
        ]:
            StringName = Current + NameOffset
            VarStoreName = StringName.decode("utf-8")
        elif BlockType in [
            EFI_HII_SIBT_STRING_UCS2,
            EFI_HII_SIBT_STRING_UCS2_FONT,
            EFI_HII_SIBT_STRINGS_UCS2,
            EFI_HII_SIBT_STRINGS_UCS2_FONT,
        ]:
            UnicodeString = Current + NameOffset
            Length = self.GetUnicodeStringTextSize(UnicodeString)
            DestTmp = bytearray(Length // 2 + 1)
            VarStoreName = DestTmp
            index = 0
            while UnicodeString[index] != "\0":
                DestTmp[index] = ord(UnicodeString[index])
                index += 1
            DestTmp[index] = "\0"
        else:
            return None

        return VarStoreName


gVfrStringDB = VfrStringDB()

EFI_RULE_ID_START = 0x01
EFI_RULE_ID_INVALID = 0x00


class SVfrRuleNode:
    def __init__(self, RuleName=None, RuleId=0):
        self.RuleId = RuleId
        self.RuleName = RuleName
        self.Next = None


class VfrRulesDB:
    def __init__(self):
        self.RuleList = None
        self.FreeRuleId = EFI_VARSTORE_ID_START

    def RegisterRule(self, RuleName):
        if RuleName is None:
            return

        pNew = SVfrRuleNode(RuleName, self.FreeRuleId)
        if pNew is None:
            return
        self.FreeRuleId += 1
        pNew.Next = self.RuleList
        self.RuleList = pNew

    def GetRuleId(self, RuleName):
        if RuleName is None:
            return EFI_RULE_ID_INVALID

        pNode = self.RuleList
        while pNode is not None:
            if pNode.RuleName == RuleName:
                return pNode.RuleId
            pNode = pNode.Next

        return EFI_RULE_ID_INVALID


EFI_QUESTION_ID_MAX = 0xFFFF
EFI_FREE_QUESTION_ID_BITMAP_SIZE = int((EFI_QUESTION_ID_MAX + 1) / EFI_BITS_PER_UINT32)
EFI_QUESTION_ID_INVALID = 0x0


class EFI_QUESION_TYPE(Enum):
    QUESTION_NORMAL = 0
    QUESTION_DATE = 1
    QUESTION_TIME = 2
    QUESTION_REF = 3


class SVfrQuestionNode:
    def __init__(self, Name=None, VarIdStr=None, BitMask=0):  #
        self.Name = Name
        self.VarIdStr = VarIdStr
        self.QuestionId = EFI_QUESTION_ID_INVALID
        self.BitMask = BitMask
        self.Next = None
        self.QType = EFI_QUESION_TYPE.QUESTION_NORMAL


DATE_YEAR_BITMASK = 0x0000FFFF
DATE_MONTH_BITMASK = 0x00FF0000
DATE_DAY_BITMASK = 0xFF000000
TIME_HOUR_BITMASK = 0x000000FF
TIME_MINUTE_BITMASK = 0x0000FF00
TIME_SECOND_BITMASK = 0x00FF0000


class VfrQuestionDB:
    def __init__(self):
        self.FreeQIdBitMap = []
        for i in range(0, EFI_FREE_QUESTION_ID_BITMAP_SIZE):
            self.FreeQIdBitMap.append(0)

        # Question ID 0 is reserved.
        self.FreeQIdBitMap[0] = 0x80000000

        self.QuestionList = None

    def FindQuestionByName(self, Name):
        if Name is None:
            return VfrReturnCode.VFR_RETURN_FATAL_ERROR

        pNode = self.QuestionList
        while pNode is not None:
            if pNode.Name == Name:
                return VfrReturnCode.VFR_RETURN_SUCCESS
            pNode = pNode.Next

        return VfrReturnCode.VFR_RETURN_UNDEFINED

    def FindQuestionById(self, QuestionId):
        if QuestionId == EFI_QUESTION_ID_INVALID:
            return VfrReturnCode.VFR_RETURN_INVALID_PARAMETER

        pNode = self.QuestionList
        while pNode is not None:
            if pNode.QuestionId == QuestionId:
                return VfrReturnCode.VFR_RETURN_SUCCESS
            pNode = pNode.Next

        return VfrReturnCode.VFR_RETURN_UNDEFINED

    def GetFreeQuestionId(self):
        Index = 0
        for i in range(0, EFI_FREE_QUESTION_ID_BITMAP_SIZE):
            if self.FreeQIdBitMap[i] != 0xFFFFFFFF:
                Index = i
                break
        if Index == EFI_FREE_QUESTION_ID_BITMAP_SIZE:
            return EFI_QUESTION_ID_INVALID

        Offset = 0
        Mask = 0x80000000
        while Mask != 0:
            if (self.FreeQIdBitMap[Index] & Mask) == 0:
                self.FreeQIdBitMap[Index] |= Mask
                return (Index << EFI_BITS_SHIFT_PER_UINT32) + Offset
            Mask >>= 1
            Offset += 1

        return EFI_QUESTION_ID_INVALID

    def CheckQuestionIdFree(self, QId):
        Index = int(QId / EFI_BITS_PER_UINT32)
        Offset = QId % EFI_BITS_PER_UINT32
        return (self.FreeQIdBitMap[Index] & (0x80000000 >> Offset)) == 0

    def MarkQuestionIdUsed(self, QId):
        Index = int(QId / EFI_BITS_PER_UINT32)
        Offset = QId % EFI_BITS_PER_UINT32
        self.FreeQIdBitMap[Index] |= 0x80000000 >> Offset

    def MarkQuestionIdUnused(self, QId):
        Index = int(QId / EFI_BITS_PER_UINT32)
        Offset = QId % EFI_BITS_PER_UINT32
        self.FreeQIdBitMap[Index] &= ~(0x80000000 >> Offset)

    def RegisterQuestion(self, Name, VarIdStr, QuestionId, gFormPkg):
        if (Name is not None) and (self.FindQuestionByName(Name) == VfrReturnCode.VFR_RETURN_SUCCESS):
            return QuestionId, VfrReturnCode.VFR_RETURN_REDEFINED

        pNode = SVfrQuestionNode(Name, VarIdStr)
        if pNode is None:
            return QuestionId, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        if QuestionId == EFI_QUESTION_ID_INVALID:
            QuestionId = self.GetFreeQuestionId()
        else:
            if self.CheckQuestionIdFree(QuestionId) is False:
                return QuestionId, VfrReturnCode.VFR_RETURN_QUESTIONID_REDEFINED
            self.MarkQuestionIdUsed(QuestionId)

        pNode.QuestionId = QuestionId
        pNode.Next = self.QuestionList
        self.QuestionList = pNode

        gFormPkg.DoPendingAssign(VarIdStr, QuestionId)

        return QuestionId, VfrReturnCode.VFR_RETURN_SUCCESS

    def UpdateQuestionId(self, QId, NewQId, gFormPkg):
        if QId == NewQId:
            # don't update
            return VfrReturnCode.VFR_RETURN_SUCCESS

        if self.CheckQuestionIdFree(NewQId) is False:
            return VfrReturnCode.VFR_RETURN_REDEFINED

        pNode = self.QuestionList
        TempList = []
        while pNode is not None:
            if pNode.QuestionId == QId:
                TempList.append(pNode)
            pNode = pNode.Next

        if len(TempList) == 0:
            return VfrReturnCode.VFR_RETURN_UNDEFINED

        self.MarkQuestionIdUnused(QId)

        for pNode in TempList:
            pNode.QuestionId = NewQId
            gFormPkg.DoPendingAssign(pNode.VarIdStr, NewQId)

        self.MarkQuestionIdUsed(NewQId)

        return VfrReturnCode.VFR_RETURN_SUCCESS

    def GetQuestionId(self, Name, VarIdStr=None, QType=None):
        QuestionId = EFI_QUESTION_ID_INVALID
        BitMask = 0x00000000
        if QType is not None:
            QType = EFI_QUESION_TYPE.QUESTION_NORMAL

        if Name is None and VarIdStr is None:
            return QuestionId, BitMask, QType

        pNode = self.QuestionList
        while pNode is not None:
            if Name is not None:
                if pNode.Name != Name:
                    pNode = pNode.Next
                    continue

            if VarIdStr is not None:
                if pNode.VarIdStr != VarIdStr:
                    pNode = pNode.Next
                    continue

            QuestionId = pNode.QuestionId
            BitMask = pNode.BitMask
            if QType is not None:
                QType = pNode.QType
            break

        return QuestionId, BitMask, QType

    def RegisterNewDateQuestion(self, Name, BaseVarId, QuestionId, gFormPkg):
        if BaseVarId == "" and Name is None:
            if QuestionId == EFI_QUESTION_ID_INVALID:
                QuestionId = self.GetFreeQuestionId()
            else:
                if self.CheckQuestionIdFree(QuestionId) is False:
                    return QuestionId, VfrReturnCode.VFR_RETURN_REDEFINED
                self.MarkQuestionIdUsed(QuestionId)
            return QuestionId, VfrReturnCode.VFR_RETURN_SUCCESS

        VarIdStrList = []
        if BaseVarId != "":
            VarIdStrList.append(BaseVarId + ".Year")
            VarIdStrList.append(BaseVarId + ".Month")
            VarIdStrList.append(BaseVarId + ".Day")

        else:
            VarIdStrList.append(Name + ".Year")
            VarIdStrList.append(Name + ".Month")
            VarIdStrList.append(Name + ".Day")

        pNodeList = []
        pNode = SVfrQuestionNode(Name, VarIdStrList[0], DATE_YEAR_BITMASK)
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return QuestionId, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        pNode = SVfrQuestionNode(Name, VarIdStrList[1], DATE_MONTH_BITMASK)
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return QuestionId, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        pNode = SVfrQuestionNode(Name, VarIdStrList[2], DATE_DAY_BITMASK)
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return QuestionId, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        if QuestionId == EFI_QUESTION_ID_INVALID:
            QuestionId = self.GetFreeQuestionId()
        else:
            if self.CheckQuestionIdFree(QuestionId) is False:
                return QuestionId, VfrReturnCode.VFR_RETURN_REDEFINED
            self.MarkQuestionIdUsed(QuestionId)

        pNodeList[0].QuestionId = QuestionId
        pNodeList[1].QuestionId = QuestionId
        pNodeList[2].QuestionId = QuestionId
        pNodeList[0].QType = EFI_QUESION_TYPE.QUESTION_DATE
        pNodeList[1].QType = EFI_QUESION_TYPE.QUESTION_DATE
        pNodeList[2].QType = EFI_QUESION_TYPE.QUESTION_DATE
        pNodeList[0].Next = pNodeList[1]
        pNodeList[1].Next = pNodeList[2]
        pNodeList[2].Next = self.QuestionList
        self.QuestionList = pNodeList[0]

        gFormPkg.DoPendingAssign(VarIdStrList[0], QuestionId)
        gFormPkg.DoPendingAssign(VarIdStrList[1], QuestionId)
        gFormPkg.DoPendingAssign(VarIdStrList[2], QuestionId)

        return QuestionId, VfrReturnCode.VFR_RETURN_SUCCESS

    def RegisterNewTimeQuestion(self, Name, BaseVarId, QuestionId, gFormPkg):
        if BaseVarId == "" and Name is None:
            if QuestionId == EFI_QUESTION_ID_INVALID:
                QuestionId = self.GetFreeQuestionId()
            else:
                if self.CheckQuestionIdFree(QuestionId) is False:
                    return QuestionId, VfrReturnCode.VFR_RETURN_REDEFINED
                self.MarkQuestionIdUsed(QuestionId)
            return QuestionId, VfrReturnCode.VFR_RETURN_SUCCESS

        VarIdStrList = []
        if BaseVarId != "":
            VarIdStrList.append(BaseVarId + ".Hour")
            VarIdStrList.append(BaseVarId + ".Minute")
            VarIdStrList.append(BaseVarId + ".Second")

        else:
            VarIdStrList.append(Name + ".Hour")
            VarIdStrList.append(Name + ".Minute")
            VarIdStrList.append(Name + ".Second")

        pNodeList = []
        pNode = SVfrQuestionNode(Name, VarIdStrList[0], TIME_HOUR_BITMASK)
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return QuestionId, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        pNode = SVfrQuestionNode(Name, VarIdStrList[1], TIME_MINUTE_BITMASK)
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return QuestionId, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        pNode = SVfrQuestionNode(Name, VarIdStrList[2], TIME_SECOND_BITMASK)
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return QuestionId, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        if QuestionId == EFI_QUESTION_ID_INVALID:
            QuestionId = self.GetFreeQuestionId()
        else:
            if self.CheckQuestionIdFree(QuestionId) is False:
                return QuestionId, VfrReturnCode.VFR_RETURN_REDEFINED
            self.MarkQuestionIdUsed(QuestionId)

        pNodeList[0].QuestionId = QuestionId
        pNodeList[1].QuestionId = QuestionId
        pNodeList[2].QuestionId = QuestionId
        pNodeList[0].QType = EFI_QUESION_TYPE.QUESTION_TIME
        pNodeList[1].QType = EFI_QUESION_TYPE.QUESTION_TIME
        pNodeList[2].QType = EFI_QUESION_TYPE.QUESTION_TIME
        pNodeList[0].Next = pNodeList[1]
        pNodeList[1].Next = pNodeList[2]
        pNodeList[2].Next = self.QuestionList
        self.QuestionList = pNodeList[0]

        gFormPkg.DoPendingAssign(VarIdStrList[0], QuestionId)
        gFormPkg.DoPendingAssign(VarIdStrList[1], QuestionId)
        gFormPkg.DoPendingAssign(VarIdStrList[2], QuestionId)

        return QuestionId, VfrReturnCode.VFR_RETURN_SUCCESS

    def RegisterRefQuestion(self, Name, BaseVarId, QuestionId, gFormPkg):
        if BaseVarId == "" and Name is None:
            return QuestionId, VfrReturnCode.VFR_RETURN_FATAL_ERROR

        VarIdStrList = []
        if BaseVarId != "":
            VarIdStrList.append(BaseVarId + ".QuestionId")
            VarIdStrList.append(BaseVarId + ".FormId")
            VarIdStrList.append(BaseVarId + ".FormSetGuid")
            VarIdStrList.append(BaseVarId + ".DevicePath")

        else:
            VarIdStrList.append(BaseVarId + ".QuestionId")
            VarIdStrList.append(BaseVarId + ".FormId")
            VarIdStrList.append(BaseVarId + ".FormSetGuid")
            VarIdStrList.append(BaseVarId + ".DevicePath")

        pNodeList = []
        pNode = SVfrQuestionNode(Name, VarIdStrList[0])
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return QuestionId, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        pNode = SVfrQuestionNode(Name, VarIdStrList[1])
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return QuestionId, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        pNode = SVfrQuestionNode(Name, VarIdStrList[2])
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return QuestionId, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        pNode = SVfrQuestionNode(Name, VarIdStrList[3])
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return QuestionId, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        if QuestionId == EFI_QUESTION_ID_INVALID:
            QuestionId = self.GetFreeQuestionId()
        else:
            if self.CheckQuestionIdFree(QuestionId) is False:
                return QuestionId, VfrReturnCode.VFR_RETURN_REDEFINED
            self.MarkQuestionIdUsed(QuestionId)

        pNodeList[0].QuestionId = QuestionId
        pNodeList[1].QuestionId = QuestionId
        pNodeList[2].QuestionId = QuestionId
        pNodeList[3].QuestionId = QuestionId

        pNodeList[0].QType = EFI_QUESION_TYPE.QUESTION_REF
        pNodeList[1].QType = EFI_QUESION_TYPE.QUESTION_REF
        pNodeList[2].QType = EFI_QUESION_TYPE.QUESTION_REF
        pNodeList[3].QType = EFI_QUESION_TYPE.QUESTION_REF

        pNodeList[0].Next = pNodeList[1]
        pNodeList[1].Next = pNodeList[2]
        pNodeList[2].Next = pNodeList[3]
        pNodeList[3].Next = self.QuestionList
        self.QuestionList = pNodeList[0]

        gFormPkg.DoPendingAssign(VarIdStrList[0], QuestionId)
        gFormPkg.DoPendingAssign(VarIdStrList[1], QuestionId)
        gFormPkg.DoPendingAssign(VarIdStrList[2], QuestionId)
        gFormPkg.DoPendingAssign(VarIdStrList[3], QuestionId)

        return QuestionId, VfrReturnCode.VFR_RETURN_SUCCESS

    def RegisterOldDateQuestion(self, YearVarId, MonthVarId, DayVarId, QuestionId, gFormPkg):
        pNodeList = []
        if YearVarId == "" or MonthVarId == "" or DayVarId == "" or \
            YearVarId is None or MonthVarId is None or DayVarId is None:
            return QuestionId, VfrReturnCode.VFR_RETURN_ERROR_SKIPED

        pNode = SVfrQuestionNode(None, YearVarId, DATE_YEAR_BITMASK)
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return EFI_QUESTION_ID_INVALID, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        pNode = SVfrQuestionNode(None, MonthVarId, DATE_MONTH_BITMASK)
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return EFI_QUESTION_ID_INVALID, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        pNode = SVfrQuestionNode(None, DayVarId, DATE_DAY_BITMASK)
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return EFI_QUESTION_ID_INVALID, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        if QuestionId == EFI_QUESTION_ID_INVALID:
            QuestionId = self.GetFreeQuestionId()
        else:
            if self.CheckQuestionIdFree(QuestionId) is False:
                return EFI_QUESTION_ID_INVALID, VfrReturnCode.VFR_RETURN_REDEFINED
            self.MarkQuestionIdUsed(QuestionId)

        pNodeList[0].QuestionId = QuestionId
        pNodeList[1].QuestionId = QuestionId
        pNodeList[2].QuestionId = QuestionId
        pNodeList[0].QType = EFI_QUESION_TYPE.QUESTION_DATE
        pNodeList[1].QType = EFI_QUESION_TYPE.QUESTION_DATE
        pNodeList[2].QType = EFI_QUESION_TYPE.QUESTION_DATE
        pNodeList[0].Next = pNodeList[1]
        pNodeList[1].Next = pNodeList[2]
        pNodeList[2].Next = self.QuestionList
        self.QuestionList = pNodeList[0]

        gFormPkg.DoPendingAssign(YearVarId, QuestionId)
        gFormPkg.DoPendingAssign(MonthVarId, QuestionId)
        gFormPkg.DoPendingAssign(DayVarId, QuestionId)

        return QuestionId, VfrReturnCode.VFR_RETURN_SUCCESS

    def RegisterOldTimeQuestion(self, HourVarId, MinuteVarId, SecondVarId, QuestionId, gFormPkg):
        pNodeList = []
        if HourVarId == "" or MinuteVarId == "" or SecondVarId == "" \
            or HourVarId is None or MinuteVarId is None or SecondVarId is None:
            return QuestionId, VfrReturnCode.VFR_RETURN_ERROR_SKIPED

        pNode = SVfrQuestionNode(None, HourVarId, TIME_HOUR_BITMASK)
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return EFI_QUESTION_ID_INVALID, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        pNode = SVfrQuestionNode(None, MinuteVarId, TIME_MINUTE_BITMASK)
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return EFI_QUESTION_ID_INVALID, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        pNode = SVfrQuestionNode(None, SecondVarId, TIME_SECOND_BITMASK)
        if pNode is not None:
            pNodeList.append(pNode)
        else:
            return EFI_QUESTION_ID_INVALID, VfrReturnCode.VFR_RETURN_OUT_FOR_RESOURCES

        if QuestionId == EFI_QUESTION_ID_INVALID:
            QuestionId = self.GetFreeQuestionId()
        else:
            if self.CheckQuestionIdFree(QuestionId) is False:
                return EFI_QUESTION_ID_INVALID, VfrReturnCode.VFR_RETURN_REDEFINED
            self.MarkQuestionIdUsed(QuestionId)

        pNodeList[0].QuestionId = QuestionId
        pNodeList[1].QuestionId = QuestionId
        pNodeList[2].QuestionId = QuestionId
        pNodeList[0].QType = EFI_QUESION_TYPE.QUESTION_TIME
        pNodeList[1].QType = EFI_QUESION_TYPE.QUESTION_TIME
        pNodeList[2].QType = EFI_QUESION_TYPE.QUESTION_TIME
        pNodeList[0].Next = pNodeList[1]
        pNodeList[1].Next = pNodeList[2]
        pNodeList[2].Next = self.QuestionList
        self.QuestionList = pNodeList[0]

        gFormPkg.DoPendingAssign(HourVarId, QuestionId)
        gFormPkg.DoPendingAssign(MinuteVarId, QuestionId)
        gFormPkg.DoPendingAssign(SecondVarId, QuestionId)

        return QuestionId, VfrReturnCode.VFR_RETURN_SUCCESS

    def PrintAllQuestion(self, FileName):
        with open(FileName, "w") as f:
            pNode = self.QuestionList
            while pNode is not None:
                f.write("Question VarId is {} and QuestionId is ".format(pNode.VarIdStr))
                f.write("%d\n" % (pNode.QuestionId))
                pNode = pNode.Next

        f.close()
