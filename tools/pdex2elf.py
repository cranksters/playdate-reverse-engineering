from sys import argv
from struct import pack

if (len(argv) < 3):
  print('pdex2elf.py')
  print('convert a Playdate pdex.bin to an ELF file for analysis')
  print('Usage:')
  print('python3 pdex2elf.py input.pdex output.elf')
  exit()

with open(argv[1], 'rb') as pdex, open(argv[2], 'wb') as elf:
  pdexData = pdex.read()

  # file header
  # file magic
  elf.write(b'\x7FELF')
  # 32 bit, little endian, version 1, null platform
  elf.write(bytes([1, 1, 1, 0]))
  # EI_ABIVERSION = 0, 7 null bytes 
  elf.write(bytes([0, 0, 0, 0, 0, 0, 0, 0]))
  # e_type = ET_EXEC, e_machine = 0x28 (ARM)
  elf.write(pack('<HH', 2, 0x28))
  # e_version 1
  elf.write(pack('<I', 1))
  # e_entry
  elf.write(pack('<I', 1610612768))
  # e_phoff
  elf.write(pack('<I', 0x34))
  # e_shoff
  elf.write(pack('<I', 195100))
  # e_flags
  elf.write(bytes([0x00, 0x04, 0x00, 0x05]))
  # e_ehsize, e_phentsize
  elf.write(pack('<HH', 0x34, 0x20))
  # e_phnum, e_shentsize
  elf.write(pack('<HH', 0x1, 0x28))
  # e_shnum, e_shstrndx
  elf.write(pack('<HH', 0x32, 0x31))

  # program header
  # p_type = 1 (PT_LOAD)
  elf.write(pack('<I', 1))
  # p_offset
  elf.write(pack('<I', 65536))
  # p_vaddr, p_paddr
  elf.write(pack('<II', 1610612736, 1610612736))
  # p_filesz
  elf.write(pack('<I', len(pdexData)))
  # p_memsz
  elf.write(pack('<I', len(pdexData) + 72)) # TODO: not sure how this is actually calculated
  # p_flags
  elf.write(pack('<I', 7))
  # p_align
  elf.write(pack('<I', 65536))

  # padding until @65536 (why?)
  elf.write(bytes(65536 - elf.tell()))
  # pdex data
  elf.write(pdexData)