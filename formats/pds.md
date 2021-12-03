A file with the `.pds` extension represents a collection localization strings that have been compiled by `pdc`. This format uses little endian byte order.

## Header

| Offset | Type     | Detail |
|:-------|:---------|:-------|
| `0`    | `chr[12]` | Ident "Playdate STR" |
| `12`   | `int32`  | Unknown, seen as `0x00000080`, maybe bitflags or format ver? | |
| `16`   | `int32`  | Size of decompressed string data |
| `20`   | `int32`  | Unused/reserved, seen as 0 |
| `24`   | `int32`  | Unused/reserved, seen as 0 |
| `28`   | `int32`  | Unused/reserved, seen as 0 |

## String Data

This section is zlib-compressed, after decompression:

### Table Header

| Offset | Type    | Detail |
|:-------|:--------|:-------|
| `0`    | `int32` | Number of string entries |

### Table

After this header, there is a table of int32 offsets for each string entry aside from the first one, as well as an offset to the end of the data.

Offsets are relative to the end of the table, and the first string entry always begins directly after the table.

### String Entry

Each string entry contains an utf8 key, followed by a null byte, followed by a utf8 value, followed by another null byte.