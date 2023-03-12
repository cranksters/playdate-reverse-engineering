A file with the `.pdi` extension represents a 1-bit bitmap image that has been compiled by `pdc`. This format uses little endian byte order.

## Header

| Offset | Type      | Detail               |
|:-------|:----------|:---------------------|
| `0`    | `char[12]` | Ident `Playdate IMG` |
| `12`   | `uint32`   | [File Flags](#file-flags) |

### File Flags

| Bitmask             | Detail                                      |
|:--------------------|:--------------------------------------------|
| `flags & 0x80000000` | If `> 0`, the data in this file is compressed |

## Image Header

If the compression flag is set, there's an extra image header after the file header. Everything after this is zlib-compressed. 

| Offset | Type     | Detail |
|:-------|:---------|:--------------------------------|
| `0`    | `uint32`  | Size of image data section when decompressed |
| `4`    | `uint32`  | Image width (in pixels) |
| `8`    | `uint32`  | Image height (in pixels) |
| `12`   | `uint32`  | Unknown/reserved? Seen as 0 |

## Image Data

`.pdi` image data comprises of a single [Image Cell](#image-cell).

## Image Cell

The `pdi`, [`.pdt`](formats/pdi.md) and [`.pft`](formats/pft.md) formats store pixels as "cells", where transparent edges are cropped out to save on space. 

### Cell Header

| Offset | Type     | Detail |
|:-------|:---------|:-------|
| `0`    | `uint16` | Cell clip width (in pixels) |
| `2`    | `uint16` | Cell clip height (in pixels) |
| `4`    | `uint16` | Cell stride (bytes per image row) |
| `6`    | `uint16` | Cell clip left (in pixels) |
| `8`    | `uint16` | Cell clip right (in pixels) |
| `10`   | `uint16` | Cell clip top (in pixels) |
| `12`   | `uint16` | Cell clip bottom (in pixels) |
| `14`   | `uint16` | [Cell bitflags](#cell-bitflags) |

### Cell Bitflags

| Bitmask             | Detail                     |
|:--------------------|:---------------------------|
| `flags & 0x3` | If `> 0`, cell uses transparency |

### Cell Pixels

Cells contain at least one 1-bit bitmap for black/white color (`0` for black and `1` for white). If the transparency flag is set, this will be followed by an additional 1-bit bitmap for the image alpha (`0` for transparent and `1` for opaque).

The data for a cell bitmap will be `stride * clip height` bytes long. Each row of the image will contain `clip width` pixels. Transparent edges are not stored, and must be added back to the cell based on the values given in th cell header.

![Transparent edges are removed from the image to reduce its size](https://github.com/jaames/playdate-reverse-engineering/blob/main/_images/bitmap-clip.png)

The final image width will equal `clip left + clip width + clip right`, likewise the height will equal `clip top + clip height + clip bottom`,