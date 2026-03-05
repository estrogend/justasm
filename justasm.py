import subprocess
import os
import shutil
from enum import Enum

class AsmSyntax(Enum):
    ATT = "att"
    INTEL = "intel"

class Assembler:
    asmcache = ""
    asm = []
    assembler = "as"
    asm_args = []
    asm_bin = ""
    updated = True
    syntax = AsmSyntax.ATT
    def __init__(self, syntax = AsmSyntax.ATT, bitsize = 64):
        self.syntax = syntax
        self.asmcache = os.getcwd() + "/asm_cache"
        
        if not os.path.exists(self.asmcache):
            os.mkdir(self.asmcache)    

        self.asm_bin = shutil.which(self.assembler)
        self.asm_args.append(self.asmcache + "/asm.S")
        self.asm_args.append(f"-{bitsize}")
        self.asm_args.append("-msyntax")
        self.asm_args.append(syntax.value)
        self.asm_args.append("-o")
        self.asm_args.append(self.asmcache + "/a.out")

        if self.syntax == AsmSyntax.INTEL:
            self.asm.append(".intel_syntax noprefix")

    # Appends one or multiple instructions. if instr is a string,
    # it is seperated on newlines.
    def append_instr(self, instr):
        if isinstance(instr, str):
            self.asm = self.asm + instr.split('\n')
        elif isinstance(instr, list):
            self.asm = self.asm + instr
        else:
            self.asm.append(instr)
        self.updated = True

    # clears all instructions    
    def clear(self):
        self.asm.clear()
        # clear() will clear this too, so restore it:
        if self.syntax == AsmSyntax.INTEL:
            self.asm.append(".intel_syntax noprefix")
    # assembles all the given instructions and returns a bytes object
    # that contains the assembled bytecode.
    def assemble(self):
        if not self.asm:
            return None

        if os.path.exists(self.asmcache + '/asm.S') and not self.updated:
            with open(self.asmcache + "/asm.S", "r+") as file:
                for instr in self.asm:
                    file.write(instr + "\n")
                file.close()
        else:
            with open(self.asmcache + "/asm.S", "w") as file:
                for instr in self.asm:
                    file.write(instr + "\n")
                file.close()
        self.updated = False

        argv = [self.asm_bin] + self.asm_args
        subprocess.run(argv, stdout=subprocess.DEVNULL)
        # The above compiled an ELF, but we only need the bytecode,
        # so extract the text segment:
        extractor = subprocess.Popen([shutil.which('objcopy'), '-O', 'binary', '-j', '.text', 
                          self.asmcache + "/a.out", 
                          self.asmcache + "/out.bin"], stdout=subprocess.DEVNULL)
        extractor.wait()
        out_file = open(self.asmcache + "/out.bin", "rb")
        res = out_file.read()
        out_file.close()
        return res
