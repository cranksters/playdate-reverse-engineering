# based on https://gist.github.com/zhuowei/666c7e6d21d842dbb8b723e96164d9c3
# PDZ docs: https://github.com/jaames/playdate-reverse-engineering/blob/main/formats/pdz.md

from sys import argv
from os import path, makedirs
from struct import unpack
from zlib import decompress

if (len(argv) < 3):
  print('pdz.py')
  print('Unpack a Playdate .pdz executable file archive')
  print('Usage:')
  print('python3 pdz.py input.pdz output_directory')
  exit()

file_types = {
  1: 'luac',
  2: 'pdi',
  3: 'pdt',
  4: 'unknown',
  5: 'pda',
  6: 'str',
  7: 'pft',
}

def readcstr(dat, ptr):
  return dat[ptr:dat.find(b"\0", ptr)]

with open(argv[1], 'rb') as pdz:
  data = pdz.read()
  ptr = 0x10
  while ptr < len(data):
    flags = data[ptr]
    is_compressed = (flags >> 7) & 0x1
    innerlen = data[ptr + 1] | (data[ptr + 2] << 8)
    filename = readcstr(data, ptr + 4)
    outerheadersize = 4 + len(filename) + 1
    outerheadersize = ((ptr + outerheadersize + 3) & ~3) - ptr
    zlibdata = data[ptr + outerheadersize + 4: ptr + outerheadersize + innerlen]
    filename_s = argv[2] + '/' + filename.decode('utf-8') + '.' + file_types[flags & 0xF]

    print(filename_s)

    if "/" in filename_s:
      makedirs(path.dirname(filename_s), exist_ok=True)
    with open(filename_s, 'wb') as outfile:
      if flags == 133:
        outfile.write(zlibdata)
      else:
        outfile.write(decompress(zlibdata))

    ptr += outerheadersize + innerlen

