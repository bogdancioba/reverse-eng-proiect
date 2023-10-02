from enum import Enum

class Detection(Enum):
    Unknown          = 0x00
    Text             = 0x01
    Binary           = 0x02
    UTF8             = 0x03
    Unicode          = 0x04
    LanguageRomanian = 0x05
    LanguageEnglish  = 0x06
    PythonScript     = 0x07
    PythonBytecode   = 0x08
    ZipArchive       = 0x09
    MediaImage       = 0x0A
    LinkDocument     = 0x0B
    SecretDocument   = 0x0C
    ImagesInDocument = 0x0D
    MacrosInDocument = 0x0E
    XMLMacrosDocument= 0x0F
    DocumentwithExec = 0x10
    ProtectedDocument= 0x11
    PttxFile         = 0x12
    XLSBFile         = 0x13
    ElfFile          = 0x14
    PEFile           = 0x15
    MachOFile        = 0x16
    UPXFile          = 0x17
    CryptoFile       = 0x18
    AesFile          = 0x19
    SecretSectionFile= 0x20
    OpCodeFile       = 0x21
