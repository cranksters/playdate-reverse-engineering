## USB commands in unlocked mode

This is the output of running `help` on a Playdate with firmware 1.10 after running `unlock`:

```
The following commands are available:

Telnet commands:
 help        Displays all available commands or individual help on each command
 loop        loop next command x times with delay y ms (eg loop 10 100 help)
 lock        Lock the firmware command interface

eMMC kvstore:
 kvget       kvget <key> [len]
 kvput       kvput <key> <len>
 kvrm        kvrm <key>
 kvwipe      kvwipe

CPU Control:
 gpio        gpio <port> <i(pu/pd)/1(pu/pd)/0(pu/pd)>. (gpio A3 1 or gpio B2 ipu)
 i2cread     i2cread <unit> <address> <register> <len>. (i2cread 0 0x47 0x38 3)
 i2cwrite    i2cwrite <unit> <address> <register> <value>. (i2cwrite 3 0x47 0x38 0xff)
 tlv493read  tlv493read <address> <len>. (tlv493read 0x47 3)
 tlv493write tlv493write <address> <val>. (tlv493write 0x47 0x00 0x37 0x48)
 serialwrite serialwrite <string>
 serialread  Print the device serial number
 pwwrite     pwwrite <string>
 pwread      pwread
 reset       reset system
 dfu         reset system
 trace       trace_<delay>. (trace 10)
 stoptrace   stoptrace
 bootdisk    reboot into recovery segment USB disk
 datadisk    reboot into data segment USB disk
 sysdisk     reboot into system segment USB disk
 formatboot  format recovery disk
 formatdata  format data disk
 formatsys   format system disk
 shutdown    put device in stop mode
 cleartime   clear time from device
 settime     sets the RTC. format is ISO8601 plus weekday (1=mon) e.g.: 2018-03-20T19:58:29Z 2
 gettime     reads the RTC
 rtccalib    rtccalib <on/off>: enable rtc calibration output
 vbat        get battery voltage
 batpct      get battery percentage
 temp        get estimated ambient temperature
 peek        peek <addr>: Read a 32-bit value from memory
 poke        poke <addr> <value>: Write a 32-bit value int memory
 dump        dump <start> <end>: Dump memory in range [start-end) as bytes
 dumpw       dumpw <start> <end>: Dump memory in range [start-end) as words
 stop        stop cpu
 led         led <R> <G> <B>. (led 0-255 0-255 0-255)
 leddemo     leddemo
 charge      charge <on/off>: enables/disables battery charging
 readcharger readcharger
 burn        waste cpu to run down the battery
 lsedrive    get LSE drive level
 extv        get 5V_ext voltage
 dcache      dcache <on/off>: turn dcache on or off
 icache      icache <on/off>: turn icache on or off
 rcccsr      report bootinfo.rcccsr value
 rdp         rdp <enable/disable>
 suspendusb  sets USB current limit to 500uA

eMMC Control:
 emmctest    emmctest
 emmcinfo    emmcinfo
 emmcwipe    emmcwipe
 emmcdump    emmcdump <addr> <len>

Audio Control:
 audiotest   Send test data to audio output
 audiosweep  audiosweep <startfreq> <endfreq> <length>: Send sweep signal to audio output. Frequencies are (integer) Hz, length is milliseconds
 stopaudio   Stop audio output
 startaudio  Start audio output
 audioout    audioout <speaker|headphone|both|none|bt|onboard>
 mictest     mictest <int|ext> <filename> <length>: Record microphone to given file. length is in milliseconds
 blowtest    blowtest
 micbiastest micbiastest <level:0-5> <verbose:0/1>

Encryption:
 encrypt     encrypt <file_in> <file_out>
 decrypt     decrypt <file_in> <file_out>

Runtime control:
 echo        echo (on|off): turn console echo on or off
 buttons     Test buttons & crank
 btn         btn <btn>: simulate a button press. +a/-a/a for down/up/both
 changecrank changecrank +-<degrees>
 dockcrank   simulates crank docking
 enablecrank Reenables crank updates
 disablecrank Disables crank updates
 accel       simulate accelerometer change
 pause       Pause execution
 resume      Resume execution
 restart     Restart Lua runtime
 step        Step one frame
 fps         fps to return current frame rate, fps <frame rate> to set
 screen      Dump framebuffer data (400x240 bits)
 bitmap      Send bitmap to screen (followed by 400x240 bits)
 lcdtest     Draw a marching stripes pattern on the screen
 controller  start or stop controller mode
 eval        execute a compiled Lua function
 run         run <path to pdx>: Run the named program
 whatsrunning Returns the path of the currently running program
 luatrace    Get a Lua stack trace
 stats       Display runtime stats
 autolock    autolock <always|onBattery|never>
 version     Display build target and SDK version
 station     station <travel agent station name>: Configure device for running at the named station
 setvolume   setvolume <amt>:, 0-255
 getvolume   Returns the volume level 0-255
 wifi        wifi <GET|POST> <url> [file1] [file2]
 wifitest    wifitest <network> <password>
 memtest     memtest
 memstats    memstats
 woprset     woprset [server]
 woprget     woprget
 syncperiod  syncperiod <initial_s> [period_s]
 hibernate   hibernate

Filesystem Stuff:
 listfiles   listfiles path: list files at path
 getfile     getfile <path>: get file contents at path
 putfile     putfile <path> <size>: upload file to path
 mkdir       mkdir <path>
 delete      delete <path>
 rmdir       rmdir <path>: Recursively delete directory
 unzip       unzip zip_path out_path
 md5         md5 <file_path>

memio commands:
 memiomd5    memiomd5 <addr> <size>

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
 esptest     esptest <baud> <cts>
 espwipe     espwipe
 espversion  espversion
 wifiperf    wifiperf <addr> <port>
 wifistop    wifistop

Firmware Update:
 fw          fw
 fwup        fwup [bundle_path]
 recovery    recovery
 unstage     unstage

unzip test:
 unzipmem    unzipmem <addr> <len> <path>

Memfault Tests:
 hardfault   Trigger a hardfault
 assert      Trigger an assert
 mflt        mflt <status|clear|send>

```
