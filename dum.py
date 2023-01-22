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
    print ("Usage: dum.py romfile.rom <xor hex value>")
elif argc == 2:
    dumpname=sys.argv[1]
    xorval=0
else:
    dumpname=sys.argv[1]
    xorval=int(sys.argv[2],16)

#print ("xorval=",xorval)

loc = 0
with open(dumpname, "rb") as f:
    while (byte := f.read(1)):
        # Do stuff with byte.
        #print(loc%64)
        value=int.from_bytes(byte,"little")
        #value=value^0xaa #password
        #value=value^0x4e #name etc
        value=value^xorval
        if ((loc%64)==0):
            print ("\n"+hex(loc)+": ", end='')
        loc = loc + 1
        if (value>31 and value<127):
            print(chr(value),end='')
        else:
            print(".",end='')
print("\n")
