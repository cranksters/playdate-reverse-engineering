import argparse
import hashlib
import zlib

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='pdex2elf.py',
        description='Converts a Playdate pdex.bin file to an ELF file.'
    )
    parser.add_argument('pdex', help='the path to the input pdex.bin')
    parser.add_argument('elf', help='the path to the output ELF file')
    args = parser.parse_args()

    with open(args.pdex, 'rb') as pdex:
        pdex_magic = pdex.read(12)
        if pdex_magic in [b'Playdate PDX', b'Playdate BIN']:
            pdex_flags = int.from_bytes(pdex.read(4), byteorder='little')
            if pdex_flags & 0x40000000:
                raise ValueError('the specified pdex.bin is encrypted')
            pdex_version = '2.0'
            pdex_checksum = pdex.read(16)
            pdex_filesz = int.from_bytes(pdex.read(4), byteorder='little')
            pdex_memsz = int.from_bytes(pdex.read(4), byteorder='little')
            pdex_entry = int.from_bytes(pdex.read(4), byteorder='little')
            pdex_relnum = int.from_bytes(pdex.read(4), byteorder='little')
            pdex_data = zlib.decompress(pdex.read())
        else:
            pdex_entry = int.from_bytes(pdex_magic[:4], byteorder='little') - 0x6000000c
            pdex_filesz = int.from_bytes(pdex_magic[4:8], byteorder='little') - 0x6000000c
            pdex_memsz = int.from_bytes(pdex_magic[8:], byteorder='little') - 0x6000000c
            if pdex_entry < 0 or pdex_filesz < 0 or pdex_memsz < 0:
                raise ValueError('the specified file is not a pdex.bin')
            pdex_version = '1.0'
            pdex_magic = None
            pdex_flags = 0
            pdex_relnum = 0
            pdex_checksum = None
            pdex_data = pdex.read()

    print('pdex.bin info:')
    print('  Version:           {}'.format(pdex_version))
    if pdex_magic is not None:
        print('  File signature:    {}'.format(pdex_magic.decode()))
    print('  Flags:             {}'.format(pdex_flags))
    if pdex_checksum is not None:
        print('  Declared checksum: {}'.format(pdex_checksum.hex()))
        print('  Computed checksum: {}'.format(hashlib.md5(pdex_data[:pdex_filesz]).hexdigest()))
    print('  Entry point:       {}'.format(pdex_entry))
    print('  File size:         {}'.format(pdex_filesz))
    print('  Memory size:       {}'.format(pdex_memsz))
    print('  Relocations:       {}'.format(pdex_relnum))

    with open(args.elf, 'wb') as elf:
        text_index = 1
        text_addr = 0
        text_offset = 0x10000
        text_size = pdex_filesz

        bss_index = 2
        bss_addr = (pdex_filesz + 3) & ~3
        bss_offset = text_offset + bss_addr
        bss_size = pdex_memsz - pdex_filesz

        rel_text_index = 3
        rel_text_offset = bss_offset
        rel_text_size = pdex_relnum * 8

        symtab_index = 4
        symtab_offset = (rel_text_offset + rel_text_size + 3) & ~3
        symtab_size = 2 * 16

        strtab_index = 5
        strtab_data = b'\0'
        strtab_offset = symtab_offset + symtab_size
        strtab_size = len(strtab_data)

        shstrtab_index = 6
        shstrtab_data = b'\0.text\0.bss\0.rel.text\0.symtab\0.strtab\0.shstrtab\0'
        shstrtab_offset = strtab_offset + strtab_size
        shstrtab_size = len(shstrtab_data)

        sh_offset = (shstrtab_offset + shstrtab_size + 3) & ~3

        # ==== ELF header ====

        # e_ident[EI_MAG0..EI_MAG3]
        elf.write(b'\x7fELF')
        # e_ident[EI_CLASS]
        elf.write(b'\x01') # ELFCLASS32
        # e_ident[EI_DATA]
        elf.write(b'\x01') # ELFDATA2LSB
        # e_ident[EI_VERSION]
        elf.write(b'\x01') # EV_CURRENT
        # e_ident[EI_OSABI]
        elf.write(b'\x00') # ELFOSABI_SYSV
        # e_ident[EI_ABIVERSION]
        elf.write(b'\x00')
        # e_ident[EI_PAD..(EI_NIDENT - 1)]
        elf.write(b'\x00\x00\x00\x00\x00\x00\x00')
        # e_type
        elf.write(b'\x02\x00') # ET_EXEC
        # e_machine
        elf.write(b'\x28\x00') # EM_ARM
        # e_version
        elf.write(b'\x01\x00\x00\x00') # EV_CURRENT
        # e_entry
        elf.write(pdex_entry.to_bytes(4, byteorder='little'))
        # e_phoff
        elf.write(b'\x34\x00\x00\x00')
        # e_shoff
        elf.write(sh_offset.to_bytes(4, byteorder='little'))
        # e_flags
        elf.write(b'\x00\x04\x00\x05') # EF_ARM_EABI_VER5 | EF_ARM_ABI_FLOAT_HARD
        # e_ehsize
        elf.write(b'\x34\x00')
        # e_phentsize
        elf.write(b'\x20\x00')
        # e_phnum
        elf.write(b'\x01\x00')
        # e_shentsize
        elf.write(b'\x28\x00')
        # e_shnum
        elf.write(b'\x07\x00')
        # e_shstrndx
        elf.write(shstrtab_index.to_bytes(2, byteorder='little'))

        # ==== Program header ====

        # p_type
        elf.write(b'\x01\x00\x00\x00') # PT_LOAD
        # p_offset
        elf.write(text_offset.to_bytes(4, byteorder='little'))
        # p_vaddr
        elf.write(b'\x00\x00\x00\x00')
        # p_paddr
        elf.write(b'\x00\x00\x00\x00')
        # p_filesz
        elf.write(pdex_filesz.to_bytes(4, byteorder='little'))
        # p_memsz
        elf.write(pdex_memsz.to_bytes(4, byteorder='little'))
        # p_flags
        elf.write(b'\x07\x00\x00\x00') # PF_X | PF_W | PF_R
        # p_align
        elf.write(text_offset.to_bytes(4, byteorder='little'))

        # ==== .text section ====

        elf.write(b'\x00' * (text_offset - elf.tell()))

        elf.write(pdex_data[:pdex_filesz])

        # ==== .rel.text section ====

        elf.write(b'\x00' * (rel_text_offset - elf.tell()))

        for i in range(pdex_filesz, pdex_filesz + 4 * pdex_relnum, 4):
            # r_offset
            elf.write(pdex_data[i:(i + 4)])
            # r_info
            elf.write(b'\x02')
            elf.write(text_index.to_bytes(2, byteorder='little'))
            elf.write(b'\x00')

        # ==== .symtab section ====

        elf.write(b'\x00' * (symtab_offset - elf.tell()))

        # NULL
        # st_name
        elf.write(b'\x00\x00\x00\x00')
        # st_value
        elf.write(b'\x00\x00\x00\x00')
        # st_size
        elf.write(b'\x00\x00\x00\x00')
        # st_info
        elf.write(b'\x00') # STB_LOCAL, STT_NOTYPE
        # st_other
        elf.write(b'\x00')
        # st_shndx
        elf.write(b'\x00\x00')

        # .text
        # st_name
        elf.write(text_addr.to_bytes(4, byteorder='little'))
        # st_value
        elf.write(b'\x00\x00\x00\x00')
        # st_size
        elf.write(b'\x00\x00\x00\x00')
        # st_info
        elf.write(b'\x03') # STB_LOCAL, STT_SECTION
        # st_other
        elf.write(b'\x00')
        # st_shndx
        elf.write(text_index.to_bytes(2, byteorder='little'))

        # ==== .strtab section ====

        elf.write(strtab_data)

        # ==== .shstrtab section ====

        elf.write(shstrtab_data)

        # ==== Section headers ====

        elf.write(b'\x00' * (sh_offset - elf.tell()))

        # NULL
        # sh_name
        elf.write(b'\x00\x00\x00\x00')
        # sh_type
        elf.write(b'\x00\x00\x00\x00') # SHT_NULL
        # sh_flags
        elf.write(b'\x00\x00\x00\x00')
        # sh_addr
        elf.write(b'\x00\x00\x00\x00')
        # sh_offset
        elf.write(b'\x00\x00\x00\x00')
        # sh_size
        elf.write(b'\x00\x00\x00\x00')
        # sh_link
        elf.write(b'\x00\x00\x00\x00')
        # sh_info
        elf.write(b'\x00\x00\x00\x00')
        # sh_addralign
        elf.write(b'\x00\x00\x00\x00')
        # sh_entsize
        elf.write(b'\x00\x00\x00\x00')

        # .text
        # sh_name
        elf.write((shstrtab_data.index(b'\0.text\0') + 1).to_bytes(4, byteorder='little'))
        # sh_type
        elf.write(b'\x01\x00\x00\x00') # SHT_PROGBITS
        # sh_flags
        elf.write(b'\x37\x00\x00\x00') # SHF_WRITE | SHF_ALLOC | SHF_EXECINSTR | SHF_MERGE | SHF_STRINGS
        # sh_addr
        elf.write(text_addr.to_bytes(4, byteorder='little'))
        # sh_offset
        elf.write(text_offset.to_bytes(4, byteorder='little'))
        # sh_size
        elf.write(text_size.to_bytes(4, byteorder='little'))
        # sh_link
        elf.write(b'\x00\x00\x00\x00')
        # sh_info
        elf.write(b'\x00\x00\x00\x00')
        # sh_addralign
        elf.write(b'\x08\x00\x00\x00')
        # sh_entsize
        elf.write(b'\x00\x00\x00\x00')

        # .bss
        # sh_name
        elf.write((shstrtab_data.index(b'\0.bss\0') + 1).to_bytes(4, byteorder='little'))
        # sh_type
        elf.write(b'\x08\x00\x00\x00') # SHT_NOBITS
        # sh_flags
        elf.write(b'\x03\x00\x00\x00') # SHF_WRITE | SHF_ALLOC
        # sh_addr
        elf.write(bss_addr.to_bytes(4, byteorder='little'))
        # sh_offset
        elf.write(bss_offset.to_bytes(4, byteorder='little'))
        # sh_size
        elf.write(bss_size.to_bytes(4, byteorder='little'))
        # sh_link
        elf.write(b'\x00\x00\x00\x00')
        # sh_info
        elf.write(b'\x00\x00\x00\x00')
        # sh_addralign
        elf.write(b'\x04\x00\x00\x00')
        # sh_entsize
        elf.write(b'\x00\x00\x00\x00')

        # .rel.text
        # sh_name
        elf.write((shstrtab_data.index(b'\0.rel.text\0') + 1).to_bytes(4, byteorder='little'))
        # sh_type
        elf.write(b'\x09\x00\x00\x00') # SHT_REL
        # sh_flags
        elf.write(b'\x40\x00\x00\x00') # SHF_INFO_LINK
        # sh_addr
        elf.write(b'\x00\x00\x00\x00')
        # sh_offset
        elf.write(rel_text_offset.to_bytes(4, byteorder='little'))
        # sh_size
        elf.write(rel_text_size.to_bytes(4, byteorder='little'))
        # sh_link
        elf.write(symtab_index.to_bytes(4, byteorder='little'))
        # sh_info
        elf.write(text_index.to_bytes(4, byteorder='little'))
        # sh_addralign
        elf.write(b'\x04\x00\x00\x00')
        # sh_entsize
        elf.write(b'\x08\x00\x00\x00')

        # .symtab
        # sh_name
        elf.write((shstrtab_data.index(b'\0.symtab\0') + 1).to_bytes(4, byteorder='little'))
        # sh_type
        elf.write(b'\x02\x00\x00\x00') # SHT_SYMTAB
        # sh_flags
        elf.write(b'\x00\x00\x00\x00')
        # sh_addr
        elf.write(b'\x00\x00\x00\x00')
        # sh_offset
        elf.write(symtab_offset.to_bytes(4, byteorder='little'))
        # sh_size
        elf.write(symtab_size.to_bytes(4, byteorder='little'))
        # sh_link
        elf.write(strtab_index.to_bytes(4, byteorder='little'))
        # sh_info
        elf.write(b'\x02\x00\x00\x00')
        # sh_addralign
        elf.write(b'\x04\x00\x00\x00')
        # sh_entsize
        elf.write(b'\x10\x00\x00\x00')

        # .strtab
        # sh_name
        elf.write((shstrtab_data.index(b'\0.strtab\0') + 1).to_bytes(4, byteorder='little'))
        # sh_type
        elf.write(b'\x03\x00\x00\x00') # SHT_STRTAB
        # sh_flags
        elf.write(b'\x00\x00\x00\x00')
        # sh_addr
        elf.write(b'\x00\x00\x00\x00')
        # sh_offset
        elf.write(strtab_offset.to_bytes(4, byteorder='little'))
        # sh_size
        elf.write(strtab_size.to_bytes(4, byteorder='little'))
        # sh_link
        elf.write(b'\x00\x00\x00\x00')
        # sh_info
        elf.write(b'\x00\x00\x00\x00')
        # sh_addralign
        elf.write(b'\x01\x00\x00\x00')
        # sh_entsize
        elf.write(b'\x00\x00\x00\x00')

        # .shstrtab
        # sh_name
        elf.write((shstrtab_data.index(b'\0.shstrtab\0') + 1).to_bytes(4, byteorder='little'))
        # sh_type
        elf.write(b'\x03\x00\x00\x00') # SHT_STRTAB
        # sh_flags
        elf.write(b'\x00\x00\x00\x00')
        # sh_addr
        elf.write(b'\x00\x00\x00\x00')
        # sh_offset
        elf.write(shstrtab_offset.to_bytes(4, byteorder='little'))
        # sh_size
        elf.write(shstrtab_size.to_bytes(4, byteorder='little'))
        # sh_link
        elf.write(b'\x00\x00\x00\x00')
        # sh_info
        elf.write(b'\x00\x00\x00\x00')
        # sh_addralign
        elf.write(b'\x01\x00\x00\x00')
        # sh_entsize
        elf.write(b'\x00\x00\x00\x00')

    print('')
    print("ELF file successfully written to '{}'".format(args.elf))
