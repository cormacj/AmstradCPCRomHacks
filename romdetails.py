#!/usr/bin/env python3

# Copyright (c) 2023 Cormac McGaughey
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


#This program is designed to patch the Graduate software CPM+ rom for Amstrad CPC systems

import sys


def dumphelp():
    print ("Usage:")
    print ("This will display the RSX commands (if any) available in a ROM:")
    print ("  romdetails.py SourceROM.rom\n\n")
    print("Examples:")
    print("\t./romdetails.py TestROM.rom\n\tRom type: Background\n\tVersion:  1.21\n\n\tTESTROM\n\tRSX1\n\tRSX2\n\tHidden Command: 0x0\n\tHidden Command: 0x1\n")
    quit()
    return
argc = len(sys.argv)

loc = 0

src=""

if argc <= 1:
    dumphelp()

values=range(argc)

#Process the command line parameters
for param in values:
    if (sys.argv[param] =="-h") or (sys.argv[param]=="--help"):
        dumphelp()
    else:
        src = sys.argv[param]
        sourceset=1

#Make sure we have a source or we error out
if sourceset==-1:
    print("Error: You must specify a source rom filename")
    quit()

addrl=0
addrh=0
rsx=0xffff
cmdend=-1
command=""
version=""

#Scan the source rom
with open(src, "rb") as f:
    #print("Reading from: "+src)
    while (byte := f.read(1)):
        value=int.from_bytes(byte,"little")
        if (loc==0x0000):
            match value:
                case 0:
                    print("Rom type: External Foreground")
                case 1:
                    print("Rom type: Background")
                case 2:
                    print("Rom type: Extension Foreground")
                case 0x80:
                    print("Rom type: Internal, eg BASIC")
                case _:
                    print("Rom type: Unknown, id=",hex(value))
            #print("\n")
        if (loc==0x0001):
            version=version+chr(value+48)+"."
        if (loc==0x0002):
            version=version+chr(value+48)
        if (loc==0x0003):
            version=version+chr(value+48)
            print ("Version: ",version,"\n")
        if (loc==0x0004):
            addrl=value
            #print(hex(value))
        if (loc==0x0005):
            addrh=value
            rsx=((addrh*256)+addrl)-0xc000
        if (loc>=rsx) and (cmdend==-1):
            if value>127:
                if (value-128)<31:
                    if command=="":
                        print("Hidden Command:",hex(value-128))
                else:
                    command=command+chr(value-128)
                    print (command)
                    command=""
            if value==0:
                cmdend=0
            if (value>31) and (value<127) and cmdend==-1:
                command=command+chr(value)
        loc = loc + 1

cmds=(addrh*256)+addrl
#print(hex(cmds))
