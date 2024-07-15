# based on https://gist.github.com/zhuowei/666c7e6d21d842dbb8b723e96164d9c3
# PDZ docs: https://github.com/jaames/playdate-reverse-engineering/blob/main/formats/pdz.md

from sys import exit
from os import path, makedirs
from struct import pack, unpack
from zlib import decompress
from argparse import ArgumentParser

PDZ_IDENT = b'Playdate PDZ'
FILE_TYPES = {
  1: 'luac',
  2: 'pdi',
  3: 'pdt',
  4: 'pdv',
  5: 'pda',
  6: 'pds',
  7: 'pft',
}
FILE_IDENTS = {
  'pdi': b'Playdate IMG',
  'pdt': b'Playdate IMT',
  'pdv': b'Playdate IMT',
  'pda': b'Playdate AUD',
  'pds': b'Playdate STR',
  'pft': b'Playdate FNT'
}

class PlaydatePdz:
  @classmethod
  def open(cls, path):
    with open(path, "rb") as buffer:
      return cls(buffer)

  def __init__(self, buffer):
    self.buffer = buffer
    self.entries = {}
    self.num_entries = 0
    self.read_header()
    self.read_entries()

  def read_header(self):
    self.buffer.seek(0)
    magic = self.buffer.read(16)
    magic = magic[:magic.index(b'\0')] # trim null bytes
    assert magic == PDZ_IDENT, 'Invalid PDZ file ident'
    self.buffer.seek(12)
    flags = unpack('<I', self.buffer.read(4))[0]
    is_encrypted = (flags & 0x40000000) > 0
    assert not is_encrypted, 'PDZ file is encrypted'

  def read_string(self):
    res = b''
    while True:
      char = self.buffer.read(1)
      if char == b'\0': break
      res += char
    return res.decode()

  def read_entries(self):
    self.buffer.seek(0, 2)
    ptr = 0x10
    pdz_len = self.buffer.tell()
    self.buffer.seek(ptr)
    while ptr < pdz_len:
      head = unpack('<I', self.buffer.read(4))[0]
      flags = head & 0xFF
      entry_len = (head >> 8) & 0xFFFFFF
      # doesn't seem to be any other flags
      is_compressed = (flags >> 7) & 0x1
      file_type = FILE_TYPES[flags & 0xF]
      # file name is a null terminated string
      file_name = self.read_string()
      # align offset to next nearest multiple of 4
      self.buffer.seek((self.buffer.tell() + 3) & ~3)
      # .pda files have two more values after filename before data
      if file_type == 'pda':
        entry_len -= 4
        audio_info = unpack('<I', self.buffer.read(4))[0]
        audio_rate = audio_info & 0xFFFFFF
        audio_format = (audio_info >> 24) & 0xFF 
      # if compression flag is set, there's another uint32 with the decompressed size
      if is_compressed:
        decompressed_size = unpack('<I', self.buffer.read(4))[0]
        entry_len -= 4
      else:
        decompressed_size = entry_len

      data = self.buffer.read(entry_len)
      ptr = self.buffer.tell()
      
      self.num_entries += 1
      self.entries[file_name] = {
        'name': file_name,
        'type': file_type,
        'data': data,
        'size': entry_len,
        'compressed': is_compressed,
        'decompressed_size': decompressed_size
      }
      if file_type == 'pda':
        self.entries[file_name].update({
          'audio_rate': audio_rate, 
          'audio_format': audio_format})
  
  def get_entry_data(self, name):
    assert name in self.entries
    entry = self.entries[name]
    if entry['compressed']:
      return decompress(entry['data'])
    return entry['data']
  
  def construct_entry_header(self, name):
    # this is probably incorrect, use at your own risk
    assert name in self.entries
    entry = self.entries[name]
    file_type = entry['type']
    is_compressed = entry['compressed']
    assert file_type in ['pdi','pdt','pdv','pda','pds','pft']
    ident = FILE_IDENTS[file_type]
    if file_type == 'pda':
      rate = entry['audio_rate']
      fmt = entry['audio_format']
      audio_info = (fmt << 24) + rate
      header = pack('<12sI', ident, audio_info)
    else:
      flags = 0x80000000 if is_compressed else 0x00000000
      header = pack('<12sI', ident, flags)
    return header

  def save_entry_data(self, name, outdir, gen_header):
    assert name in self.entries
    print(f'processing entry: {name}')
    entry = self.entries[name]
    file_type = entry['type']
    data = self.get_entry_data(name)
    filepath = outdir + '/' + entry['name'] + '.' + entry['type']
    if '/' in filepath:
      makedirs(path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as outfile:
      if gen_header and file_type in ['pdi','pdt','pdv','pda','pds','pft']:
        hdr = self.construct_entry_header(name)
        outfile.write(hdr)
      outfile.write(data)

  def save_entries(self, outdir, gen_header):
    for name in self.entries:
      self.save_entry_data(name, outdir, gen_header)

  def print_entries(self):
    for name in self.entries:
      print(f'{name}: {self.entries[name]["type"]}')

if __name__ == "__main__":
  parser = ArgumentParser(prog="pdz.py", description="Extract contents of a pdz file.")
  parser.add_argument("-o", "--outdir", default="pdz_output", help="output directory", dest="out_dir")
  parser.add_argument("-i", "--infile", help="input file", dest="in_file", required=True)
  parser.add_argument("-l", "--list-files", help="print a list of all entries in the file, ignoring all other arguments",
                      dest="list_files", required=False, action="store_true")
  parser.add_argument("-g", "--gen-headers", help="generate file headers for pd* files (experimental, default=false)" , 
                      dest="gen_headers", required=False, action="store_true")
  parser.add_argument("-f", "--extract-file", help="extract the given file(s), or all if this arg isn't provided",
                      dest="file_list", required=False, action="append")
  args = parser.parse_args()

  pdz = PlaydatePdz.open(args.in_file)
  
  if args.list_files:
    pdz.print_entries()
    exit()
  
  if args.file_list:
    for f in args.file_list:
      pdz.save_entry_data(f, args.out_dir, args.gen_headers)
  else:
    pdz.save_entries(args.out_dir, args.gen_headers)
