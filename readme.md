Playdate reverse-engineering notes/tools - covers file formats, server API and USB commands

## Documentation

- **File Formats**
  - **Playdate compiled game formats**
    - [**.pdz**](https://github.com/jaames/playdate-reverse-engineering/blob/main/formats/pdz.md) - Executable file container
    - [**.pda**](https://github.com/jaames/playdate-reverse-engineering/blob/main/formats/pda.md) - Audio file
    - [**.pdi**](https://github.com/jaames/playdate-reverse-engineering/blob/main/formats/pdi.md) - Image file
    - [**.pdt**](https://github.com/jaames/playdate-reverse-engineering/blob/main/formats/pdt.md) - Imagetable file
    - [**.pdv**](https://github.com/jaames/playdate-reverse-engineering/blob/main/formats/pdv.md) - Video file
    - **.pft** - Font file
  - **Other formats**
    - **.fnt** - Font source file
- **Server**
  - [**Playdate API**](https://github.com/jaames/playdate-reverse-engineering/blob/main/server/api.md) - Main Playdate server API
- **Misc**
  - [**USB**](https://github.com/jaames/playdate-reverse-engineering/blob/main/usb/usb.md) - Playdate USB interface

## Tools

- [**`pdz.py`**](https://github.com/jaames/playdate-reverse-engineering/blob/tools/pdz.py) - Unpacks all files from a `.pdz` file container
- [**`pdex2elf.py`**](https://github.com/jaames/playdate-reverse-engineering/blob/tools/pdex2elf.py) - Converts a `pdex.bin` to an ELF file that can be analysed in a decompilation tool such as Ghidra

## Special Thanks

 - [Matt Sephton](https://github.com/gingerbeardman) for helping me get access to the Playdate Developer Preview
 - [Simon](https://github.com/simontime) for helping with some ADPCM audio reverse engineering
 - [zhuowei](https://github.com/zhuowei) for this [script for unpacking Playdate .pdx executables](https://gist.github.com/zhuowei/666c7e6d21d842dbb8b723e96164d9c3), which was the base for `pdz.py`
 - The folks at [Panic](https://panic.com/) for making such a wonderful and fascinating handheld!

 ----

 2021 James Daniel

 Playdate is © [Panic Inc.](https://panic.com/) This project isn't affiliated with or endorsed by them in any way