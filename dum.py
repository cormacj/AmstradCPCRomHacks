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

#This program is aimed at exploring the contents of Amstrad ROM files
#It has an optional XOR argument as some ROMs like the Graduate software
#CPM+ roms has encoded areas for user details and password

import sys

argc = len(sys.argv)
#print(argc)
if argc <= 1 or sys.argv[1]=="-h" or sys.argv[1]=="--help":
    print ("Usage: dum.py romfile.rom -x <xor hex value>")
    print ("   or: dum.py romfile.rom -o <address offset value>\n")
    print ("  Known XOR values are:")
    print ("    0xaa - password")
    print ("    0x4e - name, address, serial etc\n")
    print ("Examples:\ndum.py CPM1.rom -x 0x4e")
    print ("dum.py Rodos_v2_17.ROM -o 0xc000")
    quit()
elif argc == 2:
    dumpname=sys.argv[1]
    xorval=0 #xor 0 is no xor
    romoffsetval=0 #dumps will show as 0x0000
else:
    xorval=0
    romoffsetval=0
    dumpname=sys.argv[1]
    #We're going to parse what extras we warranty
    if sys.argv[2]=='-x':
            xorval=int(sys.argv[3],16)
    if sys.argv[2]=='-o':
            romoffsetval=int(sys.argv[3],16)

loc = romoffsetval
hexpart=""
strpart=""
#print (dumpname)
locstr=(str(hex(loc)).split("x")[1]).rjust(4,"0")
try:
    with open(dumpname, "rb") as f:
        while (byte := f.read(1)):
            # Do stuff with byte.
            #print(loc%64)
            value=int.from_bytes(byte,"little")
            #value=value^0xaa #password
            #value=value^0x4e #name etc
            value=value^xorval
            hexsingle=(str(hex(value)).split("x")[1]).rjust(2,"0") #covert the value to hex and strip off the 0x part and pad to double digits, ie 8 becomes 0x8 and ends as 08

            if (loc>romoffsetval and (loc%16)==0):
                print (locstr+": "+hexpart+"  "+strpart)
                hexpart=""
                strpart=""
                locstr=(str(hex(loc)).split("x")[1]).rjust(4,"0")
            if (value>31 and value<127): #It's human readable, use what we read
                strsingle=chr(value)
            else:
                strsingle="." #it's not readable, print a dot
                #print(".",end='')
            if hexpart=="":
                hexpart=hexsingle+" "
                strpart=strsingle
            else:
                hexpart=hexpart+hexsingle+" "
                strpart=strpart+strsingle
            loc = loc + 1

    print (locstr+": "+hexpart+"  "+strpart)
    print("\n")
except FileNotFoundError:
    msg = "Sorry, the file "+ dumpname + " doesn't exist."
    print(msg)
except BrokenPipeError:
    #Just exit nicly so things like piping to head or more doesn't end ugly
    #print ("Broken pipe error")
    quit()
finally:
    #print ("Quitting nicely")
    #just quit
    quit()
