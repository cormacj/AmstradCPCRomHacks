#!/usr/bin/env python3
# Copyright (c) 2024,2025 Cormac McGaughey
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

# This progam is designed to decode Amstrad ROMs and display details and commands from those.


# TODO:
# makeacc.py
# -r <new file> rebuild a rom option (eg replace an existing program with a newer one)

# Future Ideas:
# - Rebuild a ROM file (add new file, delete file?)

import sys
from datetime import datetime

now = datetime.now()  # current date and time

myversion = "1.50"
rom = bytearray()
comfiles = bytearray()
romloc = 0
total_size=15872 #Number of bytes that are available for .COM storage

# Generate a default ID for the rom
year = now.strftime("%Y")
month = now.strftime("%m")

# Some defaults
rom_id = "Grad ROM " + month + "/" + year
rom_name = "CP/M Test Rom"
rom_version = "$VER 0.02 "
romfile = ""

# This variable is the location of where the .COM files are stored in the ROM
filestart = 0xC200
comfiles = []


# ================================================================================
#                       Various functions and procedures
# ================================================================================
def extract(filename, list_of_files):
    # This procedure will extract files from a .ROM

    # First, all files in the ROM are upper case.
    # I'm converting the command line files passed to uppercase.
    list_of_UPPER_files = []
    for names in list_of_files:
        # Reformat the list of requested files, to upper case and strip off any extensions
        list_of_UPPER_files.append(names.upper().split(".")[0])

    romfile = bytearray()  # used for the source rom file
    comfile = bytearray()  # used for building .COM files
    print(f"Extracting files from: {filename}")

    # Now load the ROM into memory
    with open(filename, "rb") as binary_file:
        romfile = binary_file.read()
    binary_file.close()

    file_was_found = False
    # The list of files in a rom are stored between 0x100 and 0x200
    for files in range(0x100, 0x200, 0x10):
        name = ""
        # if a file slot is not used it's filled with 0xff, so if we find that, we'll ignore that slot
        if romfile[files] != 0xFF:
            # First 8 characters are the filename (without .COM)
            for loop in range(files, files + 8):
                name = name + chr(romfile[loop])
            name = name.strip()  # strip off all spaces.

            # If just -e was used - extract everything, or just handle the matched file
            if (name in list_of_UPPER_files) or list_of_files == []:
                file_was_found = True
                print(f'Found: "{name}"', end="")
                print(f' ... Writing: "{name}.COM"', end="")

                # Because its a ROM, the address in the com starts at 0xc000
                start = (romfile[files + 9] + (romfile[files + 10] * 0x100)) - 0xC000
                length = romfile[files + 11] + (romfile[files + 12] * 0x100)
                name = name + ".COM"
                # Now we have the start location and the length, copy it to the comfile array
                for loop in range(start, start + length):
                    comfile.append(romfile[loop])

                # Now write the .COM file
                with open(name, "wb") as binary_file:
                    binary_file.write(comfile)
                binary_file.close()
                comfile.clear()
                print(" ... Done!")
    if not file_was_found:
        err("\nError: The requested files were not found in the specified ROM\n")
    quit()


def err(text):
    # Print an error message and quit
    print(text)
    quit(1)


