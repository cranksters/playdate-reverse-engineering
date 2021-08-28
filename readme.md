Playdate reverse-engineering notes - covers file formats, server API and USB commands

## Contents

- **File Formats**
  - **Playdate compiled game formats**
    - [**.pdz**](https://github.com/jaames/playdate-reverse-engineering/blob/main/formats/pdz.md) - Executable file container
    - [**.pda**](https://github.com/jaames/playdate-reverse-engineering/blob/main/formats/pda.md) - Audio file
    - [**.pdi**](https://github.com/jaames/playdate-reverse-engineering/blob/main/formats/pdi.md) - Image file
    - [**.pdt**](https://github.com/jaames/playdate-reverse-engineering/blob/main/formats/pdt.md) - Imagetable file
    - **.pft** - Font file
    - **.pdv** - Video file
  - **Other formats**
    - **.fnt** - Font source file
- **Server**
  - [**Playdate API**](https://github.com/jaames/playdate-reverse-engineering/blob/main/server/api.md) - Main Playdate server API
- **Misc**
  - [**USB**](https://github.com/jaames/playdate-reverse-engineering/blob/main/usb/usb.md) - Playdate USB interface

## Special Thanks

 - [Matt Sephton](https://github.com/gingerbeardman) for helping me get access to the Playdate Developer Preview
 - [Simon](https://github.com/simontime) for helping with some ADPCM audio reverse engineering
 - [zhuowei](https://github.com/zhuowei) for this [script for unpacking Playdate .pdx executables](https://gist.github.com/zhuowei/666c7e6d21d842dbb8b723e96164d9c3), even though it's outdated/wrong :P
 - The folks at [Panic](https://panic.com/) for making such a wonderful and fascinating handheld

 ----

 2021 James Daniel

 Playdate is © [Panic Inc.](https://panic.com/) This project isn't affiliated with or endorsed by them in any way