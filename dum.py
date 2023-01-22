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


import sys

argc = len(sys.argv)
#print(argc)
if argc <= 1:
    print ("Usage: dum.py romfile.rom <xor hex value>\nExample: dum.py CPM1.rom 0x4e")
    quit()
elif argc == 2:
    dumpname=sys.argv[1]
    xorval=0 #xor 0 is no xor
else:
    dumpname=sys.argv[1]
    xorval=int(sys.argv[2],16)

#print ("xorval=",xorval)

loc = 0
hexpart=""
strpart=""
locstr=(str(hex(loc)).split("x")[1]).rjust(4,"0")

with open(dumpname, "rb") as f:
    while (byte := f.read(1)):
        # Do stuff with byte.
        #print(loc%64)
        value=int.from_bytes(byte,"little")
        #value=value^0xaa #password
        #value=value^0x4e #name etc
        value=value^xorval
        hexsingle=(str(hex(value)).split("x")[1]).rjust(2,"0") #covert the value to hex and strip off the 0x part and pad to double digits, ie 8 becomes 0x8 and ends as 08

        if (loc>0 and (loc%16)==0):
            print (locstr+": "+hexpart+"  "+strpart)
            hexpart=""
            strpart=""
            locstr=(str(hex(loc)).split("x")[1]).rjust(4,"0")
        if (value>31 and value<127):
            strsingle=chr(value)
        else:
            strsingle="."
            #print(".",end='')
        if hexpart=="":
            hexpart=hexsingle+" "
            strpart=strsingle
        else:
            hexpart=hexpart+hexsingle+" "
            strpart=strpart+strsingle

        loc = loc + 1

print("\n")
