#!/usr/bin/env python3

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
    print ("-w or --wiki - output the commands in a wikitable format, suitable for pasting into a wiki")
    quit()
    return

def graduaterom(gradrom):
    # Special section, just to decode Graduate CP/M accessory ROMs
    # - The first 0x10 bytes are a name (must start with "G")
    # - From 0x11 to a $ sign is the second part of the name.
    # - From the $ sign to 0x30 is version details
    # From 0x100 to 0x200 is the list of apps within the ROM.
    # This consists of an array of 0x10 bytes consisting of:
    # - Bytes 0 to 8 - Program Name.
    # - Bytes 8 to 0x10 - Progam details for rom (not used here)
    #
    loc=0
    appcounter=0
    romvalue=""
    appname=""
    namedone=0
    verdone=0
    with open(gradrom, "rb") as g:
        #print("Reading from: "+src)
        while (gradbyte := g.read(1)):
            loc=loc+1
            value=int.from_bytes(gradbyte,"little")
            if namedone==0 and value==ord('$'):
                #Split the string in two parts.
                if commandonly==0:
                    print("Name:\t ",romvalue[0:0x10])
                    print("\t ",romvalue[0x10:0x99])
                namedone=1
                romvalue=""
            elif verdone==0 and value==0:
                #Version info
                if commandonly==0:
                    print("Version: ",romvalue)
                verdone=1
            elif loc>0xff and loc<0x200:
                # Rom APP details section.
                if loc==0x100:
                    #start of Apps list. Initialise some stuff
                    romvalue=""
                    appcounter=0
                    if commandonly==0:
                        print("Apps:")
                    for files in range(0,0x10,1):
                        #The program name - the bit we care about.
                        name=""
                        for nameloc in range(0,9,1):
                            gradbyte = g.read(1)
                            value=int.from_bytes(gradbyte,"little")
                            if value != 0xff:
                                name=name+parsebyte(value)
                        if name != "":
                            print(name)
                        for nameloc in range(9,0x10,1):
                            #just discard the rest of the section, so we can get the next filename
                            gradbyte = g.read(1)
            else:
                if value>31: #skip any cr/lf
                    romvalue=romvalue+parsebyte(value)
    g.close()

    return

argc = len(sys.argv)

#-------------------------
loc = 0
commandonly=0 #Don't print versions etc, only commands
myversion="v2.50"
addrl=0
addrh=0
rsx=0xffff
cmdend=-1 #flag when we reached the end of the commands
hiddencmd=0 #flag for hidden commands
wiki=0 #flag for wiki output
wikitable=0 #table for wikitable format
wikispace=""
romname=1 #flag for the rom name (it looks like an RSX command, but its not.)
command="" #string used when building commands from the ROM
version="" #string used when decoding the ROM version details
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
    elif (sys.argv[param] =="-w") or (sys.argv[param]=="--wiki"):
        wiki=1
        wikispace=" " #Add a space for formatting
    else:
        src = sys.argv[param]
        sourceset=1

#Make sure we have a source or we error out
if sourceset==-1:
    print("Error: You must specify a source rom filename")
    quit()

print ("Rom Details:")

#Scan the source rom
with open(src, "rb") as f:
    #print("Reading from: "+src)
    while (byte := f.read(1)):
        value=int.from_bytes(byte,"little")
        if (loc==0x0000) and (commandonly==0):
            match value:
                case 0:
                    print(wikispace+"Rom type:\t External Foreground")
                case 1:
                    print(wikispace+"Rom type:\t Background")
                case 2:
                    print(wikispace+"Rom type:\t Extension Foreground")
                case 0x80:
                    print(wikispace+"Rom type:\t Internal, eg BASIC")
                case 0x47:
                    print(wikispace+"Rom type: Graduate Software CP/M Accessory ROM")
                    loc=0x4000 #this will skip processing the rest of this data as a normal rom
                    f.close()
                    graduaterom(src)
                    exit(0)
                case _:
                    print("Rom type:\t Unknown, id=",hex(value))
        if (loc==0x0000) and value==0x47 and commandonly==1:
            #handle special case ROM with commandonly enabled
            f.close()
            graduaterom(src)
            exit(0)

        if (loc==0x0001) and (commandonly==0):
            version=version+chr(versioncheck(value)+48)+"."
        if (loc==0x0002) and (commandonly==0):
            version=version+chr(versioncheck(value)+48)
        if (loc==0x0003) and (commandonly==0):
            version=version+chr(versioncheck(value)+48)
            print (wikispace+"Version:\t",version)
        if (loc==0x0004):
            addrl=value
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
                        print (wikispace+"Rom Name:\t",command,"\n\nCommands:")
                    romname=0 #We only ever do this once.
                    command=""
                    hiddencmd=0
                else:
                    #Otherwise we print what we decoded.
                    if (hiddencmd==1):
                        if wiki==1:
                            if wikitable==0:
                                print("{|\n|-\n! Command !! Description")
                                wikitable=1
                            print ("|-\n| Hidden Command: "+command+"||")
                        else:
                            #If hidden, highlight that.
                            print(" Hidden Command:",command)
                    else:
                        if wiki==1:
                            if wikitable==0:
                                print("{|\n|-\n! Command !! Description")
                                wikitable=1
                            print ("|-\n|"+command+"||")
                        else:
                            print (" "+command)
                    #reset our flags for the next command, and reset the string.
                    command=""
                    hiddencmd=0
        loc = loc + 1
f.close()
if wiki==1:
    print ("|}")
