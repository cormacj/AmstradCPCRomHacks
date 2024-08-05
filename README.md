# Amstrad CPC Rom Hacks
Just a repository of scripts for working with Amstrad CPC Roms

All files are Python3

If you have requests or bug reports, please open [a GitHub issue here](https://github.com/cormacj/AmstradCPCRomHacks/issues/new)

## romdetails.py

This script will display the name, version and command list for a ROM, including any hidden commands, meaning any that can only be called from code.

Some roms have a really disordered list of commands that make it hard to find a given command, so I added a -c option that only displays the commands so that these can be easily sorted with another command.

```
romdetails.py v2.50

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
Usage:
To display the details of what is stored in the ROM:
  cpmrompatch.py --src SourceROM.rom --display

To update the ROM, you must specify --src and --dest and one of the following:
  cpmrompatch.py --src SourceROM.rom --dest DestROM.rom
    --quiet - Disable the noisy, large default ROM boot message and replace it with a short version
    --name "<Name>" - Sets the name of the ROM owner
    --address "<Address>" - Sets the address of the ROM owner
    --serial <serial number> - Sets the serial number of the ROM
    --password <password> - Sets the password for |PASSWORD

You can also just pass a filename and it will display the details for that ROM
  eg cpmrompatch.py CPM1.ROM

Examples:
   cpmrompatch.py --src CPM1.rom --dest CPM1-updated.rom --name "John Smith" --address "123 Acacia Ave, Sometown"
```

## make_accessory_rom.py
This script will build an accessory ROM. It can also extract a .COM file from a prebuilt ROM file.

The name of the ROM file is required.

If you are extracting a .COM using `-e` then all the other possible arguments will be ignored if supplied.

```
usage: ./make_accessory_rom.py [-h] [-i "ROM ID String"] [-n "ROM Description"] [-v "ROM Version string"] [-e [filename, or blank for all files ...]] ROM_filename [.COM_file ...]

This is a utility to build accessory ROMs for Amstrad Graduate Software CP/M ROMs

options:
  -h, --help            show this help message and exit

Required:
  A name for a ROM file is required

  ROM_filename          This is the name of the ROM file that you are creating.

Building:
  These options relate to building a ROM

  .COM_file             This must be a CP/M program.
  -i "ROM ID String", --id "ROM ID String"
                        ROM Identification. It must start with G, and be no more than 16 characters. The default is "Grad ROM 06/2024"
  -n "ROM Description", --name "ROM Description"
                        This is the name that will be shown in commands such as |OHELP or romcat. It must be no more than 32 characters.
  -v "ROM Version string", --romversion "ROM Version string"
                        This is a string that will dictate the version of the rom.

Extracting:
  These options relate to extracting files from a ROM

  -e [filename, or blank for all files ...], --extract [filename, or blank for all files ...]
                        Extract files from a ROM.

Note: -e can only be used by itself and not with any other argument.

Examples:
  To recreate the original accessory rom:
    ./make_accessory_rom.py CPM_ACC1.ROM NSWEEP.COM FORMAT.COM PCW.COM RUN.COM UNERA.COM D.COM -i "Graduate (C)1988" -n "CP/M Accessory Rom 1" -v "VER 2.30 "

  Extract PCW.COM from CPM_ACC1.ROM:
    ./make_accessory_rom.py CPM_ACC1.ROM -e PCW
````