def validate_arguments(argslist):
    # Ensure that supplied arguments are valid
    global rom_id
    global rom_name
    global rom_version
    global romfile

    if argslist.debug:  # pragma: no cover
        print("--- debug output ---")
        print(f"  {argslist=}")
        # print(f' {argslist.filename=}')
        # print(f'  {args.goodbye=}, {args.name=}')
        print("")

    for param in argslist.ROMfile:
        tmp = param.upper()
        if tmp.endswith(".COM"):
            err(
                "Error! Destination ROM filename ends with '.COM'!\n Did you forget to include the ROM filename?"
            )
        else:
            romfile = param
            if argslist.debug:
                print("Destination filename was updated to", param)

    for param in argslist.COMfiles:
        tmp = param.upper()
        if not tmp.endswith(".COM"):
            err("Error! Filename does not end with '.COM'!")
        # else:
        #     romfile=param
        #     if argslist.debug:
        #         print(".com filename was ",param)

    for param in argslist.id:
        if len(param) > 16:
            err(
                f"Error! ROM id is too long - maximum size is 16 characters. You used {len(param)} characters"
            )
        elif not param.startswith("G"):
            print(
                "The ROM id must start with 'G' otherwise the CP/M rom will not recognize it!"
            )
            quit(1)
        else:
            rom_id = param.ljust(16)  # Pad it to fit
            if argslist.debug:
                print("rom_id was updated to", rom_id)

    for param in argslist.romversion:
        if len(param) > 16:
            err(
                f"Error! ROM version is too long - maximum size is 16 characters. You used {len(param)} characters"
            )
        # elif not param.startswith("G"):
        #     print("The ROM id must start with 'G' otherwise the CP/M rom will not recognize it!")
        #     quit(1)
        else:
            rom_version = param  # .ljust(16) #Pad it to fit
            if argslist.debug:
                print("rom_version was updated to", rom_version)

    # If no description was requested, I'll generate it for you from filenames
    if argslist.name is None:
        temp = ""
        for temp_filename in argslist.COMfiles:
            if temp_filename != "":
                temp = temp + " " + temp_filename
            # Now just limit it to what the ROM will display
            rom_name = temp[1:22]
        if argslist.debug:
            print(f'rom_name was generated to "{rom_name}"')
    else:
        for param in argslist.name:
            if len(param) > 22:
                err(
                    f"Error! ROM name is too long- maximum size is 22 characters. You used {len(param)} characters"
                )
            else:
                rom_name = param  # .ljust(22)
                if argslist.debug:
                    print("rom_name was updated to", rom_name)


