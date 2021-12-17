A file with the `.pdi` extension represents a 1-bit bitmap image that has been compiled by `pdc`. This format uses little endian byte order.

## Header

| Offset | Type      | Detail               |
|:-------|:----------|:---------------------|
| `0`    | `chr[12]` | Ident `Playdate IMG` |
| `12`   | `int32`   | File bitflags        |

### File Flags

| Bitmask             | Detail                                      |
|:--------------------|:--------------------------------------------|
| `(flag >> 7) & 0x1` | If `1`, the data in this file is compressed |

## Image Header

If the compression flag is set, there's an extra image header after the file header:

| Offset | Type     | Detail |
|:-------|:---------|:--------------------------------|
| `0`    | `int32`  | Size of image data section when decompressed |
| `4`    | `int32`  | Image width |
| `8`    | `int32`  | Image height |
| `12`   | `int32`  | Unknown/reserved? Seen as 0 |

## Image Data

If the compression flag is set, then this section is zlib-compressed.

### Cell header

| Offset | Type     | Detail |
|:-------|:---------|:-------|
| `0`    | `uint16` | Cell width |
| `2`    | `uint16` | Cell height |
| `4`    | `uint16` | Cell stride (bytes per image row) |
| `6`    | `uint16` | Cell clip left |
| `8`    | `uint16` | Cell clip right |
| `10`   | `uint16` | Cell clip top |
| `12`   | `uint16` | Cell clip bottom |
| `14`   | `uint16` | Cell bitflags |

### Cell Bitflags

| Bitmask             | Detail                     |
|:--------------------|:---------------------------|
| `(flags & 0x3) > 0` | Cell contains an alpha map |

### Cell Bitmap

Cell bitmaps are comprised of two 1-bit maps stored one after the other - first is the black/white map, second is the alpha map, which is only stored if the correct bitflags are set in the cell header. The width of each map is padded to the nearest multiple of 8. Transparent edges get trimmed.