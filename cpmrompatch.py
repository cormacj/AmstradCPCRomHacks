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


#1ff0: (C)1988 GRADUATE SOFTWARE

#xor: 0x4e
#3f00-3f17: name
#3f19-3f5f: address
#3f71-3f7d: serial

#xor: 0xaa
#3f87: password length(?)
#3f88-3fff: password

import sys

# function definition
def xorcrypt(data,xorval):
    result=""
    for element in range(0, len(data)):
        result=result+chr(ord(element)^xorval)
    return result

argc = len(sys.argv)
# print(argc)
# print(sys.argv[1])
# print(sys.argv[2])
# print(sys.argv[3])

loc = 0
name =""
address = ""
serial = ""
pwlength = 0
password = ""
copyright = ""

#Blank the parameters, just in case
newname = ""
newname_crypt = ""

newpw = ""
newpw_crypt = ""

newaddress = ""
newaddress_crypt = ""

newserial = ""
newserial_crypt = ""

src=""
dest=""

#Mark parameters as unset for later sanity checks
display=-1
setpw=-1
setname=-1
setaddr=-1
sourceset=-1
destset=-1

if argc <= 1:
    print ("Usage: cpmrompatch.py romfile.rom <xor hex value>\nExample: dum.py CPM1.rom 0x4e") #TODO: update this
    quit()
values=range(argc)

#xor: 0x4e
#3f00-3f17: name
#3f19-3f5f: address
#3f71-3f7d: serial

#xor: 0xaa
#3f87: password length(?)
#3f88-3fff: password

#Process the command line parameters
for param in values:
    if sys.argv[param] == "--display":
        display=1
    elif sys.argv[param] == "--password":
        setpw=1 #enable password setting
        newpw=sys.argv[param+1] #grab Password
        newpw_crypt=xorcrypt(newpw,0xaa)
        pwlength=len(newpw)
    elif sys.argv[param] == "--name":
        setname=1
        newname=sys.argv[param+1]
        newname_crypt=xorcrypt(newname,0x4e)
    elif sys.argv[param] == "--address":
        setaddr=1
        newaddress=sys.argv[param+1]
        newaddress_crypt=xorcrypt(newaddress,0x4e)
    elif sys.argv[param] == "--serial":
        newserial=[param+1]
        newserial_crypt=xorcrypt(serial,0x4e)
    elif sys.argv[param] == "--src":
        src = sys.argv[param+1]
        sourceset=1
    elif sys.argv[param] == "--dest":
        dest = sys.argv[param+1]
        destset=1

#Make sure we have a source or we error out
if sourceset==-1:
    print("Error: You must specify a source rom name using --src, eg --src CPM1.rom")
    quit()

#Scan the source rom
with open(src, "rb") as f:
    print("Reading from: "+src)
    while (byte := f.read(1)):
        # Do stuff with byte.
        #print(loc%64)
        #print(".",end='')
        value=int.from_bytes(byte,"little")
        #value=value^0xaa #password
        #value=value^0x4e #name etc


        #1ff0: (C)1988 GRADUATE SOFTWARE

        #xor: 0x4e
        #3f00-3f17: name
        #3f19-3f5f: address
        #3f71-3f7d: serial

        #xor: 0xaa
        #3f87: password length(?)
        #3f88-3fff: password
        if (loc>=0x1ff0) and (loc<=0x2009):
            char=value^0x00
            if char>31 and char<127:
                copyright=copyright+chr(char)
        if (loc>=0x3f00) and (loc<=0x3f16):
            char=value^0x4e
            if char>31 and char<127:
                name=name+chr(char)
        if (loc>0x3f19) and (loc<0x3f60):
            char=value^0x4e
            if char>31 and char<127:
                address=address+chr(char)
        if (loc>0x3f71) and (loc<0x3f7d):
            char=value^0x4e
            if char>31 and char<127:
                serial=serial+chr(char)
        if (loc==0x3f87):
            char=value^0xaa
            pwlength=int(char)
        if (loc>=0x3f88) and (loc<0x3fff):
            char=value^0xaa
            if char>31 and char<127:
                password=password+chr(char)
        loc = loc + 1

    #Validate if its a Graduate software rom, because it needs to be that
    if copyright!="(C)1988 GRADUATE SOFTWARE.":
        print("Error: This is not a Graduate CPM+ ROM #1")
        quit()

if display==1:
    print("\nCopyright: "+copyright)
    print("Serial:   "+serial)
    print("Name:     "+name)
    print("Address:  "+address)
    #print("Password length: ",pwlength)
    print("Password: "+password+" ("+str(pwlength)+" characters)")

#We're going to update somethings
elif (setpw==1 or setname==1 or setaddr==1 or sourceset==1):
    #We're going to be updating things, make sure we know where we're writing to
    if destset==-1:
        print("Error: You must specify a destination ROM file using --dest, eg --dest NEWROM.rom")
        quit()
    #And make sure we are'nt overwriting our source
    if src==dest:
        print("Error: You cannot have the same file for source and destination.")
        quit()
