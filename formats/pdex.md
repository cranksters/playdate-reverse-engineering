The `pdex.bin` file represents information and executable code copied by `pdc` from a `pdex.elf` ELF file compiled for ARM32 (Thumb, EABI v5, hard-float). It is usually the entry point of Playdate games created using the C API. The file format uses little endian byte order.

Supplementary reading:

- https://en.wikipedia.org/wiki/Executable_and_Linkable_Format
- https://www.man7.org/linux/man-pages/man5/elf.5.html

# File structure

1. [File header](#file-header)
2. [Program header](#program-header)
3. [Program data](#program-data)
   1. [Program segment](#program-segment)
   2. [Relocation entries](#relocation-entries)

## File header

| Offset | Type       | Detail                         |
|:-------|:-----------|:-------------------------------|
| `0x00` | `char[12]` | File signature: `Playdate PDX` |
| `0x0C` | `uint32`   | [Flags](#flags)                |
| `0x10` | -          | End of file header (size)      |

### Flags

| Bitmask             | Detail                                                |
|:--------------------|:------------------------------------------------------|
| `flag & 0x40000000` | If `> 0`, all data after the file header is encrypted |

Encryption is (at the time of writing) only used by Catalog games as a form of DRM. The encryption method is not yet known.

## Program header

| Offset | Type        | Detail                                             |
|:-------|:------------|:---------------------------------------------------|
| `0x00` | `uint8[16]` | MD5 checksum of program segment                    |
| `0x10` | `uint32`    | Size of program segment in file image; `p_filesz`  |
| `0x14` | `uint32`    | Size of program segment in memory image; `p_memsz` |
| `0x18` | `uint32`    | Entry point address; `e_entry`                     |
| `0x1C` | `uint32`    | Number of relocation entries                       |
| `0x20` | -           | End of program header (size)                       |

## Program data

The program data is zlib-compressed and consists of [a single program segment](#program-segment) immediately followed by [relocation entries](#relocation-entries).

### Program segment

The first `p_filesz` bytes of the uncompressed program data is the program segment, usually consisting of the `.text` (executable code) and `.data` (initialized global variables) sections of the original ELF file. The `.bss` (uninitialized global variables) section does not occupy any space in the file image; its size in memory can be computed via `p_memsz - p_filesz`.

### Relocation entries

The next `<number of relocation entries> * 4` bytes of the uncompressed program data are the relocation entries, usually from the `.rel.text` and/or `.rel.data` sections of the original ELF file. Each entry is a single `uint32` denoting a byte offset from the beginning of the program segment where a relocation should take place, corresponding to the `r_offset` member of an `ELf32_Rel` relocation entry.