def parse_arguments():
    # Build out the parameter list.
    # There is a lot here so I'm using ArgumentParser

    global rom_id
    global rom_name
    global version
    global romfile

    import argparse

    # Initialize parser
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="This is a utility to build accessory ROMs for Amstrad Graduate Software CP/M ROMs",
        epilog=f"""Note: -e can only be used by itself and not with any other argument.\n
Examples:
  To recreate the original accessory rom:
    {sys.argv[0]} CPM_ACC1.ROM NSWEEP.COM FORMAT.COM PCW.COM RUN.COM UNERA.COM D.COM -i "Graduate (C)1988" -n "CP/M Accessory Rom 1" -v "VER 2.30 "

  Extract PCW.COM from CPM_ACC1.ROM:
    {sys.argv[0]} CPM_ACC1.ROM -e PCW

""",
    )

    myname = sys.argv[0]
    print(myname, " - version ", myversion, "\n")
    print("")
    group0 = parser.add_argument_group("Required", "A name for a ROM file is required")
    group1 = parser.add_argument_group(
        "Building", "These options relate to building a ROM"
    )
    group2 = parser.add_argument_group(
        "Extracting", "These options relate to extracting files from a ROM"
    )
    group0.add_argument(
        "ROMfile",
        type=str,
        default="",
        metavar="ROM_filename",
        nargs=1,
        help="This is the name of the ROM file that you are creating.",
    )

    group1.add_argument(
        "COMfiles",
        type=str,
        default="",
        metavar=".COM_file",
        nargs="*",
        help="This must be a CP/M program.",
    )

    group1.add_argument(
        "-i",
        "--id",
        nargs=1,
        default="",
        metavar='"ROM ID String"',
        help="ROM Identification. It must start with G, and be no more than 16 characters. The default is "
        + chr(34)
        + rom_id
        + chr(34),
    )

    group1.add_argument(
        "-n",
        "--name",
        nargs=1,
        metavar='"ROM Description"',
        help="This is the name that will be shown in commands such as |OHELP or romcat. It must be no more than 32 characters.",
    )

    group1.add_argument(
        "-v",
        "--romversion",
        nargs=1,
        default=["V1.00"],
        metavar='"ROM Version string"',
        help="This is a string that will dictate the version of the rom.",
    )

    group2.add_argument(
        "-e",
        "--extract",
        nargs="*",
        metavar="filename, or blank for all files",
        help="Extract files from a ROM.",
    )

    parser.add_argument("-d", "--debug", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args()
    return args  # paramaterize everything


def initialse_rom():
    # This fills the rom space with zeroes
    print("\nPreparing ROM Space...", end="")

    for loop in range(romloc, 0x4000):
        rom.append(0)
    # Now the whole ROM is one big byte array.
    #  romloc will be our index of record

    print(" Done!")


def dbg(arg):
    # debug, just print something
    print(arg)


def add_null_file():
    # Used when a file isn't used for a slot
    # It's just all 0xff
    for loop in range(0, 0x10):
        push_byte_to_rom(0xFF)


def add_file(filename):
    # Generate an entry for a file being added
    # Format:
    # Offset (Hex) 	Count 	Description
    # 0 	8 	Filename (padded with spaces to fill out)
    # 8 	1 	another space
    # 9 	2 	address in ROM for start of data for file (rom at 0xc000, data for files starts at 0xc200)
    # 11 	2 	length in bytes of file
    # 13 	1 	length of filename in chars (excluding padding)
    # 14 	2   &feff (terminator)

    global filestart
    global comfiles
    global total_size

    # s = romloc

    fn = filename
    file_data = bytearray()
    with open(fn, "rb") as binary_file:
        file_data = binary_file.read()
    binary_file.close()
    file_size = len(file_data)
    fn_padded = fn.split(".")[0]  # Just the filename (no extension)
    fn_padded = fn_padded.upper()[
        0:9
    ]  # because modern OSs can have long files, CP/M wont, so chop it down.
    fn_padded = fn_padded.ljust(9)
    name_length = len(fn.split(".")[0])
    total_size = total_size - file_size

    # Be informational
    print(f"  Adding: {filename} as {fn_padded} ({file_size} bytes, {total_size} bytes remaining)")

    # Add the various things to the ROM
    push_string_to_rom(fn_padded)  # filename, padded with spaces
    push_word_to_rom(filestart)  # Where the file starts in the ROM
    push_word_to_rom(file_size)  # size of the file
    push_byte_to_rom(name_length)  # length of filename (without .COM or padding)
    push_word_to_rom(0xFEFF)  # terminator

    # add the file to the comfiles byte array
    # this bytearray is seperate from the rom at this time.
    # It'll be combined later
    for loop in file_data:
        comfiles.append(loop)
    # ...and update the start location for use with the next file
    filestart = filestart + len(file_data)


def push_word_to_rom(romdata: int):
    # push two bytes to the rom
    global romloc
    global rom

    # Convert the word to a little endian byte array
    b = bytearray()
    b = romdata.to_bytes(2, "little")

    # Now push these bytes into the ROM
    push_byte_to_rom(b[0])
    push_byte_to_rom(b[1])


def push_byte_to_rom(romdata: bytes):
    # push a byte to the rom
    # This is used by everything
    global romloc
    global rom
    # Now update the ROM
    rom[romloc] = romdata
    # Increment our location counter
    romloc = romloc + 1


def push_string_to_rom(str_data):
    # Push a string into the rom (as bytes)
    global romloc
    global rom

    # Convert the string to bytes
    str_bytes = str.encode(str_data)  # encode the string as bytes
    # Now push the bytes into the ROM
    for c in str_bytes:
        push_byte_to_rom(c)
        # rom.append(c)
    # romloc=romloc+len(str_data)


# ================================================================================
#   End of Functions/Procedures
# ================================================================================

# First, lets get our parameters sorted out:
args = parse_arguments()

# Now check the command line arguments to make sure they are valid
validate_arguments(args)

# If -e was used, we'll go do that and ignore everything else.
if args.extract is not None:
    extract(args.ROMfile[0], args.extract)

# Now... lets allocate the whole rom space, setting it all to zero
initialse_rom()

# Start of ROM
romloc = 0
push_string_to_rom(rom_id)  # Needs to start with a G to be recognised
push_string_to_rom(rom_name)  # This can be anything
push_byte_to_rom(10)  # Most of the roms have a LF/CR here, so I'll doing that too
push_byte_to_rom(13)
push_byte_to_rom(ord("$"))
push_string_to_rom(rom_version)  # The version string

# The ROM has a 0xC9 at 0x38, but we padded that with zero, so update that location.
romloc = 0x38
push_byte_to_rom(0xC9)

# This is the ROM initialization code (see seperate disassmbly)
romloc = 0x70  # Enforce the code location (it must start here)
code_array = [
    0x32,
    0xBE,
    0x3F,
    0xE5,
    0xDD,
    0xE1,
    0x2A,
    0xFE,
    0xFB,
    0x11,
    0x34,
    0x0,
    0x19,
    0x11,
    0x8C,
    0x3F,
    0x73,
    0x23,
    0x72,
    0x2A,
    0xFE,
    0xFB,
    0x11,
    0x10,
    0x0,
    0xE,
    0x3B,
    0xE9,
    0xDD,
    0x6E,
    0x0,
    0xDD,
    0x66,
    0x1,
    0xDD,
    0x4E,
    0x2,
    0xDD,
    0x46,
    0x3,
    0x11,
    0x0,
    0x1,
    0xCD,
    0xBF,
    0x3F,
    0x12,
    0x13,
    0x23,
    0xB,
    0x79,
    0xB0,
    0x20,
    0xF5,
    0x1E,
    0xFF,
    0xE,
    0x2D,
    0xCD,
    0x5,
    0x0,
    0x3A,
    0xAF,
    0xFB,
    0x5F,
    0xE,
    0xE,
    0xCD,
    0x5,
    0x0,
    0x1E,
    0x0,
    0xE,
    0x2D,
    0xCD,
    0x5,
    0x0,
    0xC9,
    0x0,
    0xC5,
    0x3A,
    0xBE,
    0x3F,
    0x4F,
    0xCD,
    0xC9,
    0x3F,
    0xC1,
    0xC9,
    0xF3,
    0xC5,
    0xD9,
    0xCB,
    0x99,
    0xED,
    0x49,
    0xD9,
    0x6,
    0xDF,
    0xED,
    0x49,
    0x7E,
    0xD9,
    0xCB,
    0xD9,
    0xED,
    0x49,
    0xD9,
    0xFB,
    0xC1,
    0xC9,
    0xED,
    0x49,
    0xD9,
    0x6,
    0xDF,
    0xED,
    0x49,
    0x7E,
    0xD9,
    0xCB,
    0xD9,
    0xED,
    0x49,
    0xD9,
    0xFB,
    0xC1,
    0xC9,
]


# Now add that code to the ROM
for loop in code_array:
    push_byte_to_rom(loop)

romloc = 0x100  # Filenames and details are at location 0x100
numfiles = 0
for com_file in args.COMfiles:
    add_file(com_file)
    numfiles = numfiles + 1
    if total_size <0: #FFFF:
        err("\nError: Too many files, or file is too large to be added to a ROM")
        exit(1)

# Now pad out the rest of the file slots with 0xff
for unused in range(numfiles, 0x16):
    add_null_file()

# Now push all the .COM files into the ROM
romloc = 0x200
for loop in comfiles:
    push_byte_to_rom(loop)

# How much space did we have left?
print("\nThere are ", 0x4000 - romloc, " bytes remaining.")

# Write the rom to file
if romfile != "":
    with open(romfile, "wb") as binary_file:
        binary_file.write(rom)
    binary_file.close()
    print("\nROM file successfully created!")
else:
    print("Unable to write ROM file - no filename specified!")
    quit(1)
quit()
