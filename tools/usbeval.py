if (len(argv) < 2):
  print('usbeval.py')
  print('Evaluates a Lua script on a Playdate device, via USB')
  print('Requires pdc from the Playdate SDK as well as the pyusb library')
  print('Usage:')
  print('python3 usbeval.py ./input.lua')
  exit()

import tempfile
import subprocess
import usb.core
import usb.util
from sys import argv
from pathlib import Path
from struct import unpack
from zlib import decompress
from time import sleep

# Playdate USB vendor and product IDs
PLAYDATE_VID = 0x1331;
PLAYDATE_PID = 0x5740;
IN_SIZE = 64;

def pdz_extract_entry(data, entry):
  ptr = 0x10
  while ptr < len(data):
    flags = data[ptr]
    is_compressed = (flags >> 7) & 0x1
    innerlen = data[ptr + 1] | (data[ptr + 2] << 8)
    filename = data[ptr + 4 : data.find(b"\0", ptr + 4)]
    outerheadersize = 4 + len(filename) + 1
    outerheadersize = ((ptr + outerheadersize + 3) & ~3) - ptr
    zlibdata = data[ptr + outerheadersize + 4: ptr + outerheadersize + innerlen]
    if filename.decode('utf-8') == entry:
      return decompress(zlibdata)
    ptr += outerheadersize + innerlen
  return None

def usb_connect():
  # find our playdate device
  device = usb.core.find(idVendor=PLAYDATE_VID, idProduct=PLAYDATE_PID)
  if device is None:
    raise ValueError('Device not found')

  # set the active configuration. With no arguments, the first
  # configuration will be the active one
  device.set_configuration()

  # get an endpoint instance
  cfg = device.get_active_configuration()
  intf = cfg[(1,0)]

  epOut = usb.util.find_descriptor(
      intf,
      # match the first OUT endpoint
      custom_match = \
      lambda e: \
          usb.util.endpoint_direction(e.bEndpointAddress) == \
          usb.util.ENDPOINT_OUT)

  epIn = usb.util.find_descriptor(
      intf,
      # match the first IN endpoint
      custom_match = \
      lambda e: \
          usb.util.endpoint_direction(e.bEndpointAddress) == \
          usb.util.ENDPOINT_IN)

  assert epOut is not None
  assert epIn is not None
  device.reset()
  return epOut, epIn

def usb_read_bytes(endPoint):
  res = bytearray()
  has_started = False
  while True:
    try:
      b = bytearray(epIn.read(IN_SIZE))
      res += b
      if b != b'': has_started = True
      if has_started and b == b'': break
    except usb.core.USBTimeoutError:
     break
  return res

with tempfile.NamedTemporaryFile(prefix='main', suffix='.lua') as luafile, tempfile.TemporaryDirectory(suffix='.pdx') as pdxdir:

  # copy lua file
  print('reading input file')
  with open(argv[1], 'rb') as infile:
    luafile.write(infile.read())
    luafile.seek(0)

  # compile lua with pdc
  print('compiling lua with pdc')
  subprocess.run(['pdc', luafile.name, pdxdir])
  luastem = Path(luafile.name).stem

  # extract lua bytecode from pdz
  print('extracting lua bytecode')
  with open(Path(pdxdir, luastem + '.pdz'), 'rb') as pdzfile:
    pdz = pdzfile.read()
    bytecode = pdz_extract_entry(pdz, luastem)

  # connect to playdate over usb 
  print('finding playdate connected to usb...')
  epOut, epIn = usb_connect()
  print('successfully connected to playdate!')

  # set usb echo mode to off
  print('setting usb echo to off')
  epOut.write('echo off\n')
  resp = usb_read_bytes(epIn)

  # get version info (to test things work, but also looks cool :^))
  # print('playdate version info:')
  # epOut.write('version\n')
  # resp = usb_read_bytes(epIn)
  # print(resp.decode("utf-8").strip())

  # consume printed console content until there's nothing new
  print('clearing current console data')
  epOut.write('eval\n')
  sleep(.2)
  usb_read_bytes(epIn)
  
  # send lua bytecode to the device
  print('sending payload for device to eval...')
  header = b'eval %d\n' % len(bytecode)
  payload = header + bytecode
  epOut.write(payload)
  sleep(.2) # payload seems to take a bit to execute, you may need to adjust this if you have a big payload
  resp = usb_read_bytes(epIn)
  print('===============')
  print('console output:')
  print(resp.decode("utf-8").strip())

  # keep polling for new console output
  while True:
    try:
      sleep(.1)
      resp = usb_read_bytes(epIn)
      text = resp.decode("utf-8").strip()
      if text: print(text)
    except KeyboardInterrupt:
      break