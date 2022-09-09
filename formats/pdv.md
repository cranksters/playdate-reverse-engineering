A file with the `.pdv` extension represents a 1-bit video that has been converted by `1bitvideo.app`. This format uses little endian byte order.

## Header

| Offset | Type     | Detail |
|:-------|:---------|:-------|
| `0`    | `chr[16]` | Ident "Playdate VID", with null padding at the end |
| `16`   | `uint16` | Number of frames |
| `18`   | `uint16` | Reserved, always 0 |
| `20`   | `float32` | Framerate, measured in frames per second |
| `24`   | `uint16` | Frame width |
| `26`   | `uint16` | Frame height |

In 1bitvideo.app the frame width and height seem to be hardcoded to `400` and `240` respectively, at least at the time of writing.

## Frame Table

Following the header is a series of `uint32` values, one for each frame, and one additional to mark the end of the data.  So if the number of frames is 16, there will be 17 entries in this table. These values contain the frame data offset as well as the frame type:

| Value | Detail |
|:------|:-------|
| `value >> 2` | Offset |
| `value & 0x3` | Frame type |

### Frame Types

| Type | Detail |
|:-----|:-------|
| `0`  | No frame |
| `1`  | [I-frame](https://en.wikipedia.org/wiki/Video_compression_picture_types) |
| `2`  | [P-frame](https://en.wikipedia.org/wiki/Video_compression_picture_types) |
| `3`  | Combined I-frame and P-frame |

A `0` type frame is placed at the end to identify where the preceeding frame's
data ends. There is no actual data following it.

## Frame Data

Frame data begins immediately after the frame table. Each frame is z-lib compressed separately. Decompressed, the frame contains a 1-bit pixel map where `0` = black and `1` = white.

### P-frames

Frame type 2 is for P-frames (frames that are based on previous frames), and these only store the pixels that have changed since the previous frame. The full image can be resolved by looping through each pixel in the frame and doing a logical XOR against the same pixel from the previous resolved frame.

For example in C this would be something like:

```c
for (int i = 0; i < sizeof(frame); i++)
{
  frame[i] ^= prevFrame[i];
}
```

### Combined I-frame and P-frame

Frame type 3 contains both I-frame and P-frame data for the same frame. This is so you can step backwards from an I-frame without having to jump to the previous I-frame then apply P-frames all the way forward. 

The frame data for this frame will start with an `uint16` giving the length of the I-frame data, followed by the I-frame data, and then the P-frame data.
