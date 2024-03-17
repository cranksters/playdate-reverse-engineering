Unofficial Playdate reverse-engineering notes/tools - covers file formats, server API and USB serial commands

> ⚠️ This documentation is unofficial and is not affiliated with Panic. All of the content herein was gleaned from reverse-engineering Playdate tools and game files, and as such there may be mistakes or missing information. 

## Documentation

- **File Formats**
  - **Playdate game formats**
    - [**pdex.bin**](formats/pdex.md) - Executable code
    - [**.luac**](formats/luac.md) - Lua bytecode
    - [**.pdz**](formats/pdz.md) - File container
    - [**.pda**](formats/pda.md) - Audio file
    - [**.pdi**](formats/pdi.md) - Image file
    - [**.pdt**](formats/pdt.md) - Imagetable file
    - [**.pdv**](formats/pdv.md) - Video file
    - [**.pds**](formats/pds.md) - Strings file
    - [**.pft**](formats/pft.md) - Font file
  - **Other formats**
    - [**.fnt**](formats/fnt.md) - Font source file
    - **.strings** - Strings source file (TODO)
- **Server**
  - [**Playdate API**](server/api.md) - Main Playdate server API
- **Misc**
  - [**USB**](usb/usb.md) - USB serial interface
  - [**Streaming**](usb/stream.md) - Video/audio streaming protocol (via USB serial), used by Playdate Mirror

## Tools

- [**`pdz.py`**](tools/pdz.py) - Unpacks all files from a `.pdz` file container.
- [**`usbeval.py`**](tools/usbeval.py) - Uses the Playdate's USB `eval` command to evaluate a Lua script over USB. Has access to the Lua runtime of the currently loaded game, except for system apps.
- [**`pdex2elf.ps1`**](tools/pdex2elf.ps1) - Converts a `pdex.bin` to an ELF file that can be analyzed in tools such as readelf, objdump or Ghidra, or compiled back to the same original `pdex.bin` by `pdc`. Requires PowerShell 7.4 or later.

## Related Projects and Resources

- [**pd-usb**](https://github.com/jaames/pd-usb) - JavaScript library for interacting with the Playdate's serial API from a WebUSB-compatible web browser.
- [**unluac**](https://github.com/scratchminer/unluac) - Fork of the unluac Lua decompiler, modified to support Playdate-flavoured Lua.
- [**lua54**](https://github.com/scratchminer/lua54) - Fork of Lua that aims to match the custom tweaks that Panic added for Playdate-flavoured Lua.

## Special Thanks

 - [Zhuowei](https://github.com/zhuowei) for this [script for unpacking Playdate .pdx executables](https://gist.github.com/zhuowei/666c7e6d21d842dbb8b723e96164d9c3), which was the base for `pdz.py`
 - [Scratchminer](https://github.com/scratchminer) for their further reverse-engineering work on the Playdate's [file formats](https://github.com/scratchminer/pd-emu), streaming protocol and [Lua implementation](https://github.com/scratchminer/lua54).
 - [Simon](https://github.com/simontime) for helping with some ADPCM audio data reverse engineering
 - The folks at [Panic](https://panic.com/) for making such a wonderful and fascinating handheld!

 ----

 2022-2023 James Daniel

 Playdate is © [Panic Inc.](https://panic.com/) - this project isn't affiliated with or endorsed by them in any way.
