#!/usr/bin/env python3

# Copyright (c) 2023,2025 Cormac McGaughey
# Licensed under the GNU GPL v3.

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
import argparse
from pathlib import Path

ROM_SIZE = 16384
PATCH_OFFSETS = {
    0xBE: 0x0, 0xC2: 0x0, 0xC3: 0x0, 0xC4: 0x0, 0xCE: 0x0, 0xCF: 0x0,
    0xD0: 0x0, 0x19B: 0xD, 0x19C: 0xA, 0x19D: 0x20, 0x19E: 0x47, 0x19F: 0x72,
    0x1A0: 0x61, 0x1A1: 0x64, 0x1A2: 0x75, 0x1A4: 0x74, 0x1A5: 0x65, 0x1A6: 0x20,
    0x1A7: 0x53, 0x1A8: 0x6F, 0x1A9: 0x66, 0x1AA: 0x74, 0x1AB: 0x77, 0x1AC: 0x61,
    0x1AD: 0x72, 0x1AE: 0x65, 0x1AF: 0x20, 0x1B0: 0x2D, 0x1B1: 0x20, 0x1B2: 0x43,
    0x1B3: 0x50, 0x1B4: 0x2F, 0x1B5: 0x4D, 0x1B6: 0x2B, 0x1B7: 0x20, 0x1B8: 0x6C,
    0x1B9: 0x6F, 0x1BA: 0x61, 0x1BB: 0x64, 0x1BC: 0x65, 0x1BD: 0x72, 0x1BE: 0xC9,
    0x1C1: 0xC9
}

def xorcrypt(data, xorval, padlevel):
    result = bytearray([b ^ xorval for b in data.encode("latin-1")])
    result.extend([0 ^ xorval] * (padlevel - len(data)))
    return bytes(result)

def validate(field, value, maxlen):
    if len(value) > maxlen:
        raise ValueError(f"{field} is too long. Maximum is {maxlen} characters, got {len(value)}.")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Patch/display Graduate Software CPM+ ROMs for Amstrad CPC. Version 2.01"
    )
    parser.add_argument("--src", help="Source ROM file")
    parser.add_argument("--dest", help="Destination ROM file (for patching)")
    parser.add_argument("--display", action="store_true", help="Display ROM details")
    parser.add_argument("--quiet", action="store_true", help="Patch ROM to quiet boot")
    parser.add_argument("--name", help="Set ROM owner name (max 24 chars)")
    parser.add_argument("--address", help="Set ROM owner address (max 68 chars)")
    parser.add_argument("--serial", help="Set serial number (max 12 chars)")
    parser.add_argument("--password", help="Set password (max 48 chars)")
    parser.add_argument("filename", nargs="?", help="ROM file (display mode if no --src)")

    args = parser.parse_args()
    # For display mode with just a filename
    if not args.src and args.filename:
        args.src = args.filename
        args.display = True
    return args

def extract_fields(rom_bytes):
    # Extract copyright, name, address, serial and password as in original
    copyright = "".join(
        chr(rom_bytes[i] ^ 0x00)
        for i in range(0x1FF0, 0x200A)
        if 31 < (rom_bytes[i] ^ 0x00) < 127
    )
    name = "".join(
        chr(rom_bytes[i] ^ 0x4E)
        for i in range(0x3F00, 0x3F17)
        if 31 < (rom_bytes[i] ^ 0x4E) < 127
    )
    address = "".join(
        chr(rom_bytes[i] ^ 0x4E)
        for i in range(0x3F1A, 0x3F5E)
        if 31 < (rom_bytes[i] ^ 0x4E) < 127
    )
    serial = "".join(
        chr(rom_bytes[i] ^ 0x4E)
        for i in range(0x3F71, 0x3F7D)
        if 31 < (rom_bytes[i] ^ 0x4E) < 127
    )
    pwlength = rom_bytes[0x3F87] ^ 0xAA
    password = "".join(
        chr(rom_bytes[i] ^ 0xAA)
        for i in range(0x3F88, 0x3FFF)
        if 31 < (rom_bytes[i] ^ 0xAA) < 127
    )
    return copyright, name, address, serial, password, pwlength

def display_rom_info(rom_bytes):
    copyright, name, address, serial, password, pwlength = extract_fields(rom_bytes)
    if copyright != "(C)1988 GRADUATE SOFTWARE.":
        sys.exit("Error: This is not a Graduate CPM+ ROM #1")
    print(f"\nCopyright: {copyright}")
    print(f"Serial:   {serial}")
    print(f"Name:     {name}")
    print(f"Address:  {address}")
    print(f"Password: {password} ({pwlength} characters)\n")

def patch_rom(args, rom_bytes):
    # Patch the boot message if requested
    if args.quiet:
        for k, v in PATCH_OFFSETS.items():
            rom_bytes[k] = v

    if args.name:
        validate("name", args.name, 24)
        rom_bytes[0x3F00:0x3F17] = xorcrypt(args.name, 0x4E, 24)
    if args.address:
        validate("address", args.address, 68)
        rom_bytes[0x3F1A:0x3F5E] = xorcrypt(args.address, 0x4E, 68)
    if args.serial:
        validate("serial", args.serial, 12)
        rom_bytes[0x3F71:0x3F7D] = xorcrypt(args.serial, 0x4E, 12)
    if args.password:
        validate("password", args.password, 48)
        rom_bytes[0x3F87] = len(args.password) ^ 0xAA
        pwcrypt = xorcrypt(args.password, 0xAA, 49)
        # Fill 0x3F88 up to 0x3F97 (max 16 chars, 17 bytes for pad)
        rom_bytes[0x3F88:0x3F88+len(pwcrypt)] = pwcrypt

    return rom_bytes

def main():
    args = parse_args()
    if not args.src:
        sys.exit("Error: Please specify a source ROM file.")

    rom_bytes = bytearray(Path(args.src).read_bytes())

    if args.display:
        display_rom_info(rom_bytes)
        return

    if any([args.name, args.address, args.serial, args.password, args.quiet]):
        if not args.dest:
            sys.exit("Error: Please specify a destination ROM file using --dest.")
        if args.src == args.dest:
            sys.exit("Error: Source and destination must be different files.")
        patched_rom = patch_rom(args, rom_bytes)
        Path(args.dest).write_bytes(patched_rom)
        print(f"Patching complete. Output written to {args.dest}")

if __name__ == "__main__":
    main()
