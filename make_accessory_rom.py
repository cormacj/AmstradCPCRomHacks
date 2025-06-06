#!/usr/bin/env python3
# Requires python 3.6+

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
import os
import argparse
from datetime import datetime

# =================== CONSTANTS ===================
ROM_TOTAL_SIZE = 0x4000 # It's a 16k rom
COM_STORAGE_START = 0xC200 # Address in memory where the ROM files will be stored.
FILE_SLOT_START = 0x100 # Start of file slot descriptors
FILE_SLOT_END = 0x200 # End of file slot descriptors
FILE_SLOT_SIZE = 0x10 # Each descriptor is 16 bytes.
MAX_ROM_ID_LEN = 16
MAX_ROM_NAME_LEN = 22
MAX_ROM_VERSION_LEN = 16
MAX_FILES = 0x16 # Total 32 files
MY_VERSION = "2.01"

# =================== UTILITIES ===================
def error(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def pad_string(s, size):
    return s.ljust(size)[:size]

# =================== ROM BUILDER ===================
class ROMBuilder:
    def __init__(self, rom_id, rom_name, rom_version, romfile):
        self.rom = bytearray([0]*ROM_TOTAL_SIZE)
        self.comfiles = bytearray()
        self.romloc = 0
        self.filestart = COM_STORAGE_START
        self.total_size = 15872 # Total binary storage available for files.
        self.rom_id = pad_string(rom_id, MAX_ROM_ID_LEN)
        self.rom_name = rom_name #Do not pad
        self.rom_version = rom_version #Do not pad
        self.romfile = romfile
        self.numfiles = 0

    def push_byte(self, b):
        # Store a single byte
        self.rom[self.romloc] = b
        self.romloc += 1

    def push_word(self, w):
        # Store a word in little endian, eg 0x12AC is stored as 0xAC, 0x12
        self.push_byte(w & 0xFF)
        self.push_byte((w >> 8) & 0xFF)

    def push_string(self, s):
        # Store a string in binary
        for b in s.encode():
            self.push_byte(b)

    def add_null_filename(self):
        # Fill with blanks
        for _ in range(FILE_SLOT_SIZE):
            self.push_byte(0xFF)

    def add_file(self, filename):
        try:
            with open(filename, "rb") as f:
                data = f.read()

        except FileNotFoundError:
            print(f'\n *** ERROR: {filename} was not found.')
            exit(1)
        except Exception as e:
           print(f'\n *** ERROR: Error accessing {filename}.')
           exit(1)

        file_size = len(data)
        basename = pad_string(filename.split(".")[0].upper(), 9)
        name_length = len(filename.split(".")[0])

        if self.total_size - file_size < 0:
            error("\nError: Too many files, or file is too large to be added to a ROM")

        print(f"  Adding: {filename} as {basename} ({file_size} bytes, {self.total_size-file_size} bytes remaining)")
        self.push_string(basename)
        self.push_word(self.filestart)
        self.push_word(file_size)
        self.push_byte(name_length)
        self.push_word(0xFEFF)

        self.comfiles.extend(data)
        self.filestart += file_size
        self.total_size -= file_size
        self.numfiles += 1

    def finalize(self, comfiles_list):
        # Header
        self.romloc = 0
        self.push_string(self.rom_id)
        self.push_string(self.rom_name)
        self.push_byte(10)
        self.push_byte(13)
        self.push_byte(ord("$"))
        self.push_string(self.rom_version)

        # Set 0xC9 at 0x38
        self.romloc = 0x38
        self.push_byte(0xC9)

        # ROM initialization code
        # This code is called to copy files into RAM etc
        self.romloc = 0x70
        code_array = [
            0x32,0xBE,0x3F,0xE5,0xDD,0xE1,0x2A,0xFE,0xFB,0x11,0x34,0x0,0x19,0x11,0x8C,0x3F,0x73,0x23,0x72,
            0x2A,0xFE,0xFB,0x11,0x10,0x0,0xE,0x3B,0xE9,0xDD,0x6E,0x0,0xDD,0x66,0x1,0xDD,0x4E,0x2,
            0xDD,0x46,0x3,0x11,0x0,0x1,0xCD,0xBF,0x3F,0x12,0x13,0x23,0xB,0x79,0xB0,0x20,0xF5,
            0x1E,0xFF,0xE,0x2D,0xCD,0x5,0x0,0x3A,0xAF,0xFB,0x5F,0xE,0xE,0xCD,0x5,0x0,0x1E,
            0x0,0xE,0x2D,0xCD,0x5,0x0,0xC9,0x0,0xC5,0x3A,0xBE,0x3F,0x4F,0xCD,0xC9,0x3F,0xC1,
            0xC9,0xF3,0xC5,0xD9,0xCB,0x99,0xED,0x49,0xD9,0x6,0xDF,0xED,0x49,0x7E,0xD9,0xCB,
            0xD9,0xED,0x49,0xD9,0xFB,0xC1,0xC9,0xED,0x49,0xD9,0x6,0xDF,0xED,0x49,0x7E,0xD9,
            0xCB,0xD9,0xED,0x49,0xD9,0xFB,0xC1,0xC9,
        ]
        for b in code_array:
            self.push_byte(b)

        # Add files
        self.romloc = FILE_SLOT_START
        # First fill the filename slots with the files we have...
        for com_file in comfiles_list:
            self.add_file(com_file)
        # ...and fill the rest of the slots with 0xFF
        for _ in range(self.numfiles, MAX_FILES):
            self.add_null_filename()

        # Add .COM file data
        self.romloc = FILE_SLOT_END
        for b in self.comfiles:
            self.push_byte(b)

        print("\nThere are", ROM_TOTAL_SIZE - self.romloc, "bytes remaining.")

        # Write the ROM to file
        if self.romfile:
            with open(self.romfile, "wb") as fout:
                fout.write(self.rom)
            print("\nROM file successfully created!")
        else:
            error("Unable to write ROM file - no filename specified!")

# =================== ARGUMENT PARSING ===================
def parse_args():
    now = datetime.now()
    default_id = f"Grad ROM {now.strftime('%m')}/{now.strftime('%Y')}"
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Build accessory ROMs for Amstrad Graduate Software CP/M ROMs',
        epilog=f"""\n
Examples:
  To recreate the original accessory rom:
    {sys.argv[0]} -i "Graduate (C)1988" -n "CP/M Accessory Rom 1" -v "VER 2.30" CPM_ACC1.ROM NSWEEP.COM FORMAT.COM PCW.COM RUN.COM UNERA.COM D.COM

  Extract PCW.COM from CPM_ACC1.ROM:
    {sys.argv[0]} CPM_ACC1.ROM -e PCW
""",
    )
    rom_create=parser.add_argument_group('Creating ROMs','make_accessory_rom.py [-h] [-i ID] [-n NAME] [-v ROMVERSION] ROMfile COMfile [COMfiles ...]')
    rom_extract=parser.add_argument_group('Extracting files from a ROM','usage: make_accessory_rom.py ROMFILE -e COMfile [COMfiles ...]')
    rom_create.add_argument("ROMfile", type=str, help="ROM file to create")
    rom_create.add_argument("COMfiles", type=str, nargs="*", help="CP/M .COM programs to add")
    rom_create.add_argument("-i", "--id", default=default_id, help=f"ROM id (max {MAX_ROM_ID_LEN})")
    rom_create.add_argument("-n", "--name", default="CP/M Test Rom", help=f"ROM name (max {MAX_ROM_NAME_LEN})")
    rom_create.add_argument("-v", "--romversion", default="$VER 0.02 ", help=f"ROM version (max {MAX_ROM_VERSION_LEN})")
    rom_extract.add_argument("-e", "--extract", nargs="+", metavar="COMfile",help="Extract files from ROM\n")
    parser.add_argument("-d", "--debug", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args()

# =================== FILE EXTRACTION ===================
def extract_files(filename, files):
    # Extract a .COM file from a ROM
    # First, read in the ROM file
    with open(filename, "rb") as f:
        rom = f.read()

    # Now, figure out where the binary data is within the ROM
    files_upper = [name.upper().split(".")[0] for name in files] if files else []
    found = False

    # Finally, dump the data out to a .COM file
    for i in range(FILE_SLOT_START, FILE_SLOT_END, FILE_SLOT_SIZE):
        if rom[i] != 0xFF:
            name = bytes(rom[i:i+8]).decode("ascii").strip()
            if not files or name in files_upper:
                found = True
                start = (rom[i+9] + (rom[i+10] << 8)) - 0xC000
                length = rom[i+11] + (rom[i+12] << 8)
                data = rom[start:start+length]
                fname = name + ".COM"
                with open(fname, "wb") as out:
                    out.write(data)
                print(f'Extracted "{fname}"')
    if not found:
        error("Error: Requested files not found in ROM.")

# =================== MAIN ===================
def main():
    print(f"{os.path.basename(__file__)} - version {MY_VERSION}\n")
    args = parse_args()

    # Extraction mode
    if args.extract is not None:
        extract_files(args.ROMfile, args.extract)
        return

    # Validate arguments
    if args.id and (len(args.id) > MAX_ROM_ID_LEN or not args.id.startswith("G")):
        error(f"ROM id must start with 'G' and be <= {MAX_ROM_ID_LEN} characters")
    if args.name and len(args.name) > MAX_ROM_NAME_LEN:
        error(f"ROM name too long (max {MAX_ROM_NAME_LEN})")
    if args.romversion and len(args.romversion) > MAX_ROM_VERSION_LEN:
        error(f"ROM version too long (max {MAX_ROM_VERSION_LEN})")
    if not args.COMfiles:
        error("At least one .COM file is required.")

    builder = ROMBuilder(args.id, args.name, args.romversion, args.ROMfile)
    builder.finalize(args.COMfiles)

if __name__ == "__main__":
    main()
