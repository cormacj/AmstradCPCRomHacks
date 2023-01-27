# Amstrad CPC Rom Hacks
Just a repository of scripts for working with Amstrad CPC Roms

All files are Python3

Currently the two scripts here are aimed at the Graduate Software CPM+ roms. For more details see here: https://www.cpcwiki.eu/index.php/Graduate_Software

- dum.py

This dumps a .ROM file showing any printable ascii characters and strings. It takes an optional xor value for looking
at the encoded information in Graduate Software CPM+ roms.

Usage: dum.py romfile.rom <xor hex value>
Example: dum.py CPM1.rom 0x4e
  Known XOR values are:
    0xaa - password
    0x4e - name, address, serial etc
- cpmrompatch.py

This patches the first CPM rom so you can use your own name, address, password etc

Usage:
To display the details of what is stored in the ROM:
  cpmrompatch.py --src SourceROM.rom --display

To update the ROM, you must specify --src and --dest and one of the following:
  cpmrompatch.py --src SourceROM.rom --dest DestROM.rom
    --name "<Name>" - Sets the name of the ROM owner
    --address "<Address>" - Sets the address of the ROM owner
    --serial <serial number> - Sets the serial number of the ROM
    --password <password> - Sets the password for |PASSWORD

Examples:
   cpmrompatch.py --src CPM1.rom --dest CPM1-updated.rom --name "John Smith" --address "123 Acacia Ave, Sometown"
