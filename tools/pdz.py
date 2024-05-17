# based on https://gist.github.com/zhuowei/666c7e6d21d842dbb8b723e96164d9c3
# PDZ docs: https://github.com/jaames/playdate-reverse-engineering/blob/main/formats/pdz.md

from os import path, makedirs
from struct import unpack
from zlib import decompress

PDZ_IDENT = b'Playdate PDZ'
FILE_TYPES = {
  1: 'luac',
  2: 'pdi',
  3: 'pdt',
  4: 'pdv',
  5: 'pda',
  6: 'str',
  7: 'pft',
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
        audio_type = (audio_info >> 24) & 0xFF 
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
        self.entries[file_name].update( {
          'audio_rate': audio_rate, 
          'audio_type': audio_type
        } )
      
  def get_entry_data(self, name):
    assert name in self.entries
    entry = self.entries[name]
    if entry['compressed']:
      return decompress(entry['data'])
    return entry['data']

  def save_entry_data(self, name, outdir):
    assert name in self.entries
    entry = self.entries[name]
    data = self.get_entry_data(name)
    filepath = outdir + '/' + entry['name'] + '.' + entry['type']
    if '/' in filepath:
      makedirs(path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as outfile:
      outfile.write(data)

  def save_entries(self, outdir):
    for name in self.entries:
      self.save_entry_data(name, outdir)

if __name__ == "__main__":
  from sys import argv

  if (len(argv) < 3):
    print('pdz.py')
    print('Unpack a Playdate .pdz executable file archive')
    print('Usage:')
    print('python3 pdz.py input.pdz output_directory')
    exit()

  pdz = PlaydatePdz.open(argv[1])
  pdz.save_entries(argv[2])
