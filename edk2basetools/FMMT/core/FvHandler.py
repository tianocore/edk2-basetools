## @file
# This file is used to the implementation of Bios layout handler.
#
# Copyright (c) 2021-, Intel Corporation. All rights reserved.<BR>
# SPDX-License-Identifier: BSD-2-Clause-Patent
##
import os
from edk2basetools.FMMT.core.BiosTree import *
from edk2basetools.FMMT.core.GuidTools import GUIDTools
from edk2basetools.FMMT.core.BiosTreeNode import *
from edk2basetools.FMMT.PI.Common import *

EFI_FVB2_ERASE_POLARITY = 0x00000800

def ChangeSize(TargetTree, size_delta: int=0) -> None:
    if type(TargetTree.Data.Header) == type(EFI_FFS_FILE_HEADER2()) or type(TargetTree.Data.Header) == type(EFI_COMMON_SECTION_HEADER2()):
        TargetTree.Data.Size -= size_delta
        TargetTree.Data.Header.ExtendedSize -= size_delta
    elif TargetTree.type == SECTION_TREE and TargetTree.Data.OriData:
        OriSize = TargetTree.Data.Header.SECTION_SIZE
        OriSize -= size_delta
        TargetTree.Data.Header.Size[0] = OriSize % (16**2)
        TargetTree.Data.Header.Size[1] = OriSize % (16**4) //(16**2)
        TargetTree.Data.Header.Size[2] = OriSize // (16**4)
    else:
        TargetTree.Data.Size -= size_delta
        TargetTree.Data.Header.Size[0] = TargetTree.Data.Size % (16**2)
        TargetTree.Data.Header.Size[1] = TargetTree.Data.Size % (16**4) //(16**2)
        TargetTree.Data.Header.Size[2] = TargetTree.Data.Size // (16**4)

def ModifyFfsType(TargetFfs) -> None:
    if type(TargetFfs.Data.Header) == type(EFI_FFS_FILE_HEADER()) and TargetFfs.Data.Size > 0xFFFFFF:
        ExtendSize = TargetFfs.Data.Header.FFS_FILE_SIZE + 8
        New_Header = EFI_FFS_FILE_HEADER2()
        New_Header.Name = TargetFfs.Data.Header.Name
        New_Header.IntegrityCheck = TargetFfs.Data.Header.IntegrityCheck
        New_Header.Type = TargetFfs.Data.Header.Type
        New_Header.Attributes = TargetFfs.Data.Header.Attributes
        New_Header.Size = 0
        New_Header.State = TargetFfs.Data.Header.State
        New_Header.ExtendedSize = ExtendSize
        TargetFfs.Data.Header = New_Header
        TargetFfs.Data.Size = TargetFfs.Data.Header.FFS_FILE_SIZE
        TargetFfs.Data.HeaderLength = TargetFfs.Data.Header.HeaderLength
        TargetFfs.Data.ModCheckSum()
    elif type(TargetFfs.Data.Header) == type(EFI_FFS_FILE_HEADER2()) and TargetFfs.Data.Size <= 0xFFFFFF:
        New_Header = EFI_FFS_FILE_HEADER()
        New_Header.Name = TargetFfs.Data.Header.Name
        New_Header.IntegrityCheck = TargetFfs.Data.Header.IntegrityCheck
        New_Header.Type = TargetFfs.Data.Header.Type
        New_Header.Attributes = TargetFfs.Data.Header.Attributes
        New_Header.Size = TargetFfs.Data.HeaderLength + TargetFfs.Data.Size
        New_Header.State = TargetFfs.Data.Header.State
        TargetFfs.Data.Header = New_Header
        TargetFfs.Data.Size = TargetFfs.Data.Header.FFS_FILE_SIZE
        TargetFfs.Data.HeaderLength = TargetFfs.Data.Header.HeaderLength
        TargetFfs.Data.ModCheckSum()
        if struct2stream(TargetFfs.Parent.Data.Header.FileSystemGuid) == EFI_FIRMWARE_FILE_SYSTEM3_GUID_BYTE:
            NeedChange = True
            for item in TargetFfs.Parent.Child:
                if type(item.Data.Header) == type(EFI_FFS_FILE_HEADER2()):
                    NeedChange = False
            if NeedChange:
                TargetFfs.Parent.Data.Header.FileSystemGuid = ModifyGuidFormat("8c8ce578-8a3d-4f1c-9935-896185c32dd3")

    if type(TargetFfs.Data.Header) == type(EFI_FFS_FILE_HEADER2()):
        TarParent = TargetFfs.Parent
        while TarParent:
            if TarParent.type == FV_TREE and struct2stream(TarParent.Data.Header.FileSystemGuid) == EFI_FIRMWARE_FILE_SYSTEM2_GUID_BYTE:
                TarParent.Data.Header.FileSystemGuid = ModifyGuidFormat("5473C07A-3DCB-4dca-BD6F-1E9689E7349A")
            TarParent = TarParent.Parent

