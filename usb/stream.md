# The `stream` protocol

When `stream enable` is sent over serial, the Playdate enters streaming mode, used by Playdate Mirror.
In this mode, the device continuously reports the state of its screen, audio engine, buttons, and crank over serial, using a special protocol to do so.

(As with all Playdate formats, all numbers reported using the protocol are little-endian.)

### Entering, exiting, and maintaining streaming mode
If the Playdate has been in streaming mode for over one second without a `stream poke` command sent over USB, it will stop reporting data.
However, it won't completely exit streaming mode -- any future `stream enable` will *not* resend the entire screen afterward.

To exit streaming mode, send `stream disable` via serial.

### Stream messages
While the Playdate is streaming, it will report data in short messages.
The general format of one of these messages is:

| **Offset** | **Data type** | **Content** |
|:-----|:-----|:-----|
| 0 | `uint16` | Message type (see below) |
| 2 | `uint16` | Payload length in bytes |

The actual payload data follows this 4-byte header.

### Audio control
To control how audio is reported, there are three options you can send during streaming mode.
(The format the samples are parsed with isn't actually changed until the format switch is acknowledged with a stream message!)

| **Command** | **Meaning** |
|:-----|:-----|
| `stream a+` | Switch to stereo signed 16-bit PCM audio |
| `stream am` | Switch to mono signed 16-bit PCM audio |
| `stream a-` | Don't send any audio (the default) |

## Message types

### `0x0001`: Input state
Reports the state of the Playdate's buttons and crank every frame.

| **Payload offset** | **Data type** | **Content** |
|:-----|:-----|:-----|
| 0 | `uint16` | Button flags (see below) |
| 2 | `uint16` | Unknown: Seems to change erratically |
| 4 | `float` | Crank angle in degrees |

#### Button flags
| **Bitmask** | **Meaning** |
|:-----|:-----|
| `flags & 0x0001` | If `> 0`, d-pad left button is pressed |
| `flags & 0x0002` | If `> 0`, d-pad right button is pressed |
| `flags & 0x0004` | If `> 0`, d-pad up button is pressed |
| `flags & 0x0008` | If `> 0`, d-pad down button is pressed |
| `flags & 0x0010` | If `> 0`, B button is pressed |
| `flags & 0x0020` | If `> 0`, A button is pressed |
| `flags & 0x0040` | If `> 0`, Menu button is pressed |

### `0x000A`: New frame (no delay)
Starts a new frame as fast as possible, with no delay from the previous frame.

### `0x000B`: End frame
Ends the current frame. In the official Mirror app, this flips the framebuffer to make it visible on-screen.

### `0x000C`: Update screen line
Signals that a single horizontal line of the display was updated.

Only the lines that have changed since the last frame are sent, unless the current frame is the first one.
In that case, the entire screen is sent as 240 line update messages.

| **Payload offset** | **Data type** | **Content** |
|:-----|:-----|:-----|
| 0 | `uint8` | Line number that was updated (starting at one and bit-reversed, so line 0 becomes `0b10000000 == 0x80`) |
| 1 | `50 bytes` | Line data, left to right, with the least significant bit coming first in each byte |
| 51 | `uint8` | Zero byte to pad the length to a multiple of 4 bytes |

### `0x000D`: New frame (with delay)
Starts a new frame a certain amount of time since the previous frame started.

| **Payload offset** | **Data type** | **Content** |
|:-----|:-----|:-----|
| 0 | `uint32` | Milliseconds since the start of the previous frame |

### `0x0014`: Audio frames (multiple)
Sends one or multiple audio frames to buffer for playback.

The data format is signed 16-bit PCM, with the left channel of each sample coming first.
(If the audio format is mono, then the right channel will be zero.)

### `0x0015`: Audio format switch acknowledge
Signals that a requested change in audio formats has taken place.

| **Payload offset** | **Data type** | **Content** |
|:-----|:-----|:-----|
| 0 | `uint16` | Audio format flags (see below) |

#### Audio format flags
| **Bitmask** | **Meaning** |
|:-----|:-----|
| `flags & 0x0001` | If `> 0`, audio is enabled |
| `flags & 0x0002` | If `> 0`, audio has two channels |

### `0x0016`: Audio frames (fill single)
Sends one audio sample to continuously play until more data is received. This usually denotes silence.

Like with type `0x0014`, the data format is signed 16-bit PCM, with the left channel of the sample coming first.
