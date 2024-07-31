## @file
# Calculate Crc32 value and Verify Crc32 value for input data.
#
# Copyright (c) 2007 - 2018, Intel Corporation. All rights reserved.<BR>
# SPDX-License-Identifier: BSD-2-Clause-Patent
#
#

##
# Import Modules
#
import logging
import argparse
import sys
from binascii import crc32


parser = argparse.ArgumentParser(description='''
Calculate Crc32 value and Verify Crc32 value for input data.
''')
parser.add_argument("-e", "--encode", dest="EncodeInputFile",
                    help="Calculate andverify CRC32 value for the input file.")
parser.add_argument("-d", "--decode", dest="DecodeInputFile",
                    help="Verify CRC32 value for the input file.")
parser.add_argument("-o", "--output", dest="OutputFile",
                    help="Output file name.")
parser.add_argument("-s", "--silent", help="Returns only the exit code;\
                        informational and error messages are not displayed.")
parser.add_argument("--version", action="version", version='%(prog)s Version 2.0',
                    help="Show program's version number and exit.")

group = parser.add_mutually_exclusive_group()
group.add_argument("-v", "--verbose", action="store_true", help="Print information statements")
group.add_argument("-q", "--quiet", action="store_true", help="Disable all messages except fatal errors")


## Calculate the Crc32 and store it in the file
def CalculateCrc32(inputfile: str, outputfile: str, filebytes=b''):
    logger = logging.getLogger('GenCrC32')
    try:
        if filebytes != b'':
            InputData = filebytes
            CrcCheckSum = crc32(InputData).to_bytes(4, byteorder="little")
        else:
            with open(inputfile, 'rb') as fin:
                InputData = fin.read()
            CrcCheckSum = crc32(InputData).to_bytes(4, byteorder="little")
            with open(outputfile, 'wb') as fout:
                fout.write(CrcCheckSum)
                fout.write(InputData)
    except Exception as err:
        logger.error("Calculation failed!")
        raise (err)
    return CrcCheckSum


## Verify the CRC and checkout if the file is correct
def VerifyCrc32(inputfile: str, outputfile=""):
    logger = logging.getLogger('GenCrC32')
    try:
        with open(inputfile, 'rb') as fin:
            InputData = fin.read()
            CurCrcCheckSum = InputData[0:4]
            CalCrcCheckSum = CalculateCrc32('', '', InputData[4:])
        if CurCrcCheckSum != CalCrcCheckSum:
            logger.error("Invalid file!")
        elif outputfile != "":
            with open(outputfile, 'wb') as fout:
                fout.write(InputData[4:])
    except Exception as err:
        logger.error("Verification failed!")
        raise (err)


def main():
    args = parser.parse_args()

    logger = logging.getLogger('GenCrc32')
    if args.quiet:
        logger.setLevel(logging.CRITICAL)
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    lh = logging.StreamHandler(sys.stdout)
    lf = logging.Formatter("%(levelname)-8s: %(message)s")
    lh.setFormatter(lf)
    logger.addHandler(lh)

    try:
        if not args.OutputFile:
            parser.print_help()
            logger.error("Missing options - outputfile!")
            assert ()
        if args.EncodeInputFile:
            CalculateCrc32(args.EncodeInputFile, args.OutputFile)
        elif args.DecodeInputFile:
            VerifyCrc32(args.DecodeInputFile, args.OutputFile)
    except Exception:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
