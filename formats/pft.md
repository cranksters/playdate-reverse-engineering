A file with the `.pft` extension represents a 1-bit bitmap font that has been compiled by `pdc`. This format uses little endian byte order.

## Header

| Offset | Type      | Detail               |
|:-------|:----------|:---------------------|
| `0`    | `char[12]` | Ident `Playdate FNT` |
| `12`   | `uint32`   | [Flags](#flags) |

### Flags

| Bitmask             | Detail                                      |
|:--------------------|:--------------------------------------------|
| `flags & 0x80000000` | If `> 0`, the data in this file is compressed |
| `flags & 0x00000001` | If `> 0`, the font contains characters above U+1FFFF |

## Font Header

If the compression flag is set, there's an extra font header after the file header. Everything after this is zlib-compressed. 

| Offset | Type     | Detail |
|:-------|:---------|:--------------------------------|
| `0`    | `uint32`  | Size of font data section when decompressed |
| `4`    | `uint32`  | Maximum glyph width (in pixels) |
| `8`    | `uint32`  | Maximum glyph height (in pixels) |

## Page List

### Page List Header

| Offset | Type     | Detail |
|:-------|:---------|:--------------------------------|
| `0`    | `uint8`  | Glyph width (in pixels) |
| `1`    | `uint8`  | Glyph height (in pixels) |
| `2`    | `uint16`  | Tracking (in pixels) |
| `4`    | `64 bytes` | [Page Usage Flags](#page-usage-flags) |

Font glyphs are grouped into pages based on their unicode codepoints. Each page covers a span of 256 glyphs. Pages are only stored if they have glyphs present in the font.

The page index for a given glyph codepoint will be `codepoint >> 8`.

Following this header is a list of `uint32` offsets for all of the pages present in the file, with the pages following immediately after.

### Page Usage Flags

This contains bitflags for each page, starting at the lowest significant bit in the first byte. If a page's corresponding usage flag is `1`, then it is present in the file.

## Page

### Page Header

| Offset | Type     | Detail |
|:-------|:---------|:--------------------------------|
| `0`    | `uint24`  | Reserved? Seen as `0` |
| `3`    | `uint8`  | Number of glyphs |
| `4`    | `32 bytes`  | [Glyph Usage Flags](#glyph-usage-flags) |

After the page header is a series of [Glyphs](#glyph) for the page.

### Glyph Usage Flags

This contains bitflags for each glyph, starting at the lowest significant bit in the first byte. If a glyph's corresponding usage flag is `1`, then it is present in the page.

## Glyph

Each glyph is comprised of:
 - a header
 - a short kerning table
 - (if necessary) padding bytes to align to the next multiple of 4
 - a long kerning table
 - pixel data

### Glyph Header

| Offset | Type     | Detail |
|:-------|:---------|:--------------------------------|
| `0`    | `uint8`  | Glyph advance / width (in pixels) |
| `1`    | `uint8`  | Number of [Short Kerning Table Entries](#short-kerning-table-entries) |
| `2`    | `uint16`  | Number of [Long Kerning Table Entries](#long-kerning-table-entries) |

### Short Kerning Table Entries

I think this is for codepoints within the same page?

| Offset | Type     | Detail |
|:-------|:---------|:--------------------------------|
| `0`    | `uint8`  | Other glyph codepoint |
| `1`    | `int8`  | Kerning (in pixels) |

### Long Kerning Table Entries

This supports any unicode codepoint within the whole font

| Offset | Type     | Detail |
|:-------|:---------|:--------------------------------|
| `0`    | `uint24`  | Other glyph codepoint |
| `3`    | `int8`  | Kerning (in pixels) |

### Glyph pixels

Stored as an [Image Cell](/formats/pdi.md#image-cell).