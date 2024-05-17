#!/usr/bin/env python3
#TODO: Add a flag and command to only print the rom commands

# Copyright (c) 2023,2024 Cormac McGaughey
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

#This progam is designed to decode Amstrad ROMs and display details and commands from those.

import sys

def versioncheck(val: int) -> int:
    # Sometimes roms actually have the ASCII values of the version code embedded
    # so this is a "just in case" check. If it find a value>9 then try subtracting
    # ascii 0 from it. It might work.
    #
    if (val>9):
        val=val-ord("0")
    return val

def parsebyte(val :int) -> str:
    # Parse out what to do with a byte we've read
    # If its less than 32, make it hex
    # If its greater than 128, (ie end of RSX command) but the value is less than 32 when converted, hex it.
    # otherwise, convert it back to a normal character
    #
    tmp=""
    if (val<32):
        tmp=hex(val)+","
    elif (val>127):
        if (val-128)<32:
            tmp=hex(val-128)
        else:
            tmp=chr(val-128)
    else:
        tmp=chr(val)
    return tmp

def dumphelp():
    print ("romdetails.py",myversion,"\n")
    print ("Usage:")
    print ("This will display the RSX commands (if any) available in a ROM:")
    print ("  romdetails.py SourceROM.rom\n\n")
    print("Examples:")
    print("\t./romdetails.py TestROM.rom\n\tRom type: Background\n\tVersion:  1.21\n\n\tTESTROM\n\tRSX1\n\tRSX2\n\tHidden Command: 0x0\n\tHidden Command: 0x1\n")
    print ("-h or --help - this message")
    print ("-c or --commandonly - only list the commands, suitable for sorting\n")
    quit()
    return
argc = len(sys.argv)

#-------------------------
loc = 0
commandonly=0 #Don't print versions etc, only commands
myversion="v2.00"
#--------------------------
src=""

if argc <= 1:
    dumphelp()

values=range(argc)

#Process the command line parameters
for param in values:
    if (sys.argv[param] =="-h") or (sys.argv[param]=="--help"):
        dumphelp()
    elif (sys.argv[param] =="-c") or (sys.argv[param]=="--commandonly"):
        commandonly=1
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
cmdend=-1 #flag when we reached the end of the commands
hiddencmd=0 #flag for hidden commands
romname=1 #flag for the rom name (it looks like an RSX command, but its not.)
command="" #string used when building commands from the ROM
version="" #string used when decoding the ROM version details

#Scan the source rom
with open(src, "rb") as f:
    #print("Reading from: "+src)
    while (byte := f.read(1)):
        value=int.from_bytes(byte,"little")
        if (loc==0x0000) and (commandonly==0):
            match value:
                case 0:
                    print("Rom type:\t External Foreground")
                case 1:
                    print("Rom type:\t Background")
                case 2:
                    print("Rom type:\t Extension Foreground")
                case 0x80:
                    print("Rom type:\t Internal, eg BASIC")
                case _:
                    print("Rom type:\t Unknown, id=",hex(value))
            #print("\n")
        if (loc==0x0001) and (commandonly==0):
            version=version+chr(versioncheck(value)+48)+"."
        if (loc==0x0002) and (commandonly==0):
            version=version+chr(versioncheck(value)+48)
        if (loc==0x0003) and (commandonly==0):
            version=version+chr(versioncheck(value)+48)
            print ("Version:\t",version)
        if (loc==0x0004):
            addrl=value
            #print(hex(value))
        if (loc==0x0005):
            addrh=value
            rsx=((addrh*256)+addrl)-0xc000
        if (loc>=rsx) and (cmdend==-1):
            command=command+parsebyte(value)
            if value==0:
                #End of RSX table, set a flag
                cmdend=0
            if ((value>0) and (value<32)):
                #If its a low value, its a hidden command. Set a flag
                hiddencmd=1
            if value>127:
                # If its greater than &7F it's then end of a RSX command, so parse it.
                if (value-128)<32:
                    #If the converted value is <32 its a hidden command
                    hiddencmd=1
                if romname==1:
                    #First part of the RSX table is actually the ROM name.
                    if (commandonly==0):
                        print ("Rom Name:\t",command,"\n\nCommands:")
                    romname=0 #We only ever do this once.
                    command=""
                    hiddencmd=0
                else:
                    #Otherwise we print what we decoded.
                    if (hiddencmd==1):
                        #If hidden, highlight that.
                        print(" Hidden Command:",command)
                    else:
                        print (" "+command)
                    #reset our flags for the next command, and reset the string.
                    command=""
                    hiddencmd=0
        loc = loc + 1

cmds=(addrh*256)+addrl
#print(hex(cmds))
