# Copyright © 2023 Carl Åstholm <https://github.com/castholm>
# SPDX-License-Identifier: MIT

<#
    .SYNOPSIS
    Converts a Playdate pdex.bin file to an ELF file.

    .DESCRIPTION
    Converts the specified pdex.bin (Playdate executable) file to an ELF (Executable and
    Linkable Format) file suitable for analysis by tools like readelf or objdump.

    .PARAMETER pdex
    The path to the input pdex.bin.

    .PARAMETER elf
    The path to the output ELF file.

    .EXAMPLE
    ./pdex2elf.ps1 pdex.bin pdex.elf
#>

#Requires -Version 7.4

[CmdletBinding()]
param (
    [Parameter(Mandatory = $true)]
    [string] $pdex,

    [Parameter(Mandatory = $true)]
    [string] $elf
)
begin {
    $ErrorActionPreference = "Stop"
    Set-StrictMode -Version 3.0

    $pdexStream = $null
    $zlibStream = $null
    $md5 = $null
    $elfStream = $null
    $elfWriter = $null

    $buf = [byte[]]::new(0x1000)

    $pdexStream = [System.IO.File]::OpenRead($pdex)

    $pdexStream.ReadExactly($buf, 0, 0x30)

    if (-not [System.BitConverter]::IsLittleEndian) {
        [array]::Reverse($buf, 0x0C, 4)
        [array]::Reverse($buf, 0x20, 4)
        [array]::Reverse($buf, 0x24, 4)
        [array]::Reverse($buf, 0x28, 4)
        [array]::Reverse($buf, 0x2C, 4)
    }

    $pdexMagic = [System.Text.Encoding]::ASCII.GetString($buf, 0, 0x0C)
    if ($pdexMagic -cne "Playdate PDX") {
        throw "Invalid file signature in file header (expected 'Playdate PDX', found '$pdexMagic')."
    }

    $pdexFlags = [System.BitConverter]::ToUInt32($buf, 0x0C)
    if ($pdexFlags -ne 0u) {
        if ($pdexFlags -band 0x40000000u) {
            throw "The pdex.bin is encrypted and can not be read."
        } else {
            throw "Unknown/unsupported flags in file header (found $pdexFlags)."
        }
    }

    $pdexMd5 = [System.Convert]::ToHexString($buf, 0x10, 0x10)
    $pdexFilesz = [System.BitConverter]::ToUInt32($buf, 0x20)
    $pdexMemsz = [System.BitConverter]::ToUInt32($buf, 0x24)
    $pdexEntry = [System.BitConverter]::ToUInt32($buf, 0x28)
    $pdexRelnum = [System.BitConverter]::ToUInt32($buf, 0x2C)

    "pdex.bin header:"
    "  File signature:      $pdexMagic"
    "  Flags:               $pdexFlags"
    "  MD5 checksum:        $pdexMd5"
    "  File size:           $pdexFilesz"
    "  Memory size:         $pdexMemsz"
    "  Entry point address: $pdexEntry"
    "  Relocation entries:  $pdexRelnum"

    $shCount = 7us

    $textIndex = 1us
    $textAddr = 0u
    $textOffset = 0x010000u
    $textSize = $pdexFilesz

    $bssAddr = [uint]($pdexFilesz + 3u) -band (-bnot 3u) # align(4)
    $bssOffset = [uint]($textOffset + $bssAddr)
    $bssSize = [uint]($pdexMemsz - $pdexFilesz)

    $relTextOffset = $bssOffset
    $relTextSize = [uint]($pdexRelnum * 8u)

    $symtabIndex = 4us
    $symtabOffset = [uint]($relTextOffset + $relTextSize) -band (-bnot 3u) # align(4)
    $symtabCount = 2u
    $symtabSize = [uint]($symtabCount * 0x10u)

    $strtabIndex = 5us
    $strtabOffset = [uint]($symtabOffset + $symtabSize)
    $strtab = "`0"

    $shstrtabIndex = 6us
    $shstrtabOffset = [uint]($strtabOffset + [uint]$strtab.Length)
    $shstrtab = "`0.text`0.bss`0.rel.text`0.symtab`0.strtab`0.shstrtab`0"

    $shOffset = [uint]($shstrtabOffset + [uint]$shstrtab.Length + 3u) -band (-bnot 3u) # align(4)

    $elfDir = [System.IO.Path]::GetDirectoryName($elf)
    if ($elfDir) { $null = [System.IO.Directory]::CreateDirectory($elfDir) }
    $elfStream = [System.IO.File]::OpenWrite($elf)
    $elfWriter = [System.IO.BinaryWriter]::new($elfStream, [System.Text.Encoding]::ASCII, $true)

    # ==== ELF header ====

    # e_ident[EI_MAG0] .. e_ident[EI_MAG3]
    $elfWriter.Write([System.Text.Encoding]::ASCII.GetBytes("`u{7F}ELF"))
    # e_ident[EI_CLASS]
    $elfWriter.Write(1uy) # ELFCLASS32
    # e_ident[EI_DATA]
    $elfWriter.Write(1uy) # ELFDATA2LSB
    # e_ident[EI_VERSION]
    $elfWriter.Write(1uy) # EV_CURRENT
    # e_ident[EI_OSABI]
    $elfWriter.Write(0uy) # ELFOSABI_SYSV
    # e_ident[EI_ABIVERSION]
    $elfWriter.Write(0uy)
    # e_ident[EI_PAD] .. e_ident[EI_NIDENT - 1]
    for ($i = 9; $i -lt 0x10; $i++) { $elfWriter.Write(0uy) }
    # e_type
    $elfWriter.Write(2us) # ET_EXEC
    # e_machine
    $elfWriter.Write(0x28us) # EM_ARM
    # e_version
    $elfWriter.Write(1u) # EV_CURRENT
    # e_entry
    $elfWriter.Write([uint]$pdexEntry)
    # e_phoff
    $elfWriter.Write(0x34u)
    # e_shoff
    $elfWriter.Write([uint]$shOffset)
    # e_flags
    $elfWriter.Write(0x05000400u) # EF_ARM_EABI_VER5 | EF_ARM_ABI_FLOAT_HARD
    # e_ehsize
    $elfWriter.Write(0x34us)
    # e_phentsize
    $elfWriter.Write(0x20us)
    # e_phnum
    $elfWriter.Write(1us)
    # e_shentsize
    $elfWriter.Write(0x28us)
    # e_shnum
    $elfWriter.Write([ushort]$shCount)
    # e_shstrndx
    $elfWriter.Write([ushort]$shstrtabIndex)

    # ==== Program header ====

    # p_type
    $elfWriter.Write(1u) # PT_LOAD
    # p_offset
    $elfWriter.Write([uint]$textOffset)
    # p_vaddr
    $elfWriter.Write(0u)
    # p_paddr
    $elfWriter.Write(0u)
    # p_filesz
    $elfWriter.Write([uint]$pdexFilesz)
    # p_memsz
    $elfWriter.Write([uint]$pdexMemsz)
    # p_flags
    $elfWriter.Write(7u) # PF_X | PF_W | PF_R
    # p_align
    $elfWriter.Write([uint]$textOffset)

    # ==== .text section ====

    for ($i = 0x54; $i -lt 0x010000; $i += 4) { $elfWriter.Write(0u) }

    $zlibStream = [System.IO.Compression.ZLibStream]::new($pdexStream, [System.IO.Compression.CompressionMode]::Decompress)
    $md5 = [System.Security.Cryptography.MD5]::Create()

    $bytesRemaining = [int]$pdexFilesz
    do {
        $bytesRead = $zlibStream.Read($buf, 0, [System.Math]::Min($buf.Length, $bytesRemaining))
        $elfWriter.Write($buf, 0, $bytesRead)
        $null = $md5.TransformBlock($buf, 0, $bytesRead, $null, 0)
        $bytesRemaining -= $bytesRead
    } while ($bytesRemaining -gt 0 -and $bytesRead -gt 0)
    $null = $md5.TransformFinalBlock($buf, 0, 0)

    ""
    "Computed MD5 checksum: $([System.Convert]::ToHexString($md5.Hash))"

    # ==== .rel.text section ====

    for ([uint] $i = $textOffset + $textSize; $i -lt $relTextOffset; $i++) { $elfWriter.Write(0uy) }

    for ([uint] $i = 0u; $i -lt $pdexRelnum; $i++) {
        $zlibStream.ReadExactly($buf, 0, 4)

        # r_offset
        $elfWriter.Write($buf, 0, 4)
        # r_info
        $elfWriter.Write(2uy) # R_ARM_ABS32
        $elfWriter.Write([ushort]$textIndex)
        $elfWriter.Write(0uy)
    }

    # ==== .symtab section ====

    for ([uint] $i = ($relTextOffset + $relTextSize); $i -lt $symtabOffset; $i++) { $elfWriter.Write(0uy) }

    # NULL
    # st_name
    $elfWriter.Write(0u)
    # st_value
    $elfWriter.Write(0u)
    # st_size
    $elfWriter.Write(0u)
    # st_info
    $elfWriter.Write(0uy)
    # st_other
    $elfWriter.Write(0uy)
    # st_shndx
    $elfWriter.Write(0us)

    # .text
    # st_name
    $elfWriter.Write([uint]$textAddr)
    # st_value
    $elfWriter.Write(0u)
    # st_size
    $elfWriter.Write(0u)
    # st_info
    $elfWriter.Write(3uy)
    # st_other
    $elfWriter.Write(0uy)
    # st_shndx
    $elfWriter.Write([ushort]$textIndex)

    # ==== .strtab section ====

    $elfWriter.Write([System.Text.Encoding]::ASCII.GetBytes($strtab))

    # ==== .shstrtab section ====

    $elfWriter.Write([System.Text.Encoding]::ASCII.GetBytes($shstrtab))

    # ==== Section headers ====

    for ([uint]$i = $shstrtabOffset + [uint]$shstrtab.Length; $i -lt $shOffset; $i++) { $elfWriter.Write(0uy) }

    # NULL
    # sh_name
    $elfWriter.Write(0u)
    # sh_type
    $elfWriter.Write(0u) # SHT_NULL
    # sh_flags
    $elfWriter.Write(0u)
    # sh_addr
    $elfWriter.Write(0u)
    # sh_offset
    $elfWriter.Write(0u)
    # sh_size
    $elfWriter.Write(0u)
    # sh_link
    $elfWriter.Write(0u)
    # sh_info
    $elfWriter.Write(0u)
    # sh_addralign
    $elfWriter.Write(0u)
    # sh_entsize
    $elfWriter.Write(0u)

    # .text
    # sh_name
    $elfWriter.Write([uint]($shstrtab.IndexOf("`0.text`0", [System.StringComparison]::Ordinal) + 1))
    # sh_type
    $elfWriter.Write(1u) # SHT_PROGBITS
    # sh_flags
    $elfWriter.Write(0x37u) # SHF_WRITE | SHF_ALLOC | SHF_EXECINSTR | SHF_MERGE | SHF_STRINGS
    # sh_addr
    $elfWriter.Write([uint]$textAddr)
    # sh_offset
    $elfWriter.Write([uint]$textOffset)
    # sh_size
    $elfWriter.Write([uint]$textSize)
    # sh_link
    $elfWriter.Write(0u)
    # sh_info
    $elfWriter.Write(0u)
    # sh_addralign
    $elfWriter.Write(8u)
    # sh_entsize
    $elfWriter.Write(0u)

    # .bss
    # sh_name
    $elfWriter.Write([uint]($shstrtab.IndexOf("`0.bss`0", [System.StringComparison]::Ordinal) + 1))
    # sh_type
    $elfWriter.Write(8u) # SHT_NOBITS
    # sh_flags
    $elfWriter.Write(3u) # SHF_WRITE | SHF_ALLOC
    # sh_addr
    $elfWriter.Write([uint]$bssAddr)
    # sh_offset
    $elfWriter.Write([uint]$bssOffset)
    # sh_size
    $elfWriter.Write([uint]$bssSize)
    # sh_link
    $elfWriter.Write(0u)
    # sh_info
    $elfWriter.Write(0u)
    # sh_addralign
    $elfWriter.Write(4u)
    # sh_entsize
    $elfWriter.Write(0u)

    # .rel.text
    # sh_name
    $elfWriter.Write([uint]($shstrtab.IndexOf("`0.rel.text`0", [System.StringComparison]::Ordinal) + 1))
    # sh_type
    $elfWriter.Write(9u) # SHT_REL
    # sh_flags
    $elfWriter.Write(0x40u) # SHF_INFO_LINK
    # sh_addr
    $elfWriter.Write(0u)
    # sh_offset
    $elfWriter.Write([uint]$relTextOffset)
    # sh_size
    $elfWriter.Write([uint]$relTextSize)
    # sh_link
    $elfWriter.Write([uint]$symtabIndex)
    # sh_info
    $elfWriter.Write([uint]$textIndex)
    # sh_addralign
    $elfWriter.Write(4u)
    # sh_entsize
    $elfWriter.Write(8u)

    # .symtab
    # sh_name
    $elfWriter.Write([uint]($shstrtab.IndexOf("`0.symtab`0", [System.StringComparison]::Ordinal) + 1))
    # sh_type
    $elfWriter.Write(2u) # SHT_SYMTAB
    # sh_flags
    $elfWriter.Write(0u)
    # sh_addr
    $elfWriter.Write(0u)
    # sh_offset
    $elfWriter.Write([uint]$symtabOffset)
    # sh_size
    $elfWriter.Write([uint]$symtabSize)
    # sh_link
    $elfWriter.Write([uint]$strtabIndex)
    # sh_info
    $elfWriter.Write([uint]$symtabCount)
    # sh_addralign
    $elfWriter.Write(4u)
    # sh_entsize
    $elfWriter.Write(0x10u)

    # .strtab
    # sh_name
    $elfWriter.Write([uint]($shstrtab.IndexOf("`0.strtab`0", [System.StringComparison]::Ordinal) + 1))
    # sh_type
    $elfWriter.Write(3u) # SHT_STRTAB
    # sh_flags
    $elfWriter.Write(0u)
    # sh_addr
    $elfWriter.Write(0u)
    # sh_offset
    $elfWriter.Write([uint]$strtabOffset)
    # sh_size
    $elfWriter.Write([uint]$strtab.Length)
    # sh_link
    $elfWriter.Write(0u)
    # sh_info
    $elfWriter.Write(0u)
    # sh_addralign
    $elfWriter.Write(1u)
    # sh_entsize
    $elfWriter.Write(0u)

    # .shstrtab
    # sh_name
    $elfWriter.Write([uint]($shstrtab.IndexOf("`0.shstrtab`0", [System.StringComparison]::Ordinal) + 1))
    # sh_type
    $elfWriter.Write(3u) # SHT_STRTAB
    # sh_flags
    $elfWriter.Write(0u)
    # sh_addr
    $elfWriter.Write(0u)
    # sh_offset
    $elfWriter.Write([uint]$shstrtabOffset)
    # sh_size
    $elfWriter.Write([uint]$shstrtab.Length)
    # sh_link
    $elfWriter.Write(0u)
    # sh_info
    $elfWriter.Write(0u)
    # sh_addralign
    $elfWriter.Write(1u)
    # sh_entsize
    $elfWriter.Write(0u)

    $elfWriter.Flush()
    $elfStream.SetLength($elfStream.Position)

    ""
    "ELF file written to '$elf'."
}
clean {
    ${elfWriter}?.Close()
    ${elfStream}?.Close()
    ${md5}?.Dispose()
    ${zlibStream}?.Close()
    ${pdexStream}?.Close()
}
