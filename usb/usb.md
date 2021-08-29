> ⚠️ I am not so experienced with USB, so I might be missing details or using incorrect terminology here. If you have any suggestions or corrections, please open an issue thread!

When connected to USB and unlocked, the Playdate provides a kind of command line interface via USB bulk transfers. Commands are sent as ascii text via bulk out and must end in a newline character (`\n`), and the response is received via bulk in. Some commands (such as `button` or `stream enable`) will cause the Playdate to continually send data via bulk in until another command is sent to cancel it, other commands (for example, `bitmap`) may require extra binary data to be sent after the command text.

Some of these commands are used by Playdate Simulator for features like "preview bitmap" or "run pdx". If you want to play around with these, and you use a browser that supports WebUSB, you should check out my [playdate-usb](https://github.com/jaames/playdate-usb) library.

## USB commands

Running  `help` will return a very helpful list of the available commands:

```
The following commands are available:
Telnet commands:
 help        Displays all available commands or individual help on each command
CPU Control:
 serialread  Print the device serial number
 trace       trace_<delay>. (trace 10)
 stoptrace   stoptrace
 bootdisk    reboot into recovery segment USB disk
 datadisk    reboot into data segment USB disk
 formatdata  format data disk
 settime     sets the RTC. format is ISO8601 plus weekday (1=mon) e.g.: 2018-03-20T19:58:29Z 2
 gettime     reads the RTC
 vbat        get battery voltage
 batpct      get battery percentage
 temp        get estimated ambient temperature
 dcache      dcache <on/off>: turn dcache on or off
 icache      icache <on/off>: turn icache on or off
Firmware Update:
 fwup        fwup [bundle_path]
Runtime control:
 echo        echo (on|off): turn console echo on or off
 buttons     Test buttons & crank
 btn         btn <btn>: simulate a button press. +a/-a/a for down/up/both
 changecrank changecrank +-<degrees>
 dockcrank   simulates crank docking
 enablecrank Reenables crank updates
 disablecrank Disables crank updates
 accel       simulate accelerometer change
 screen      Dump framebuffer data (400x240 bits)
 bitmap      Send bitmap to screen (followed by 400x240 bits)
 controller  start or stop controller mode
 eval        execute a compiled Lua function
 run         run <path to pdx>: Run the named program
 luatrace    Get a Lua stack trace
 stats       Display runtime stats
 autolock    autolock <always|onBattery|never>
 version     Display build target and SDK version
 memstats    memstats
Stream:
 stream      stream <enable|disable|poke>
ESP functions:
 espreset    reset the ESP chip
 espoff      turn off the ESP
 espbootlog  get the ESP startup log
 espfile     espfile <path> <address> <md5> <uncompressed size>: add the given file to the upload list. If <uncompressed size> is added then the file is assumed to be compressed.
 espflash    espflash <baud> [0|1] send the files listed with the espfile command to the ESP flash.
 espbaud     espbaud <speed> [cts]
 esp         esp <cmd>: Forward a command to the ESP firmware, read until keypress
```

Most of these commands are self-explanatory, so I will just detail some of the interesting/different ones. Please note these were run on an older Playdate Developer Preview unit, so there may be some differences with the final units that get shipped to the public.

### `buttons`

Begins button-testing mode causes the device to begin continually writing the current control state to USB bulk in, at approximately 50 times per second. This can be stopped by sending a newline to the device.

Each new state will be written as a single line with the following structure:

```
buttons:XX XX XX crank:X.X docked:X
```

`button` gives three hex-formatted numbers containing the current button state. The first number indicates which buttons are currently pressed, the second indicates which buttons were pressed after the last update, and the third indicates which buttons were released after the last update. These should be treated as bitflags:

| Button | Bitmask |
|:-------|:--------|
| a      | `0x1`    |
| b      | `0x2`    |
| up     | `0x4`    |
| down   | `0x8`    |
| left   | `0x10`   |
| right  | `0x20`   |
| menu   | `0x40`   |
| lock   | `0x80`   |

`crank` gives the crank angle as a floating point number, measured in degrees, with `0` being the 12 o'clock position.

`docked` will be `0` if the crank is not docked, or `1` if docked.

### `screen`

Gets the current screen buffer as a 1-bit array of pixels. The data returned from the Playdate will begin with an 11-byte string `\r\nscreen~:\n`, followed by 12000 bytes of bitmap data where each bit of every byte represents one pixel; `0` for black, `1` for white. 

### `bitmap`

Sends a 1-bit bitmap to be previewed on the Playdate screen. The command must begin with a 7-byte command string `bitmap\n`, followed by 12000 bytes of bitmap data where each bit of every byte represents one pixel; `0` for black, `1` for white. 

### `run`

Launches a .pdx rom from the Playdate's data partition. The game path must begin with a forward slash, e.g `run /System/Crayons.pdx`.

### `stats`

Example output:

```
~stats:
frame count: 194503
frame time: 0.000977
gc time: 0.016602
disp time: 18
current time: 9855691
mem alloced: 403288
mem reserved: 460448
mem total: 16645684
kernel: 0.1%
serial: 0.0%
game: 2.5%
GC: 35.2%
wifi: 0.0%
trace: 0.0%
audio: 0.2%
```

### `version`

Example output:

```
~version:
target=DVT1
build=3f1ccd8bb42e-1.3.1-release.119347-buildbot-20210818_165619
boot_build=3f1ccd8bb42e-1.3.1-release.119347-buildbot
SDK=1.3.1
pdxversion=10200
serial#=<REDACTED>
cc=9.2.1 20191025 (release) [ARM/arm-9-branch revision 277599]
```

### `esp`

Using the `esp <cmd>` command will forward an [ESP-AT](https://docs.espressif.com/projects/esp-at/en/latest/Get_Started/What_is_ESP-AT.html) command to the ESP32 firmware. Please note that these commands can potentially be very dangerous and may even damage your Playdate, so only mess with this stuff if you're stupid (me) or know what you're doing (not me). In the event that you do goof something up, you may be able to recover by holding down the Playdate's secret power/reset button, which is hidden in the cavity where the crank handle goes when it's docked. Have paperclips on standby!

After sending an ESP-AT command, you need to continue reading from the device until you receive a line that contains `OK` or `ERROR` to get the full response.

I can't profess to be very experienced here, so I didn't poke to deeply. However here's the results of some of the commands I tried:

[**`AT+GMR`**](https://docs.espressif.com/projects/esp-at/en/latest/AT_Command_Set/Basic_AT_Commands.html#at-gmr-check-version-information):

Version information:

```
AT version:2.0.0.0-dev(b6850a4 - Oct 24 2019 12:10:13)
SDK version:v3.3-beta3-170-g91f29bef17
compile time(e9c8abb):Aug 18 2021 16:58:09
```

[**`AT+CMD?`**](https://docs.espressif.com/projects/esp-at/en/latest/AT_Command_Set/Basic_AT_Commands.html#at-cmd-list-all-at-commands-and-types-supported-in-current-firmware):

Querying supported commands doesn't seem to be supported.

[**`AT+UART_CUR?`**](https://docs.espressif.com/projects/esp-at/en/latest/AT_Command_Set/Basic_AT_Commands.html#at-uart-cur-current-uart-configuration-not-saved-in-flash):

Current UART configuration:

```
+UART_CUR:2534653,8,1,0,3
```

[**`AT+SYSFLASH?`**](https://docs.espressif.com/projects/esp-at/en/latest/AT_Command_Set/Basic_AT_Commands.html#at-sysflash-query-set-user-partitions-in-flash):

Querying user partitions in ESP flash:

```
AT+SYSFLASH?
+SYSFLASH:"ble_data",64,1,0x21000,0x3000
+SYSFLASH:"server_cert",64,2,0x24000,0x2000
+SYSFLASH:"server_key",64,3,0x26000,0x2000
+SYSFLASH:"server_ca",64,4,0x28000,0x2000
+SYSFLASH:"client_cert",64,5,0x2a000,0x2000
+SYSFLASH:"client_key",64,6,0x2c000,0x2000
+SYSFLASH:"client_ca",64,7,0x2e000,0x2000
+SYSFLASH:"factory_param",64,8,0x30000,0x1000
+SYSFLASH:"wpa2_cert",64,9,0x31000,0x2000
+SYSFLASH:"wpa2_key",64,10,0x33000,0x2000
+SYSFLASH:"wpa2_ca",64,11,0x35000,0x2000
+SYSFLASH:"mqtt_cert",64,12,0x37000,0x2000
+SYSFLASH:"mqtt_key",64,13,0x39000,0x2000
+SYSFLASH:"mqtt_ca",64,14,0x3b000,0x2000
+SYSFLASH:"fatfs",1,129,0x70000,0x90000
```

Most partitions don't seem to be readable, however you can for example dump the client CA cert by doing `AT+SYSFLASH=2,"client_ca",0,0x2000`.

[**`AT_FS`**](https://docs.espressif.com/projects/esp-at/en/latest/AT_Command_Set/Basic_AT_Commands.html#esp32-only-at-fs-filesystem-operations):

No file system commands seem to be supported.