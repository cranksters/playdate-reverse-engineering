A file with the `.pdt` extension represents a 1-bit bitmap image table containing multiple sub-images (like a spritesheet or animation) that has been compiled by `pdc`. This format uses little endian byte order.

## Header

| Offset | Type     | Detail |
|:-------|:---------|:-------|
| `0`    | `char[12]` | Ident `Playdate IMT` |
| `12`   | `uint32`   | File bitflags  |

### File Flags

| Bitmask             | Detail                                      |
|:--------------------|:--------------------------------------------|
| `flag & 0x80000000` | If `> 0`, the data in this file is compressed |

## Image Header

If the compression flag is set, there's an extra header after the file header:

| Offset | Type     | Detail |
|:-------|:---------|:--------------------------------|
| `0`    | `uint32`  | Size of decompressed image data |
| `4`    | `uint32`  | Image width (in pixels) |
| `8`    | `uint32`  | Image height (in pixels) |
| `12`   | `uint32`  | Number of cells |

The image width and height are for the first image only. In sequential image tables, the following images may be of
different sizes. In matrix image tables, all images must be the same size.

## Image Data

If the compression flag is set, then this section is zlib-compressed.

### Table Header

| Offset | Type    | Detail |
|:-------|:--------|:-------|
| `0`    | `uint16` | Num cells |
| `2`    | `uint16` | Num cells per row |

For sequential image tables, the values will be the same. For matrix image tables, the second value will be the number of cells on each row.

### Table

After this header, there is a table of uint32 offsets for each [image cell](#image-cell) aside from the first one, as well as an offset to the end of the data.

Offsets are relative to the end of the table, and the first cell always begins directly after the table.

### Image Cell

See: (Image Cell)[/formats/pdi.md#image-cell]