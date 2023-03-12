A file with the `.pdz` extension represents a file container that has been compiled by `pdc`. They mostly contain compiled Lua bytecode, but they can sometimes include other assets such as images or fonts. This format uses little endian byte order.

## Header

| Offset | Type     | Detail |
|:-------|:---------|:-------|
| `0`    | `char[12]` | Ident `Playdate PDZ` |
| `12`   | `uint32`   | Reserved, always 0  |

## File Entries

Following the header is a list of file entries. Each entry has a header.

| Type    | Detail |
|:--------|:-------|
| `uint8`  | [Entry Flags](#entry-flags) |
| `uint24` | [Entry Data](#entry-data) length |
| `string` | Filename as null-terminated C string |
| `-` | Optional null-padding if needed to align to the next multiple of 4 bytes |

If the [Entry Type](#entry-type) flag is `5` (for a `.pda` audio file), some additional values are included:

| Type    | Detail |
|:--------|:-------|
| `uint24` | Audio sample rate in Hz |
| `uint8`  | [Audio Data Format](/format/pda.md#audio-data-format) |

### Entry Flags

| Flag | Detail |
|:-------|:-------|
| `flags & 0x80` | If `> 0`, file entry data is compressed |
| `flags & 0x7F` | [Entry Type](#entry-type) |

### Entry Type

| Flag | Detail |
|:-------|:-------|
| `0` | Unknown/unused |
| `1` | Compiled Lua bytecode ([`.luac`](/formats/luac.md)) |
| `2` | Static image ([`.pdi`](/formats/pdi.md)) |
| `3` | Animated image ([`.pdt`](/formats/pdt.md)) |
| `4` | Video ([`.pdv`](/formats/pdv.md)) |
| `5` | Audio ([`.pda`](/formats/pda.md)) |
| `6` | Text strings ([`.pds`](/formats/pds.md)) |
| `7` | Font ([`.pft`](/formats/pft.md)) |

## Entry Data

The data for a given file entry is immediately after the entry's file header. If the file's compression flag is set, this will begin with a `uint32` giving the decompressed size of the data, followed by zlib-compressed data.

All of the asset entries (`.pdi`, `.pdt`, `.pdv`, `.pda`, `.pds`, `.pft`), will be missing the first 16 bytes of the header, since for most of these formats this just contains a 12-byte format ident string and some compression flags. This is why `.pda` entries have additional header fields for the sample rate and audio format.