# Amstrad CPC Rom Hacks
Just a repository of scripts for working with Amstrad CPC Roms

All files are Python3

Currently the two scripts here are aimed at the Graduate Software CPM+ roms. For more details see here: https://www.cpcwiki.eu/index.php/Graduate_Software

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