class FvHandler:
    def __init__(self, NewFfs, TargetFfs) -> None:
        self.NewFfs = NewFfs
        self.TargetFfs = TargetFfs
        self.Status = False
        self.Remain_New_Free_Space = 0

    ## Use for Compress the Section Data
    def CompressData(self, TargetTree) -> None:
        TreePath = TargetTree.GetTreePath()
        pos = len(TreePath)
        self.Status = True
        while pos:
            if self.Status:
                if TreePath[pos-1].type == SECTION_TREE and TreePath[pos-1].Data.Type == 0x02:
                    self.CompressSectionData(TreePath[pos-1], None, TreePath[pos-1].Data.ExtHeader.SectionDefinitionGuid)
                else:
                    if pos == len(TreePath):
                        self.CompressSectionData(TreePath[pos-1], pos)
                    else:
                        self.CompressSectionData(TreePath[pos-1], None)
            pos -= 1

    def CompressSectionData(self, TargetTree, pos: int, GuidTool=None) -> None:
        NewData = b''
        temp_save_child = TargetTree.Child
        if TargetTree.Data:
            for item in temp_save_child:
                if item.type == SECTION_TREE and not item.Data.OriData and item.Data.ExtHeader:
                    NewData += struct2stream(item.Data.Header) + struct2stream(item.Data.ExtHeader) + item.Data.Data + item.Data.PadData
                elif item.type == SECTION_TREE and item.Data.OriData and not item.Data.ExtHeader:
                    NewData += struct2stream(item.Data.Header) + item.Data.OriData + item.Data.PadData
                elif item.type == SECTION_TREE and item.Data.OriData and item.Data.ExtHeader:
                    NewData += struct2stream(item.Data.Header) + struct2stream(item.Data.ExtHeader) + item.Data.OriData + item.Data.PadData
                elif item.type == FFS_FREE_SPACE:
                    NewData += item.Data.Data + item.Data.PadData
                else:
                    NewData += struct2stream(item.Data.Header) + item.Data.Data + item.Data.PadData
            if TargetTree.type == FFS_TREE:
                New_Pad_Size = GetPadSize(len(NewData), 8)
                Size_delta = len(NewData) - len(TargetTree.Data.Data)
                ChangeSize(TargetTree, -Size_delta)
                Delta_Pad_Size = len(TargetTree.Data.PadData) - New_Pad_Size
                self.Remain_New_Free_Space += Delta_Pad_Size
                TargetTree.Data.PadData = b'\xff' * New_Pad_Size
                TargetTree.Data.ModCheckSum()
            elif TargetTree.type == FV_TREE or TargetTree.type == SEC_FV_TREE and not pos:
                if self.Remain_New_Free_Space:
                    if TargetTree.Data.Free_Space:
                        TargetTree.Data.Free_Space += self.Remain_New_Free_Space
                        NewData += self.Remain_New_Free_Space * b'\xff'
                        TargetTree.Child[-1].Data.Data += self.Remain_New_Free_Space * b'\xff'
                    else:
                        TargetTree.Data.Data += self.Remain_New_Free_Space * b'\xff'
                        New_Free_Space = BIOSTREE('FREE_SPACE')
                        New_Free_Space.type = FFS_FREE_SPACE
                        New_Free_Space.Data = FreeSpaceNode(b'\xff' * self.Remain_New_Free_Space)
                        TargetTree.insertChild(New_Free_Space)
                    self.Remain_New_Free_Space = 0
                if TargetTree.type == SEC_FV_TREE:
                    Size_delta = len(NewData) + self.Remain_New_Free_Space - len(TargetTree.Data.Data)
                    TargetTree.Data.Header.FvLength += Size_delta
                TargetTree.Data.ModFvExt()
                TargetTree.Data.ModFvSize()
                TargetTree.Data.ModExtHeaderData()
                self.ModifyFvExtData(TargetTree)
                TargetTree.Data.ModCheckSum()
            elif TargetTree.type == SECTION_TREE and TargetTree.Data.Type != 0x02:
                New_Pad_Size = GetPadSize(len(NewData), 4)
                Size_delta = len(NewData) - len(TargetTree.Data.Data)
                ChangeSize(TargetTree, -Size_delta)
                if TargetTree.NextRel:
                    Delta_Pad_Size = len(TargetTree.Data.PadData) - New_Pad_Size
                    self.Remain_New_Free_Space += Delta_Pad_Size
                    TargetTree.Data.PadData = b'\x00' * New_Pad_Size
            TargetTree.Data.Data = NewData
        if GuidTool:
            ParPath = os.path.abspath(os.path.dirname(os.path.abspath(__file__))+os.path.sep+"..")
            ToolPath = os.path.join(ParPath, r'FMMTConfig.ini')
            guidtool = GUIDTools(ToolPath).__getitem__(struct2stream(GuidTool))
            CompressedData = guidtool.pack(TargetTree.Data.Data)
            if len(CompressedData) < len(TargetTree.Data.OriData):
                New_Pad_Size = GetPadSize(len(CompressedData), 4)
                Size_delta = len(CompressedData) - len(TargetTree.Data.OriData)
                ChangeSize(TargetTree, -Size_delta)
                if TargetTree.NextRel:
                    TargetTree.Data.PadData = b'\x00' * New_Pad_Size
                    self.Remain_New_Free_Space = len(TargetTree.Data.OriData) + len(TargetTree.Data.PadData) - len(CompressedData) - New_Pad_Size
                else:
                    TargetTree.Data.PadData = b''
                    self.Remain_New_Free_Space = len(TargetTree.Data.OriData) - len(CompressedData)
                TargetTree.Data.OriData = CompressedData
            elif len(CompressedData) == len(TargetTree.Data.OriData):
                TargetTree.Data.OriData = CompressedData
            elif len(CompressedData) > len(TargetTree.Data.OriData):
                New_Pad_Size = GetPadSize(CompressedData, 4)
                self.Remain_New_Free_Space = len(CompressedData) + New_Pad_Size - len(TargetTree.Data.OriData) - len(TargetTree.Data.PadData)
                Size_delta = len(TargetTree.Data.OriData) - len(CompressedData)
                ChangeSize(TargetTree, -Size_delta)
                if TargetTree.NextRel:
                    TargetTree.Data.PadData = b'\x00' * New_Pad_Size
                TargetTree.Data.OriData = CompressedData
                self.ModifyTest(TargetTree, self.Remain_New_Free_Space)
                self.Status = False

    def ModifyFvExtData(self, TreeNode) -> None:
        FvExtData = b''
        if TreeNode.Data.Header.ExtHeaderOffset:
            FvExtHeader = struct2stream(TreeNode.Data.ExtHeader)
            FvExtData += FvExtHeader
        if TreeNode.Data.Header.ExtHeaderOffset and TreeNode.Data.ExtEntryExist:
            FvExtEntry = struct2stream(TreeNode.Data.ExtEntry)
            FvExtData += FvExtEntry
        if FvExtData:
            InfoNode = TreeNode.Child[0]
            InfoNode.Data.Data = FvExtData + InfoNode.Data.Data[TreeNode.Data.ExtHeader.ExtHeaderSize:]
            InfoNode.Data.ModCheckSum()

    def ModifyTest(self, ParTree, Needed_Space: int) -> None:
        if Needed_Space > 0:
            if ParTree.type == FV_TREE or ParTree.type == SEC_FV_TREE:
                ParTree.Data.Data = b''
                Needed_Space = Needed_Space - ParTree.Data.Free_Space
                if Needed_Space < 0:
                    ParTree.Child[-1].Data.Data = b'\xff' * (-Needed_Space)
                    ParTree.Data.Free_Space = (-Needed_Space)
                    self.Status = True
                else:
                    if ParTree.type == FV_TREE:
                        self.Status = False
                    else:
                        BlockSize = ParTree.Data.Header.BlockMap[0].Length
                        New_Add_Len = BlockSize - Needed_Space%BlockSize
                        if New_Add_Len % BlockSize:
                            ParTree.Child[-1].Data.Data = b'\xff' * New_Add_Len
                            ParTree.Data.Free_Space = New_Add_Len
                            Needed_Space += New_Add_Len
                        else:
                            ParTree.Child.remove(ParTree.Child[-1])
                            ParTree.Data.Free_Space = 0
                        ParTree.Data.Size += Needed_Space
                        ParTree.Data.Header.Fvlength = ParTree.Data.Size
                for item in ParTree.Child:
                    if item.type == FFS_FREE_SPACE:
                        ParTree.Data.Data += item.Data.Data + item.Data.PadData
                    else:
                        ParTree.Data.Data += struct2stream(item.Data.Header)+ item.Data.Data + item.Data.PadData
                ParTree.Data.ModFvExt()
                ParTree.Data.ModFvSize()
                ParTree.Data.ModExtHeaderData()
                self.ModifyFvExtData(ParTree)
                ParTree.Data.ModCheckSum()
            elif ParTree.type == FFS_TREE:
                ParTree.Data.Data = b''
                for item in ParTree.Child:
                    if item.Data.OriData:
                        if item.Data.ExtHeader:
                            ParTree.Data.Data += struct2stream(item.Data.Header) + struct2stream(item.Data.ExtHeader) + item.Data.OriData + item.Data.PadData
                        else:
                            ParTree.Data.Data += struct2stream(item.Data.Header)+ item.Data.OriData + item.Data.PadData
                    else:
                        if item.Data.ExtHeader:
                            ParTree.Data.Data += struct2stream(item.Data.Header) + struct2stream(item.Data.ExtHeader) + item.Data.Data + item.Data.PadData
                        else:
                            ParTree.Data.Data += struct2stream(item.Data.Header)+ item.Data.Data + item.Data.PadData
                ChangeSize(ParTree, -Needed_Space)
                New_Pad_Size = GetPadSize(ParTree.Data.Size, 8)
                Delta_Pad_Size = New_Pad_Size - len(ParTree.Data.PadData)
                Needed_Space += Delta_Pad_Size
                ParTree.Data.PadData = b'\xff' * GetPadSize(ParTree.Data.Size, 8)
                ParTree.Data.ModCheckSum()
            elif ParTree.type == SECTION_TREE:
                OriData = ParTree.Data.Data
                ParTree.Data.Data = b''
                for item in ParTree.Child:
                    if item.type == SECTION_TREE and item.Data.ExtHeader and item.Data.Type != 0x02:
                        ParTree.Data.Data += struct2stream(item.Data.Header) + struct2stream(item.Data.ExtHeader) + item.Data.Data + item.Data.PadData
                    elif item.type == SECTION_TREE and item.Data.ExtHeader and item.Data.Type == 0x02:
                        ParTree.Data.Data += struct2stream(item.Data.Header) + struct2stream(item.Data.ExtHeader) + item.Data.OriData + item.Data.PadData
                    else:
                        ParTree.Data.Data += struct2stream(item.Data.Header) + item.Data.Data + item.Data.PadData
                if ParTree.Data.Type == 0x02:
                    ParTree.Data.Size += Needed_Space
                    ParPath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
                    ToolPath = os.path.join(os.path.dirname(ParPath), r'FMMTConfig.ini')
                    guidtool = GUIDTools(ToolPath).__getitem__(struct2stream(ParTree.Data.ExtHeader.SectionDefinitionGuid))
                    CompressedData = guidtool.pack(ParTree.Data.Data)
                    Needed_Space = len(CompressedData) - len(ParTree.Data.OriData)
                    ParTree.Data.OriData = CompressedData
                    New_Size = ParTree.Data.HeaderLength + len(CompressedData)
                    ParTree.Data.Header.Size[0] = New_Size % (16**2)
                    ParTree.Data.Header.Size[1] = New_Size % (16**4) //(16**2)
                    ParTree.Data.Header.Size[2] = New_Size // (16**4)
                    if ParTree.NextRel:
                        New_Pad_Size = GetPadSize(New_Size, 4)
                        Delta_Pad_Size = New_Pad_Size - len(ParTree.Data.PadData)
                        ParTree.Data.PadData = b'\x00' * New_Pad_Size
                        Needed_Space += Delta_Pad_Size
                    else:
                        ParTree.Data.PadData = b''
                elif Needed_Space:
                    ChangeSize(ParTree, -Needed_Space)
                    New_Pad_Size = GetPadSize(ParTree.Data.Size, 4)
                    Delta_Pad_Size = New_Pad_Size - len(ParTree.Data.PadData)
                    Needed_Space += Delta_Pad_Size
                    ParTree.Data.PadData = b'\x00' * New_Pad_Size
            NewParTree = ParTree.Parent
            ROOT_TYPE = [ROOT_FV_TREE, ROOT_FFS_TREE, ROOT_SECTION_TREE, ROOT_TREE]
            if NewParTree and NewParTree.type not in ROOT_TYPE:
                self.ModifyTest(NewParTree, Needed_Space)
        else:
            self.Status = True

    def ReplaceFfs(self) -> bool:
        TargetFv = self.TargetFfs.Parent
        # If the Fv Header Attributes is EFI_FVB2_ERASE_POLARITY, Child Ffs Header State need be reversed.
        if TargetFv.Data.Header.Attributes & EFI_FVB2_ERASE_POLARITY:
                self.NewFfs.Data.Header.State = c_uint8(
                    ~self.NewFfs.Data.Header.State)
        # NewFfs parsing will not calculate the PadSize, thus recalculate.
        self.NewFfs.Data.PadData = b'\xff' * GetPadSize(self.NewFfs.Data.Size, 8)
        if self.NewFfs.Data.Size >= self.TargetFfs.Data.Size:
            Needed_Space = self.NewFfs.Data.Size + len(self.NewFfs.Data.PadData) - self.TargetFfs.Data.Size - len(self.TargetFfs.Data.PadData)
            # If TargetFv have enough free space, just move part of the free space to NewFfs.
            if TargetFv.Data.Free_Space >= Needed_Space:
                # Modify TargetFv Child info and BiosTree.
                TargetFv.Child[-1].Data.Data = b'\xff' * (TargetFv.Data.Free_Space - Needed_Space)
                TargetFv.Data.Free_Space -= Needed_Space
                Target_index = TargetFv.Child.index(self.TargetFfs)
                TargetFv.Child.remove(self.TargetFfs)
                TargetFv.insertChild(self.NewFfs, Target_index)
                # Modify TargetFv Header and ExtHeader info.
                TargetFv.Data.ModFvExt()
                TargetFv.Data.ModFvSize()
                TargetFv.Data.ModExtHeaderData()
                self.ModifyFvExtData(TargetFv)
                TargetFv.Data.ModCheckSum()
                # return the Status
                self.Status = True
            # If TargetFv do not have enough free space, need move part of the free space of TargetFv's parent Fv to TargetFv/NewFfs.
            else:
                if TargetFv.type == FV_TREE:
                    self.Status = False
                else:
                    # Recalculate TargetFv needed space to keep it match the BlockSize setting.
                    Needed_Space -= TargetFv.Data.Free_Space
                    BlockSize = TargetFv.Data.Header.BlockMap[0].Length
                    New_Add_Len = BlockSize - Needed_Space%BlockSize
                    Target_index = TargetFv.Child.index(self.TargetFfs)
                    if New_Add_Len % BlockSize:
                        TargetFv.Child[-1].Data.Data = b'\xff' * New_Add_Len
                        TargetFv.Data.Free_Space = New_Add_Len
                        Needed_Space += New_Add_Len
                        TargetFv.insertChild(self.NewFfs, Target_index)
                        TargetFv.Child.remove(self.TargetFfs)
                    else:
                        TargetFv.Child.remove(self.TargetFfs)
                        TargetFv.Data.Free_Space = 0
                        TargetFv.insertChild(self.NewFfs)
                    # Encapsulate the Fv Data for update.
                    TargetFv.Data.Data = b''
                    for item in TargetFv.Child:
                        if item.type == FFS_FREE_SPACE:
                            TargetFv.Data.Data += item.Data.Data + item.Data.PadData
                        else:
                            TargetFv.Data.Data += struct2stream(item.Data.Header)+ item.Data.Data + item.Data.PadData
                    TargetFv.Data.Size += Needed_Space
                    # Modify TargetFv Data Header and ExtHeader info.
                    TargetFv.Data.Header.FvLength = TargetFv.Data.Size
                    TargetFv.Data.ModFvExt()
                    TargetFv.Data.ModFvSize()
                    TargetFv.Data.ModExtHeaderData()
                    self.ModifyFvExtData(TargetFv)
                    TargetFv.Data.ModCheckSum()
                    # Start free space calculating and moving process.
                    self.ModifyTest(TargetFv.Parent, Needed_Space)
        else:
            New_Free_Space = self.TargetFfs.Data.Size - self.NewFfs.Data.Size
            # If TargetFv already have free space, move the new free space into it.
            if TargetFv.Data.Free_Space:
                TargetFv.Child[-1].Data.Data += b'\xff' * New_Free_Space
                TargetFv.Data.Free_Space += New_Free_Space
                Target_index = TargetFv.Child.index(self.TargetFfs)
                TargetFv.Child.remove(self.TargetFfs)
                TargetFv.insertChild(self.NewFfs, Target_index)
                self.Status = True
            # If TargetFv do not have free space, create free space for Fv.
            else:
                New_Free_Space_Tree = BIOSTREE('FREE_SPACE')
                New_Free_Space_Tree.type = FFS_FREE_SPACE
                New_Free_Space_Tree.Data = FfsNode(b'\xff' * New_Free_Space)
                TargetFv.Data.Free_Space = New_Free_Space
                TargetFv.insertChild(New_Free_Space)
                Target_index = TargetFv.Child.index(self.TargetFfs)
                TargetFv.Child.remove(self.TargetFfs)
                TargetFv.insertChild(self.NewFfs, Target_index)
                self.Status = True
            # Modify TargetFv Header and ExtHeader info.
            TargetFv.Data.ModFvExt()
            TargetFv.Data.ModFvSize()
            TargetFv.Data.ModExtHeaderData()
            self.ModifyFvExtData(TargetFv)
            TargetFv.Data.ModCheckSum()
        return self.Status

    def AddFfs(self) -> bool:
        # NewFfs parsing will not calculate the PadSize, thus recalculate.
        self.NewFfs.Data.PadData = b'\xff' * GetPadSize(self.NewFfs.Data.Size, 8)
        if self.TargetFfs.type == FFS_FREE_SPACE:
            TargetLen = self.NewFfs.Data.Size + len(self.NewFfs.Data.PadData) - self.TargetFfs.Data.Size - len(self.TargetFfs.Data.PadData)
            TargetFv = self.TargetFfs.Parent
            # If the Fv Header Attributes is EFI_FVB2_ERASE_POLARITY, Child Ffs Header State need be reversed.
            if TargetFv.Data.Header.Attributes & EFI_FVB2_ERASE_POLARITY:
                self.NewFfs.Data.Header.State = c_uint8(
                    ~self.NewFfs.Data.Header.State)
            # If TargetFv have enough free space, just move part of the free space to NewFfs, split free space to NewFfs and new free space.
            if TargetLen < 0:
                self.Status = True
                self.TargetFfs.Data.Data = b'\xff' * (-TargetLen)
                TargetFv.Data.Free_Space = (-TargetLen)
                TargetFv.Data.ModFvExt()
                TargetFv.Data.ModExtHeaderData()
                self.ModifyFvExtData(TargetFv)
                TargetFv.Data.ModCheckSum()
                TargetFv.insertChild(self.NewFfs, -1)
                ModifyFfsType(self.NewFfs)
            elif TargetLen == 0:
                self.Status = True
                TargetFv.Child.remove(self.TargetFfs)
                TargetFv.insertChild(self.NewFfs)
                ModifyFfsType(self.NewFfs)
            # If TargetFv do not have enough free space, need move part of the free space of TargetFv's parent Fv to TargetFv/NewFfs.
            else:
                if TargetFv.type == FV_TREE:
                    self.Status = False
                elif TargetFv.type == SEC_FV_TREE:
                    # Recalculate TargetFv needed space to keep it match the BlockSize setting.
                    BlockSize = TargetFv.Data.Header.BlockMap[0].Length
                    New_Add_Len = BlockSize - TargetLen%BlockSize
                    if New_Add_Len % BlockSize:
                        self.TargetFfs.Data.Data = b'\xff' * New_Add_Len
                        self.TargetFfs.Data.Size = New_Add_Len
                        TargetLen += New_Add_Len
                        TargetFv.insertChild(self.NewFfs, -1)
                        TargetFv.Data.Free_Space = New_Add_Len
                    else:
                        TargetFv.Child.remove(self.TargetFfs)
                        TargetFv.insertChild(self.NewFfs)
                        TargetFv.Data.Free_Space = 0
                    ModifyFfsType(self.NewFfs)
                    TargetFv.Data.Data = b''
                    for item in TargetFv.Child:
                        if item.type == FFS_FREE_SPACE:
                            TargetFv.Data.Data += item.Data.Data + item.Data.PadData
                        else:
                            TargetFv.Data.Data += struct2stream(item.Data.Header)+ item.Data.Data + item.Data.PadData
                    # Encapsulate the Fv Data for update.
                    TargetFv.Data.Size += TargetLen
                    TargetFv.Data.Header.FvLength = TargetFv.Data.Size
                    TargetFv.Data.ModFvExt()
                    TargetFv.Data.ModFvSize()
                    TargetFv.Data.ModExtHeaderData()
                    self.ModifyFvExtData(TargetFv)
                    TargetFv.Data.ModCheckSum()
                    # Start free space calculating and moving process.
                    self.ModifyTest(TargetFv.Parent, TargetLen)
        else:
            # If TargetFv do not have free space, need directly move part of the free space of TargetFv's parent Fv to TargetFv/NewFfs.
            TargetLen = self.NewFfs.Data.Size + len(self.NewFfs.Data.PadData)
            TargetFv = self.TargetFfs.Parent
            if TargetFv.Data.Header.Attributes & EFI_FVB2_ERASE_POLARITY:
                self.NewFfs.Data.Header.State = c_uint8(
                    ~self.NewFfs.Data.Header.State)
            if TargetFv.type == FV_TREE:
                self.Status = False
            elif TargetFv.type == SEC_FV_TREE:
                BlockSize = TargetFv.Data.Header.BlockMap[0].Length
                New_Add_Len = BlockSize - TargetLen%BlockSize
                if New_Add_Len % BlockSize:
                    New_Free_Space = BIOSTREE('FREE_SPACE')
                    New_Free_Space.type = FFS_FREE_SPACE
                    New_Free_Space.Data = FreeSpaceNode(b'\xff' * New_Add_Len)
                    TargetLen += New_Add_Len
                    TargetFv.Data.Free_Space = New_Add_Len
                    TargetFv.insertChild(self.NewFfs)
                    TargetFv.insertChild(New_Free_Space)
                else:
                    TargetFv.insertChild(self.NewFfs)
                ModifyFfsType(self.NewFfs)
                TargetFv.Data.Data = b''
                for item in TargetFv.Child:
                    if item.type == FFS_FREE_SPACE:
                        TargetFv.Data.Data += item.Data.Data + item.Data.PadData
                    else:
                        TargetFv.Data.Data += struct2stream(item.Data.Header)+ item.Data.Data + item.Data.PadData
                TargetFv.Data.Size += TargetLen
                TargetFv.Data.Header.FvLength = TargetFv.Data.Size
                TargetFv.Data.ModFvExt()
                TargetFv.Data.ModFvSize()
                TargetFv.Data.ModExtHeaderData()
                self.ModifyFvExtData(TargetFv)
                TargetFv.Data.ModCheckSum()
                self.ModifyTest(TargetFv.Parent, TargetLen)
        return self.Status

    def DeleteFfs(self) -> bool:
        Delete_Ffs = self.TargetFfs
        Delete_Fv = Delete_Ffs.Parent
        Add_Free_Space = Delete_Ffs.Data.Size + len(Delete_Ffs.Data.PadData)
        if Delete_Fv.Data.Free_Space:
            if Delete_Fv.type == SEC_FV_TREE:
                Used_Size = Delete_Fv.Data.Size - Delete_Fv.Data.Free_Space - Add_Free_Space
                BlockSize = Delete_Fv.Data.Header.BlockMap[0].Length
                New_Free_Space = BlockSize - Used_Size % BlockSize
                self.Remain_New_Free_Space += Delete_Fv.Data.Free_Space + Add_Free_Space - New_Free_Space
                Delete_Fv.Child[-1].Data.Data = New_Free_Space * b'\xff'
                Delete_Fv.Data.Free_Space = New_Free_Space
            else:
                Used_Size = Delete_Fv.Data.Size - Delete_Fv.Data.Free_Space - Add_Free_Space
                Delete_Fv.Child[-1].Data.Data += Add_Free_Space * b'\xff'
                Delete_Fv.Data.Free_Space += Add_Free_Space
                New_Free_Space = Delete_Fv.Data.Free_Space + Add_Free_Space
        else:
            if Delete_Fv.type == SEC_FV_TREE:
                Used_Size = Delete_Fv.Data.Size - Add_Free_Space
                BlockSize = Delete_Fv.Data.Header.BlockMap[0].Length
                New_Free_Space = BlockSize - Used_Size % BlockSize
                self.Remain_New_Free_Space += Add_Free_Space - New_Free_Space
                Add_Free_Space = New_Free_Space
            else:
                Used_Size = Delete_Fv.Data.Size - Add_Free_Space
                New_Free_Space = Add_Free_Space
            New_Free_Space_Info = FfsNode(Add_Free_Space * b'\xff')
            New_Free_Space_Info.Data = Add_Free_Space * b'\xff'
            New_Ffs_Tree = BIOSTREE(New_Free_Space_Info.Name)
            New_Ffs_Tree.type = FFS_FREE_SPACE
            New_Ffs_Tree.Data = New_Free_Space_Info
            Delete_Fv.insertChild(New_Ffs_Tree)
            Delete_Fv.Data.Free_Space = Add_Free_Space
        Delete_Fv.Child.remove(Delete_Ffs)
        Delete_Fv.Data.Header.FvLength = Used_Size + New_Free_Space
        Delete_Fv.Data.ModFvExt()
        Delete_Fv.Data.ModFvSize()
        Delete_Fv.Data.ModExtHeaderData()
        self.ModifyFvExtData(Delete_Fv)
        Delete_Fv.Data.ModCheckSum()
        self.CompressData(Delete_Fv)
        self.Status = True
        return self.Status
