A file with the `.pdz` extension represents an executable file that has been compiled by `pdc`. This format uses little endian byte order.

## Header

| Offset | Type     | Detail |
|:-------|:---------|:-------|
| `0`    | `chr[12]` | "Playdate PDZ" |
| `12`   | `int32` | Unknown, seen as `0x00000000`, maybe just reserved? | |

## File Entries

Following the header is a list of file entries. These can represent either Lua bytecode, or extra data and standard library image assets such as the crank prompt UI.

Each entry has the following:

| Type    | Detail |
|:--------|:-------|
| `uint8`  | Entry flags |
| `uint24` | Compressed data length + 4 |
| `string` | Filename as null-terminated string |
| `-` | Optional null-padding if needed to align to the next multiple of 4 bytes |
| `uint32` | Decompressed data length |
| `data` | Zlib-compressed file data |

### Entry Flags

| Flag | Detail |
|:-------|:-------|
| `(flags >> 7) & 0x1` | Is file compressed |
| `(flags >> 4) & 0xF` | File type[#file-type] |

### File Type

| Flag | Detail |
|:-------|:-------|
| `0` | Unknown/unused |
| `1` | Compiled Lua bytecode |
| `2` | Static image |
| `3` | Animated image |
| `4` | Unknown |
| `5` | Audio |
| `6` | Text strings |
| `7` | Font |

## Lua Bytecode

Playdate (at the time of writing) seems to use the prerelease version of Lua 5.4. This version uses a slightly nonstandard bytecode header structure, before it was reverted for the 5.4 release.

### Header

| Offset | Type    | Detail |
|:-------|:--------|:-------|
| `0`    | `byte[4]` | Constant `LUA_SIGNATURE` (hex `1B 4C 75 61`) |
| `4`    | `uint16`  | Version (`0x03F8` = 5.4.0 prerelease) |
| `6`    | `byte`    | Constant `LUAC_FORMAT` (hex `00`) |
| `7`    | `byte[6]` | Constant `LUAC_DATA` (hex `19 93 0D 0A 1A 0A`) |
| `13`   | `uint8`   | Instruction size (always `4`) |
| `14`   | `uint8`   | Integer size (always `4`) |
| `15`   | `uint8`   | Number size (always `4`) |
| `16`   | `lua int`  | Constant `LUA_INT` (`0x5678`) |
| `20`   | `lua float`  | Constant `LUA_NUM` (`370.5`) |

## Other Assets

Any other embedded assets (such as images, strings, etc) seem to have the ident part of their header (e.g. images won't begin with `Playdate IMG`) removed, but are otherwise the same as their corresponding format.