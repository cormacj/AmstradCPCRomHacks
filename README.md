# Amstrad CPC Rom Hacks
Just a repository of scripts for working with Amstrad CPC Roms

All files are Python3

If you have requests or bug reports, please open [a GitHub issue here](https://github.com/cormacj/AmstradCPCRomHacks/issues/new)

## romdetails.py

This script will display the name, version and command list for a ROM, including any hidden commands, meaning any that can only be called from code.

Some roms have a really disordered list of commands that make it hard to find a given command, so I added a -c option that only displays the commands so that these can be easily sorted with another command.

```
romdetails.py v2.51

Usage:
This will display the RSX commands (if any) available in a ROM:
romdetails.py ./SourceROM.rom


Examples:
	./romdetails.py TestROM.rom
	Rom type: Background
	Version:  1.21

	TESTROM
	RSX1
	RSX2
	Hidden Command: 0x0
	Hidden Command: 0x1

-h or --help - this message
-c or --commandonly - only list the commands
-w or --wiki - output the commands in a wikitable format, suitable for pasting into a wiki
```
The script will also decode Graduate Software Accessory ROMS:
```
./romdetails.py ./CPM_Plus_Acc_1.rom
Rom type: Graduate Software CP/M Accessory ROM
Name:	  Graduate (C)1988
	  CP/M Accessory Rom 1
Version:  VER 2.30
Apps:
NSWEEP
FORMAT
PCW
RUN
UNERA
D
```
## dum.py

  This dumps a .ROM file showing any printable ascii characters and strings.
  There are two options parameters that can be used.

  -x <xor value> This is useful for looking at the encoded information in Graduate Software CPM+ roms.
```
  Usage: dum.py romfile.rom -x <xor hex value>
  Example: dum.py CPM1.rom -x 0x4e
    Known XOR values are:
      0xaa - password
      0x4e - name, address, serial etc
```
  Usage: dum.py romfile.rom -o <offset value>
     This is useful if you are reverse engineering a ROM and want to know where strings occur. Roms usually start at 0xC000
  Example: dum.py CPM1.ROM -o 0xc000

## cpmrompatch.py

This was written for patching Graduate Software CPM+ roms. For more details see here: https://www.cpcwiki.eu/index.php/Graduate_Software

This patches the first CPM rom so you can use your own name, address, password etc
```
usage: cpmrompatch.py [-h] [--src SRC] [--dest DEST] [--display] [--quiet] [--name NAME] [--address ADDRESS] [--serial SERIAL] [--password PASSWORD] [filename]

Patch/display Graduate Software CPM+ ROMs for Amstrad CPC. Version 2.01

positional arguments:
  filename             ROM file (display mode if no --src)

options:
  -h, --help           show this help message and exit
  --src SRC            Source ROM file
  --dest DEST          Destination ROM file (for patching)
  --display            Display ROM details
  --quiet              Patch ROM to quiet boot
  --name NAME          Set ROM owner name (max 24 chars)
  --address ADDRESS    Set ROM owner address (max 68 chars)
  --serial SERIAL      Set serial number (max 12 chars)
  --password PASSWORD  Set password (max 48 chars)

You can also just pass a filename and it will display the details for that ROM
  eg cpmrompatch.py CPM1.ROM

Examples:
   cpmrompatch.py --src CPM1.rom --dest CPM1-updated.rom --name "John Smith" --address "123 Acacia Ave, Sometown"
```

The `--quiet` flag, removes the large red noisy banner and replaces it with a simpler "Graduate Software - CP/M Loader" message.


## make_accessory_rom.py
This script will build an accessory ROM for use with the Graduate Software CP/M roms. It can also extract a .COM file from a prebuilt ROM file.

The name of the ROM file is required.

If you are extracting a .COM using `-e` then all the other possible arguments will be ignored if supplied.

```
make_accessory_rom.py - version 2.00

usage: make_accessory_rom.py [-h] [-i ID] [-n NAME] [-v ROMVERSION] [-e COMfile [COMfile ...]] ROMfile [COMfiles ...]

Build accessory ROMs for Amstrad Graduate Software CP/M ROMs

options:
  -h, --help            show this help message and exit

Creating ROMs:
  make_accessory_rom.py [-h] [-i ID] [-n NAME] [-v ROMVERSION] ROMfile COMfile [COMfiles ...]

  ROMfile               ROM file to create
  COMfiles              CP/M .COM programs to add
  -i ID, --id ID        ROM id (max 16)
  -n NAME, --name NAME  ROM name (max 22)
  -v ROMVERSION, --romversion ROMVERSION
                        ROM version (max 16)

Extracting files from a ROM:
  usage: make_accessory_rom.py ROMFILE -e COMfile [COMfiles ...]

  -e COMfile [COMfile ...], --extract COMfile [COMfile ...]
                        Extract files from ROM

Examples:
  To recreate the original accessory rom:
    /home/cormac/Amstrad/utils/make_accessory_rom.py -i "Graduate (C)1988" -n "CP/M Accessory Rom 1" -v "VER 2.30" CPM_ACC1.ROM NSWEEP.COM FORMAT.COM PCW.COM RUN.COM UNERA.COM D.COM

  Extract PCW.COM from CPM_ACC1.ROM:
    /home/cormac/Amstrad/utils/make_accessory_rom.py CPM_ACC1.ROM -e PCW
````
## headertool.py
This tool will remove AMSDOS headers from files for use with emulators.

Sometimes files are uploaded to sites with the AMSDOS 128 byte header intact and this causes the file to not work in an emuator. This tool removes that header and writes a new copy.

```
A tool to remove AMSDOS headers from an image.

Usage: headertool.py source.rom destination.rom -n <size of header to remove>
   -n is optional, defaults to 0x80

Example:
headertool.py CPM1.rom CPM1-fixed.rom -n 0x7f

```
