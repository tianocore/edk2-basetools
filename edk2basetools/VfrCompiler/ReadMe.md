# Python VfrCompiler Tool
## Overview
This python VfrCompiler tool is the python implementation of the edk2 VfrCompiler tool which C implementation locates at https://github.com/tianocore/edk2/tree/master/BaseTools/Source/C/VfrCompile.

This python implementation not only covers the same usage as the C version VfrCompiler, but also extends several new features.

### Introduction
The core function of the original C VfrCompiler tool is to convert VFR files into IFR binaries. However, the VFR format syntax is uncommon and has poor readability for users. Additionally, the C tool doesn't gather or store default variable information, except for binary generation. When modifications are required, developers have to deal with the abstract IFR binary, resulting in inefficiency. To address these challenges, this python tool generates YAML format files from VFR files. This approach allows for preservation of the VFR file's opcode layout and hierarchy, simplifying readability. Moreover, the tool generates an additional JSON file to provide a more accessible presentation of variable-related information. In a few words, the new tool offers the same usage as the original C VfrCompiler while expanding functionality with the YAML/JSON output, enhancing readability and adaptability.

### Main update in this commitment
- Update the vfr parser generator from ANTLR to ANTLR v4, which is more readable and is eaiser to add on new grammars and functions.
- Cover the same usage as the edk2 C VfrCompiler. The tool is able to compiles VFR into .c/lst/hpk output files.
- Extract variable information from each VFR file to JSON. The output JSON file stores the data structures and default values of variables.
- Convert each VFR source format to an equivalent YAML. The generated YAML file covers the same format contents in the Vfr file.

### Known issues

- The current YAML format is a reference version, and we warmly welcome everyone to provide feedback.
- The tool will extend new functions, which is able to compile yaml files. This feature will be added in future update.

### Use with Build System
- To use the VfrCompiler Python Tool with Build System,  please do the following steps in the build command.
1. Open  **'build_rule.template'**  file  in path **'\edk2\BaseTools\Conf\'.**
  - Find the C VFR command line `$(VFR)" $(VFR_FLAGS) --string-db $(OUTPUT_DIR)(+)$(MODULE_NAME)StrDefs.hpk --output-directory ${d_path} $(OUTPUT_DIR)(+)${s_base}.i` in **build_rule.template** file. There are two C VFR commands in it.
  - Add new command line `"$(PYVFR)" ${src} --string-db $(OUTPUT_DIR)(+)$(MODULE_NAME)StrDefs.hpk -w $(WORKSPACE) -m $(MODULE_NAME) -o $(OUTPUT_DIR) --vfr` after each VFR command lines.
2. Open  **'tools_def.template'**  file  in path **'\edk2\BaseTools\Conf\'.**
  - Find the C VFR_PATH command line `*_*_*_VFR_PATH                      = VfrCompile` in **tools_def.template** file .
  - Add new command line `*_*_*_PYVFR_PATH                    = PyVfrCompile` after the VFR_PATH command line.
3. Create a **PyVfrCompile.bat** file in path **'C:\edk2\BaseTools\BinWrappers\WindowsLike'.**
  - Add the following lines in the created **PyVfrCompile.bat** file.
    ```
    @setlocal
    @set ToolName=IfrCompiler
    @set PYTHONPATH=%PYTHONPATH%;%BASE_TOOLS_PATH%\Source\Python;%BASE_TOOLS_PATH%\Source\Python\VfrCompiler
    @%PYTHON_COMMAND% -m %ToolName% %*
    ```
4. Add Env: run `pip install CppHeader` based on the original build environment.
5. Run Build Command: `build -p OvmfPkg\OvmfPkgIa32X64.dsc -a IA32 -a X64 -j build.log`
`
