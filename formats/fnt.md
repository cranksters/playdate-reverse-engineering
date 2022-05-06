A file with the `.fnt` extension contains font data created by [playdate caps](https://play.date/caps/).  It is a line oriented UTF-8 plaintext file format, suitable for editing with normal text editors and optionally includes a base64 encoded PNG sprite sheet.

Each line is one of:

1. String key value data separated by an equals character `=`
2. Glyph widths: A UTF-8 character, whitespace and pixel width of the character
3. Kerning data: Two UTF-8 characters, whitespace and pixel offset for this kerning pair.
4. Lua style comments beginning with `--` and empty lines which are skipped


## Glyph Widths

````
8   8
9   8
space   5
�   9
````

In its most basic form a fnt file is one or more lines comprising an index to specify
characters and widths for each glyphs in an accompanying PNG sprite sheet.
Pairs of UTF-8 glyphs and their widths are separated by any amount of whitespace,
one per line, specified in the order they appear in the sprite sheet.
(Left to Right, Top to Buttom)

Playdate supports all code points in the first four Unicode planes, up to U+3FFFF.

Because these glyphs and widths are whitespace separated, a special string
 `space` is substited for the ` ` space glyph.

## External PNG Data

The PNG may be external file or included internally in the fnt file.
When external, the accompanying PNG must be named to match the font file.
For example the PNG for `pantspants.fnt` would named pantspants-table-9-12.png
assuming the fonts glyphs are 9 pixels wide and 12 pixels tall.

## Internal PNG Data

Alternatively the PNG data may be included within the fnt file itself, base64 encoded
along with the necessary metadata (height/width) required to process the PNG sprite sheet.

```
datalen=2052
data=iVBORw0KGgoAAAANSUhEUgAAABQAAAAKCAYAAAC0VX7mAAAAAXNSR0IArs4c6QAAAF5JREFUOE+tktsKACAIQ/X/P7owGHjJUMm3pJ02k2lei4jYy0OjyBcYyjAmQO/MnLtAOBMdQLoXZ/CIrGPquCb+1KEA4dLMsgsUceb0gCdAQPUc719eXBlc+7qH6dsbK4QPCz6OhZ4AAAAASUVORK5CYII=
```
| Key        | Value Detail |
|:-----------|:-----------------------------------------|
| `datalen=` | Integer length of `data` data value which follows (as ASCII numbers)
| `data=`    | PNG file data, Base64 encoded
| `width=`   | Maximum pixel width of each glyph
| `height=`  | Maximum pixel height of each glyph

A 1bit B+W PNG image contains a fixed-size sprite sheet of the individual glyphs.
If the glyphs themselves are narrower than the width their pixels are left justified.


## Kerning Pairs (optional)

```
To      -2
Te      -4
```

Kerning pairs may be specified, one line per pair with: two characters, whitespace and the offset.

## Tracking info (optional)

| Key        | Value Detail |
| `tracking=`| Number of pixels of horizontal whitespace between glyphs within a string. Defaults to 1


## CAPS Metadata (optional)

```
--metrics={"baseline":10,"xHeight":0,"capHeight":0,"pairs":{"Te":[-6,0]},"left":[],"right":[]}```
```

The metrics line embeds a JSON object in a lua-style comment to store relevant CAPS editor metadata.
This data is ignored by `pdc`.
The [baseline](https://en.wikipedia.org/wiki/Baseline_(typography)),
[xHeight](https://en.wikipedia.org/wiki/X-height) and
[capHeight](https://en.wikipedia.org/wiki/Cap_height)
are displayed while using the Caps Glyph editor, `left` and `right` contain an array of strings where
each string includes a list of characters which have equivalent left or right-most columns and thus
will use identical kerning information.  The pairs object includes kerning pairs specified by the
Caps "Auto-Kern" functionality.
