# Amstrad CPC Rom Hacks
Just a repository of scripts for working with Amstrad CPC Roms

All files are Python3

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
    --name "<Name>" - Sets the name of the ROM owner
    --address "<Address>" - Sets the address of the ROM owner
    --serial <serial number> - Sets the serial number of the ROM
    --password <password> - Sets the password for |PASSWORD

You can also just pass a filename and it will display the details for that ROM
  eg cpmrompatch.py CPM1.ROM

Examples:
   cpmrompatch.py --src CPM1.rom --dest CPM1-updated.rom --name "John Smith" --address "123 Acacia Ave, Sometown"
```
