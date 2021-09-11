A file with the `.pdv` extension represents a 1-bit video that has been converted by `1bitvideo.app`. This format uses little endian byte order.

## Header

| Offset | Type     | Detail |
|:-------|:---------|:-------|
| `0`    | `chr[16]` | Ident "Playdate VID", with null padding at the end |
| `16`   | `int16` | Number of frames |
| `18`   | `int16` | Reserved, always 0 |
| `20`   | `float32` | Framerate, measured in frames per second |
| `24`   | `int16` | Frame width |
| `26`   | `int16` | Frame height |
| `28`   | `int32` | Unknown, seen as 1 |

In 1bitvideo.app the frame width and height seem to be hardcoded to `400` and `240` respectively, at least at the time of writing.

## Frame Table

Following the header is a series of `int32` values, one for each frame. These values contain the frame data offset as well as the frame type:

| Value | Detail |
|:------|:-------|
| `value >> 2` | Offset |
| `value & 0x3` | Frame type |

The offset actually represents the offset at the *end* of the compressed frame data, and is relative to the start of the frame data section.

The type will be `1` for an [I-frame](https://en.wikipedia.org/wiki/Video_compression_picture_types), and `2` for a [P-frame](https://en.wikipedia.org/wiki/Video_compression_picture_types). This seems to be the frame type for the *next* frame in the list, and the first frame in the video is assumed to always be an I-frame. I-frames can be decoded and displayed as-is, whereas P-frames need to be [merged](#p-frames) with the previous frames to get a complete image.

## Frame Data

Frame data begins immediately after the frame table. Each frame is z-lib compressed separately. Decompressed, the frame contains a 1-bit pixel map where `0` = black and `1` = white.

### P-frames

P-frames (frames that are based on previous frames) only store the pixel value changes since the previous frame. These can be resolved by looping through each pixel in the frame and doing a logical XOR against the same pixel from the previous frame.

For example in C this would be something like:

```c
for(int i = 0; i < sizeof(frame); i++)
{
  frame[i] ^= prevFrame[i];
}
```