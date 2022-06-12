# @file
# build a platform or a module
#
#  Copyright (c) 2014, Hewlett-Packard Development Company, L.P.<BR>
#  Copyright (c) 2007 - 2021, Intel Corporation. All rights reserved.<BR>
#  Copyright (c) 2018 - 2020, Hewlett Packard Enterprise Development, L.P.<BR>
#
#  SPDX-License-Identifier: BSD-2-Clause-Patent
#

# Version and Copyright
from edk2basetools.Common.BuildVersion import gBUILD_VERSION
from argparse import ArgumentParser
VersionNumber = "0.60" + ' ' + gBUILD_VERSION
__version__ = "%(prog)s Version " + VersionNumber
__copyright__ = "Copyright (c) 2007 - 2018, Intel Corporation  All rights reserved."
__usage__ = "%(prog)s [options] TARGET"


class MyOptionParser():

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(MyOptionParser, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'BuildArguments'):
            self.BuildArguments = None

    def GetOption(self):
        Parser = ArgumentParser(description=__copyright__, prog="edk2_build", usage=__usage__)
        Parser.add_argument("Target", metavar="TARGET", type=str, choices=['all', 'genc', 'genmake', 'modules', 'libraries', 'fds', 'clean', 'cleanall', 'cleanlib',
                            'run'], help="target is one of the list: all, fds, genc, genmake, clean, cleanall, cleanlib, modules, libraries, run", default="all", nargs='?')
        Parser.add_argument('--version', action='version', version=__version__)
        Parser.add_argument("-a", "--arch", action="append", dest="TargetArch", choices=['IA32', 'X64', 'ARM', 'AARCH64', 'RISCV64', 'EBC'],
                            help="ARCHS is one of list: IA32, X64, ARM, AARCH64, RISCV64 or EBC, which overrides target.txt's TARGET_ARCH definition. To specify more archs, please repeat this option.")
        Parser.add_argument("-p", "--platform", type=str, dest="PlatformFile",
                            help="Build the platform specified by the DSC file name argument, overriding target.txt's ACTIVE_PLATFORM definition.")
        Parser.add_argument("-m", "--module", type=str, dest="ModuleFile",
                            help="Build the module specified by the INF file name argument.")
        Parser.add_argument("-b", "--buildtarget", type=str, dest="BuildTarget", action="append",
                            help="Using the TARGET to build the platform, overriding target.txt's TARGET definition.")
        Parser.add_argument("-t", "--tagname", action="append", type=str, dest="ToolChain",
                            help="Using the Tool Chain Tagname to build the platform, overriding target.txt's TOOL_CHAIN_TAG definition.")
        Parser.add_argument("-x", "--sku-id", type=str, dest="SkuId",
                            help="Using this name of SKU ID to build the platform, overriding SKUID_IDENTIFIER in DSC file.")

        Parser.add_argument("-n", type=int, dest="ThreadNumber", help="Build the platform using multi-threaded compiler. "
                            "The value overrides target.txt's MAX_CONCURRENT_THREAD_NUMBER. "
                            "When value is set to 0, tool automatically detect number of processor threads, "
                            "set value to 1 means disable multi-thread build, "
                            "and set value to more than 1 means user specify the threads number to build.")

        Parser.add_argument("-f", "--fdf", type=str, dest="FdfFile",
                            help="The name of the FDF file to use, which overrides the setting in the DSC file.")
        Parser.add_argument("-r", "--rom-image", action="append", type=str, dest="RomImage", default=[],
                            help="The name of FD to be generated. The name must be from [FD] section in FDF file.")
        Parser.add_argument("-i", "--fv-image", action="append", type=str, dest="FvImage", default=[],
                            help="The name of FV to be generated. The name must be from [FV] section in FDF file.")
        Parser.add_argument("-C", "--capsule-image", action="append", type=str, dest="CapName", default=[],
                            help="The name of Capsule to be generated. The name must be from [Capsule] section in FDF file.")
        Parser.add_argument("-u", "--skip-autogen", action="store_true", dest="SkipAutoGen", help="Skip AutoGen step.")
        Parser.add_argument("-e", "--re-parse", action="store_true",
                            dest="Reparse", help="Re-parse all meta-data files.")

        Parser.add_argument("-c", "--case-insensitive", action="store_true", dest="CaseInsensitive",
                            default=False, help="Don't check case of file name.")

        Parser.add_argument("-w", "--warning-as-error", action="store_true",
                            dest="WarningAsError", help="Treat warning in tools as error.")
        Parser.add_argument("-j", "--log", action="store", dest="LogFile",
                            help="Put log in specified file as well as on console.")

        Parser.add_argument("-s", "--silent", action="store_true", dest="SilentMode",
                            help="Make use of silent mode of (n)make.")
        Parser.add_argument("-q", "--quiet", action="store_true", help="Disable all messages except FATAL ERRORS.")
        Parser.add_argument("-v", "--verbose", action="store_true", help="Turn on verbose output with informational messages printed, "
                            "including library instances selected, final dependency expression, "
                            "and warning messages, etc.")
        Parser.add_argument("-d", "--debug", action="store", type=int, help="Enable debug messages at specified level.")
        Parser.add_argument("-D", "--define", action="append", type=str,
                            dest="Macros", help="Macro: \"Name [= Value]\".")

        Parser.add_argument("-y", "--report-file", action="store", dest="ReportFile",
                            help="Create/overwrite the report to the specified filename.")
        Parser.add_argument("-Y", "--report-type", action="append", type=str, dest="ReportType", default=[], choices=['PCD', 'LIBRARY', 'FLASH', 'DEPEX', 'BUILD_FLAGS', 'FIXED_ADDRESS', 'HASH', 'EXECUTION_ORDER'],
                            help="Flags that control the type of build report to generate. "
                            "Must be one of: [PCD, LIBRARY, FLASH, DEPEX, BUILD_FLAGS, FIXED_ADDRESS, HASH, EXECUTION_ORDER]. "
                            "To specify more than one flag, repeat this option on the command line and the default flag set is "
                            "[PCD, LIBRARY, FLASH, DEPEX, HASH, BUILD_FLAGS, FIXED_ADDRESS]")
        Parser.add_argument("-F", "--flag", action="store", type=str, dest="Flag", choices=['-c', '-s'],
                            help="Specify the specific option to parse EDK UNI file. Must be one of: [-c, -s]. "
                            "-c is for EDK framework UNI file, and -s is for EDK UEFI UNI file. "
                            "This option can also be specified by setting *_*_*_BUILD_FLAGS in [BuildOptions] section of platform DSC. "
                            "If they are both specified, this value will override the setting in [BuildOptions] section of platform DSC.")
        Parser.add_argument("-N", "--no-cache", action="store_true", dest="DisableCache",
                            help="Disable build cache mechanism")
        Parser.add_argument("--conf", action="store", type=str, dest="ConfDirectory",
                            help="Specify the customized Conf directory.")
        Parser.add_argument("--check-usage", action="store_true", dest="CheckUsage", default=False,
                            help="Check usage content of entries listed in INF file.")
        Parser.add_argument("--ignore-sources", action="store_true", dest="IgnoreSources",
                            help="Focus to a binary build and ignore all source files")
        Parser.add_argument("--pcd", action="append", dest="OptionPcd",
                            help="Set PCD value by command line. Format: \"PcdName=Value\" ")
        Parser.add_argument("-l", "--cmd-len", action="store", type=int, dest="CommandLength",
                            help="Specify the maximum line length of build command. Default is 4096.")
        Parser.add_argument("--hash", action="store_true", dest="UseHashCache", default=False,
                            help="Enable hash-based caching during build process.")
        Parser.add_argument("--binary-destination", action="store", type=str, dest="BinCacheDest",
                            help="Generate a cache of binary files in the specified directory.")
        Parser.add_argument("--binary-source", action="store", type=str, dest="BinCacheSource",
                            help="Consume a cache of binary files from the specified directory.")

        # WARNING: Redundant Flag. Maybe should be removed
        Parser.add_argument("--genfds-multi-thread", action="store_true", dest="GenfdsMultiThread",
                            default=True, help="Enable GenFds multi thread to generate ffs file.")

        Parser.add_argument("--no-genfds-multi-thread", action="store_true", dest="NoGenfdsMultiThread",
                            help="Disable GenFds multi thread to generate ffs file.")
        Parser.add_argument("--disable-include-path-check", action="store_true", dest="DisableIncludePathCheck",
                            help="Disable the include path check for outside of package.")

        self.BuildArguments = Parser.parse_args()
