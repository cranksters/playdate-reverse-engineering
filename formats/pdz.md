A file with the `.pdz` extension represents an executable file that has been compiled by `pdc`. This format uses little endian byte order.

## Header

| Offset | Type     | Detail |
|:-------|:---------|:-------|
| `0`    | `chr[16]` | "Playdate PDZ", with null padding at the end |

## File Entries

Following the header is a list of file entries. These can represent either Lua bytecode, or extra data and standard library image assets such as the crank prompt UI.

If the file compression flag is set, each entry consists of:

| Type    | Detail |
|:--------|:-------|
| `uint8`  | Entry flags |
| `uint24` | Compressed data length + 4 |
| `string` | Filename as null-terminated string |
| `-` | Optional null-padding if needed to align to the next multiple of 4 bytes |
| `uint32` | Decompressed data length |
| data | Zlib-compressed entry data |

Otherwise if the compression flag is not set:

| Type    | Detail |
|:--------|:-------|
| `uint8`  | Entry flags |
| `uint24` | Data length |
| `string` | Filename as null-terminated string |
| `-` | Optional null-padding if needed to align to the next multiple of 4 bytes |
| data | Entry data |

### Entry Flags

| Flag | Detail |
|:-------|:-------|
| `(flags >> 7) & 0x1` | Is file compressed |
| `flags & 0x7F` | [File type](#file-type) |

### File Type

| Flag | Detail |
|:-------|:-------|
| `0` | Unknown/unused |
| `1` | Compiled Lua bytecode |
| `2` | Static image |
| `3` | Animated image |
| `4` | Unknown - possibly video? |
| `5` | Audio |
| `6` | Text strings |
| `7` | Font |

## Lua Bytecode

At the time of writing the Playdate Lua runtime is based on [prerelease/beta version of Lua 5.4](https://github.com/lua/lua/tree/6c0e44464b9eef4be42e2c8181aabfb3301617ad). This version uses a slightly nonstandard bytecode header structure, before it was reverted for the 5.4 release.

It is possible to execute Playdate Lua bytecode by compiling the 5.4-beta version of Lua with `#define LUA_32BITS = 1` set in `luaconf.h`.

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

Any other embedded assets (such as images, strings, etc) seem to have the ident part of their header (e.g. pdi images won't begin with `Playdate IMG`) removed, but are otherwise the same as their corresponding format.