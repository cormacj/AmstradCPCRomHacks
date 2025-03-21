#!/usr/bin/env python3

# Copyright (c) 2025 Cormac McGaughey
#
# GNU GENERAL PUBLIC LICENSE
#    Version 3, 29 June 2007
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Sometimes files get exported with a disc header and that breaks in an emulator.
# This fixes that issue

import sys

def to_number(n):
    """
    Convert a string in most formats to a number
    @params:
        n   - Required: A string containing a number in any format
    """
    try:
        return int(str(n), 0)
    except Exception:
        try:
            return int('0x' + n, 0)
        except Exception:
            return float(n)

headersize=0x80
argc = len(sys.argv)
# print(argc)
# print(sys.argv)
if argc <= 1 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
    print("A tool to remove AMSDOS headers from an image.\n")
    print("Usage: headertool.py source.rom destination.rom -n <size of header to remove>")
    print("   -n is optional, defaults to 0x80")
    print("\nExample:\nheadertool.py CPM1.rom CPM1-fixed.rom -n 0x7f")
    print("\nCopyright (c) 2025 Cormac McGaughey")
    quit()
elif argc == 3:
    srcname = sys.argv[1]
    destname = sys.argv[2]

if argc == 4:
    headersize=to_number(sys.argv[3])


if srcname==destname:
    print("Error: Source and Destination should not be the same")
    quit()

with open(srcname, 'rb') as inFile:
    inFile.seek(headersize)
    with open(destname, 'wb') as outFile:
        image=inFile.read()
        outFile.write(image)
inFile.close()
outFile.close()
