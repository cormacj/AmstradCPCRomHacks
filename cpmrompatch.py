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


# This program is designed to patch the Graduate software CPM+ rom for Amstrad CPC systems
# This was written has a quick hack and I really need to refactor it along the lines of what
# I did for the accessory rom builder and pull it all into ram, patch it and write it out.

import sys


# function definition
def xorcrypt(data, xorval, padlevel):
    result = ""
    for element in range(0, len(data)):
        result = result + chr(ord(data[element]) ^ xorval)
    # pad the rest with zeroes
    for pad in range(len(data) + 1, padlevel):
        result = result + chr(0 ^ xorval)  # pad out with zeroes
    result = bytes(result, "latin-1")
    return result


def validate(what, srcstring, length):
    if len(srcstring) > length:
        print(
            "Error: " + what + " is too long. Maximum characters is",
            length,
            " Currently it's at ",
            len(srcstring),
            "characters.",
        )
        quit()
    return


def dumphelp():
    print("Usage:")
    print("To display the details of what is stored in the ROM:")
    print("  cpmrompatch.py --src SourceROM.rom --display\n")
    print(
        "To update the ROM, you must specify --src and --dest and one of the following:"
    )
    print("  cpmrompatch.py --src SourceROM.rom --dest DestROM.rom")
    print(
        "    --quiet - Disable the noisy, large default ROM boot message and replace it with a short version"
    )
    print('    --name "<Name>" - Sets the name of the ROM owner')
    print('    --address "<Address>" - Sets the address of the ROM owner')
    print("    --serial <serial number> - Sets the serial number of the ROM")
    print("    --password <password> - Sets the password for |PASSWORD\n")
    print(
        "You can also just pass a filename and it will display the details for that ROM"
    )
    print("  eg cpmrompatch.py CPM1.ROM\n")
    print("Examples:")
    print(
        '   cpmrompatch.py --src CPM1.rom --dest CPM1-updated.rom --name "John Smith" --address "123 Acacia Ave, Sometown"'
    )
    print("   cpmrompatch.py --src CPM1.rom --dest CPM1-updated.rom --quiet")
    print("\n")
    quit()
    return


argc = len(sys.argv)

if argc == 1:
    dumphelp()

loc = 0
name = ""
address = ""
serial = ""
pwlength = 0
password = ""
copyright = ""

# Blank the parameters, just in case
newname = ""
newname_crypt = ""

newpw = ""
newpw_crypt = ""
newpwlen_crypt = 0

newaddress = ""
newaddress_crypt = ""

newserial = ""
newserial_crypt = ""

src = ""
dest = ""

# Mark parameters as unset for later sanity checks
display = -1
setpw = -1
setname = -1
setaddr = -1
sourceset = -1
setserial = -1
destset = -1
quietpatch = -1

# So.. this is basically a glorified patch file.
# These changes turn off all the graduate software noise and id and colours.
# It just makes it print a single string reading:
# "Graduate Software - CP/M+ loader."
# Define an array the length of the rom
patchfile = bytearray(16384)

# First make everything invalid
for loop in range(len(patchfile)):
    patchfile[loop] = 0xFF

# Now update the array with the needed changes.
patchfile[0xBE] = 0x0
patchfile[0xC2] = 0x0
patchfile[0xC3] = 0x0
patchfile[0xC4] = 0x0
patchfile[0xCE] = 0x0
patchfile[0xCF] = 0x0
patchfile[0xD0] = 0x0
patchfile[0x19B] = 0xD
patchfile[0x19C] = 0xA
patchfile[0x19D] = 0x20
patchfile[0x19E] = 0x47
patchfile[0x19F] = 0x72
patchfile[0x1A0] = 0x61
patchfile[0x1A1] = 0x64
patchfile[0x1A2] = 0x75
patchfile[0x1A4] = 0x74
patchfile[0x1A5] = 0x65
patchfile[0x1A6] = 0x20
patchfile[0x1A7] = 0x53
patchfile[0x1A8] = 0x6F
patchfile[0x1A9] = 0x66
patchfile[0x1AA] = 0x74
patchfile[0x1AB] = 0x77
patchfile[0x1AC] = 0x61
patchfile[0x1AD] = 0x72
patchfile[0x1AE] = 0x65
patchfile[0x1AF] = 0x20
patchfile[0x1B0] = 0x2D
patchfile[0x1B1] = 0x20
patchfile[0x1B2] = 0x43
patchfile[0x1B3] = 0x50
patchfile[0x1B4] = 0x2F
patchfile[0x1B5] = 0x4D
patchfile[0x1B6] = 0x2B
patchfile[0x1B7] = 0x20
patchfile[0x1B8] = 0x6C
patchfile[0x1B9] = 0x6F
patchfile[0x1BA] = 0x61
patchfile[0x1BB] = 0x64
patchfile[0x1BC] = 0x65
patchfile[0x1BD] = 0x72
patchfile[0x1BE] = 0xC9
patchfile[0x1C1] = 0xC9

values = range(argc)

