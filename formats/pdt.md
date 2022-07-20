A file with the `.pdt` extension represents a 1-bit bitmap image table containing multiple sub-images (like a spritesheet or animation) that has been compiled by `pdc`. This format uses little endian byte order.

## Header

| Offset | Type     | Detail |
|:-------|:---------|:-------|
| `0`    | `chr[12]` | Ident `Playdate IMT` |
| `12`   | `int32`   | File bitflags  |

### File Flags

| Bitmask             | Detail                                      |
|:--------------------|:--------------------------------------------|
| `(flag >> 7) & 0x1` | If `1`, the data in this file is compressed |

## Image Header

If the compression flag is set, there's an extra header after the file header:

| Offset | Type     | Detail |
|:-------|:---------|:--------------------------------|
| `0`    | `int32`  | Size of decompressed image data |
| `4`    | `int32`  | Image width |
| `8`    | `int32`  | Image height |
| `12`   | `int32`  | Number of cells |

The image width and height are for the first image only.
In sequential image tables, the following images may be of
different sizes.
In matrix image tables, all images must be the same size.

## Image Data

If the compression flag is set, then this section is zlib-compressed.

### Table header

| Offset | Type    | Detail |
|:-------|:--------|:-------|
| `0`    | `uint16` | Num cells |
| `2`    | `uint16` | Num cells per row |

For sequential image tables, the values will be the same.

For matrix image tables, the second value will be the number of cells on each row.

### Table

After this header, there is a table of int32 offsets for each cell aside from the first one, as well as an offset to the end of the data.

Offsets are relative to the end of the table, and the first cell always begins directly after the table.

### Cell header

| Offset | Type    | Detail |
|:-------|:--------|:-------|
| `0`    | `uint16` | Cell width |
| `2`    | `uint16` | Cell height |
| `4`    | `uint16` | Cell stride (bytes per image row) |
| `6`    | `uint16` | Cell clip left |
| `8`    | `uint16` | Cell clip right |
| `10`   | `uint16` | Cell clip top |
| `12`   | `uint16` | Cell clip bottom |
| `14`   | `uint16` | Bitflags |

### Cell Bitflags

| Mask | Detail |
|:-------|:-------|
| `(flags & 0x3) > 0` | Cell contains an alpha map |

### Cell Bitmaps

Cell bitmaps are comprised of one or two 1-bit maps stored one after the other - first is the black/white map, second is the alpha map, which is only stored if the correct bitflags are set in the cell header. The width of each map is padded to the nearest multiple of 8. Transparent edges get trimmed.
