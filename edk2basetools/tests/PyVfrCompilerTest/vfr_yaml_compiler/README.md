# Python Vfrcompiler Unit test

## OverView
The feature is the implementation of unit test for the python vfrcompiler tool.
## Introduction
We choose ten VFR files from the following modules in the edk2 as test cases.
- IScsiDxe
- VlanConfigDxe
- Platform
- BootMaintenanceManagerUiLib
- BootManagerUiLib
- DeviceManagerUiLib
- FileExplorerLib
- Ip4Dxe
- UiApp
- RamDiskDxeBoot

We do the testing from the following two aspects.

1. Syntax parser test
- In test_vfr_syntax.py, We add class **TestVfrcompilSyntax** to test the correctness of the vfr syntax and the antlr parser.
- We generate test cases for each type of VFR syntax component and validate the output from each component's syntax parser.

2. Function test
- In test_Vfrcompiler.py, We add function test for the  **PreProcess()** / **Compile()** / **GenBinaryFiles()** / **DumpSourceYaml()** functions of the tool.

3. Output test
- In test_Vfrcompiler.py, We add the **test_vfr_lst_file ()** function to do the comparsions.
- To differentiate from the original C tool output files, the python tool generated files are named with prefix 'PyVfr'. We compare the python tool generated IFR file with the C tool generated ones to valid the effectiveness of the new tool.

## Add test cases
If you want to add more test cases to do further validation, please do the following steps.
- Open **edk2\BaseTools\Source\Python\VfrCompiler_test\pytest.ini**
- Add the module you want to test in `target_test_folders`

  ```
  target_test_folders =
     Module Name you want to test
  ```

## Run test
To apply the unit test feature, please do the following steps.
1. Locate the **VfrCompiler_test** folder to **edk2\BaseTools\Source\Python**
2. Refer to **edk2basetools\VfrCompiler\README.md** and run build command.
3. Add Env: run `pip install pytest` based on the original build environment.
4. run `cd edk2\BaseTools\Source\Python\VfrCompiler_test`
5. run command `pytest` in edk2\BaseTools\Source\Python\VfrCompiler_test
