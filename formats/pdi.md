A file with the `.pdi` extension represents a 1-bit bitmap image that has been compiled by `pdc`. This format uses little endian byte order.

## Header

| Offset | Type     | Detail |
|:-------|:---------|:-------|
| `0`    | `chr[12]` | Ident "Playdate IMG" |
| `12`   | `int32` | Unknown, seen as `0x00000080`, maybe bitflags or format ver? | |
| `16`   | `int32`  | Size of decompressed image data |
| `20`   | `int32`  | Image width |
| `24`   | `int32`  | Image height |
| `28`   | `int32`  | Unknown/reserved? Seen as 0 |

## Image Data

This section is zlib-compressed, after decompression:

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

### Cell Bitmap

Cell bitmaps are comprised of two 1-bit maps stored one after the other - first is the black/white map, second is the alpha map, which is only stored if the correct bitflags are set in the cell header. The width of each map is padded to the nearest multiple of 8. Transparent edges get trimmed.