# Process the command line parameters
for param in values:
    if sys.argv[param] == "--display":
        display = 1
    elif (sys.argv[param] == "-h") or (sys.argv[param] == "--help"):
        dumphelp()
    elif sys.argv[param] == "--quiet":
        print("Updating the ROM boot message to:")
        print(" Graduate Software - CP/M+ loader.")
        quietpatch = 1
        display = 0
    elif sys.argv[param] == "--password":
        setpw = 1  # enable password setting
        newpw = sys.argv[param + 1]  # grab Password
        newpwlen_crypt = len(newpw) ^ 0xAA
        newpw_crypt = xorcrypt(
            newpw, 0xAA, 17
        )  # adding an extra byte to padding because it throws off the rom size otherwise
        validate("password", newpw, 16)
        print("Updating password to:", newpw)
    elif sys.argv[param] == "--name":
        setname = 1
        newname = sys.argv[param + 1]
        newname_crypt = xorcrypt(newname, 0x4E, 24)
        validate("name", newname, 24)
    elif sys.argv[param] == "--address":
        setaddr = 1
        newaddress = sys.argv[param + 1]
        newaddress_crypt = xorcrypt(newaddress, 0x4E, 68)
        validate("address", newaddress, 68)
    elif sys.argv[param] == "--serial":
        setserial = 1
        newserial = sys.argv[param + 1]
        newserial_crypt = xorcrypt(newserial, 0x4E, 12)
        validate("serial", newserial, 12)
    elif sys.argv[param] == "--src":
        src = sys.argv[param + 1]
        sourceset = 1
    elif sys.argv[param] == "--dest":
        dest = sys.argv[param + 1]
        destset = 1

# If no parameters then, we'll assume it was just a filename that was passed, so we switch to display detail mode
if sourceset == -1:
    # OK, so if there is no --src, we're going to assume that param 1 is the filename and we're
    # just doing to do a display details eg same as --src fn.rom --display
    src = sys.argv[1]
    sourceset = 1
    display = 1

# Scan the source rom
with open(src, "rb") as f:
    # print("Reading from: "+src)
    while byte := f.read(1):
        value = int.from_bytes(byte, "little")
        if (loc >= 0x1FF0) and (loc <= 0x2009):
            char = value ^ 0x00
            if char > 31 and char < 127:
                copyright = copyright + chr(char)
        if (loc >= 0x3F00) and (loc <= 0x3F16):
            char = value ^ 0x4E
            if char > 31 and char < 127:
                name = name + chr(char)
        if (loc > 0x3F19) and (loc < 0x3F5E):
            char = value ^ 0x4E
            if char > 31 and char < 127:
                address = address + chr(char)
        if (loc > 0x3F70) and (loc < 0x3F7D):
            char = value ^ 0x4E
            if char > 31 and char < 127:
                serial = serial + chr(char)
        if loc == 0x3F87:
            char = value ^ 0xAA
            pwlength = int(char)
        if (loc >= 0x3F88) and (loc < 0x3FFF):
            char = value ^ 0xAA
            if char > 31 and char < 127:
                password = password + chr(char)
        loc = loc + 1

    # Validate if its a Graduate software rom, because it needs to be that
    if copyright != "(C)1988 GRADUATE SOFTWARE.":
        print("Error: This is not a Graduate CPM+ ROM #1")
        quit()

if display == 1:
    print("\nCopyright: " + copyright)
    print("Serial:   " + serial)
    print("Name:     " + name)
    print("Address:  " + address)
    # print("Password length: ",pwlength)
    print("Password: " + password + " (" + str(pwlength) + " characters)\n")

# We're going to update some things
elif setpw == 1 or setname == 1 or setaddr == 1 or sourceset == 1 or quietpatch == 1:
    # We're going to be updating things, make sure we know where we're writing to
    if destset == -1:
        print(
            "Error: You must specify a destination ROM file using --dest, eg --dest NEWROM.rom"
        )
        quit()
    # And make sure we are'nt overwriting our source
    if src == dest:
        print("Error: You cannot have the same file for source and destination.")
        quit()

    # start copying the ROM
    loc = 0
    destfile = open(dest, "wb")
    with open(src, "rb") as srcfile:
        # print("Reading from: "+src)
        while byte := srcfile.read(1):
            if patchfile[loc] != 0xFF:
                if loc == 0xBE:
                    print("Patching boot message: ", end="")
                elif loc < 0x1C1:
                    print(".", end="")
                else:
                    print(". done!")

                # print(f'{patchfile[loc]} ',end="")
                byte = patchfile[loc].to_bytes(1, "little")
            if (loc >= 0x3F00) and (loc <= 0x3F16) and (setname > -1):
                # Name, pad(16)
                if setname == 1:
                    print("Setting Name...")
                    destfile.write(newname_crypt)
                setname = 0  # don't need to rewrite, 0=written
            elif (loc > 0x3F19) and (loc < 0x3F5D) and (setaddr > -1):
                if setaddr == 1:
                    print("Setting Address...")
                    destfile.write(newaddress_crypt)
                setaddr = 0
            elif (loc > 0x3F70) and (loc < 0x3F7D) and (setserial > -1):
                if setserial == 1:
                    print("Setting Serial Number...")
                    destfile.write(newserial_crypt)
                setserial = 0
            elif (loc == 0x3F87) and (setpw > -1):
                num = newpwlen_crypt.to_bytes(1, byteorder="big")
                destfile.write(bytes(num))
            elif (loc >= 0x3F88) and (loc < 0x3F98) and (setpw > -1):
                if setpw == 1:
                    print("Setting Password...")
                    for loop in range(0, len(newpw_crypt)):
                        num = newpw_crypt[loop]
                        if num == 0xAA:
                            num = 0x4E
                        encbyte = num.to_bytes(1, byteorder="big")
                        destfile.write(encbyte)
                setpw = 0
            else:
                destfile.write(byte)

            loc = loc + 1
