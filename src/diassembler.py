from ram import read_data, write_data, memory

def load(filepath, start_addr=0x80000000):
    """Load a raw binary file into RAM (byte-by-byte)."""
    try:
        with open(filepath, "rb") as f:
            data = f.read()
            for offset, byte in enumerate(data):
                write_data(start_addr + offset, byte)
        print(f"Loaded {len(data)}  from bin file '{filepath}' at {hex(start_addr)}")
    except FileNotFoundError:
        print(f"bin file not found: {filepath}")
        exit(1)
        return None
    except Exception as e:
        print(f"Error reading obj file: {e}")
        return None

def get_word(addr):
    """Read 4 bytes little-endian from RAM and return 32-bit word."""
    return (read_data(addr) |
            (read_data(addr + 1) << 8) |
            (read_data(addr + 2) << 16) |
            (read_data(addr + 3) << 24))

def sign_extend(value, bits):
    """Sign-extend a `bits`-bit value to Python int."""
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)

def _fields(inst):
    """Extract common fields used by many instruction formats."""
    return {
        "opcode": inst & 0x7f,
        "rd":     (inst >> 7) & 0x1f,
        "funct3": (inst >> 12) & 0x7,
        "rs1":    (inst >> 15) & 0x1f,
        "rs2":    (inst >> 20) & 0x1f,
        "funct7": (inst >> 25) & 0x7f,
    }

def decode(all_inst):
    """Return assembly string for a single 32-bit instruction."""
    f = _fields(all_inst)
    opcode = f["opcode"]
    rd = f["rd"]
    funct3 = f["funct3"]
    rs1 = f["rs1"]
    rs2 = f["rs2"]
    funct7 = f["funct7"]

   
    if opcode == 0b0110011:
        if funct3 == 0x0:
            return f"sub x{rd}, x{rs1}, x{rs2}" if funct7 == 0x20 else f"add x{rd}, x{rs1}, x{rs2}"
        if funct3 == 0x1 and funct7 == 0x00: return f"sll x{rd}, x{rs1}, x{rs2}"
        if funct3 == 0x2 and funct7 == 0x00: return f"slt x{rd}, x{rs1}, x{rs2}"
        if funct3 == 0x3 and funct7 == 0x00: return f"sltu x{rd}, x{rs1}, x{rs2}"
        if funct3 == 0x4: return f"xor x{rd}, x{rs1}, x{rs2}"
        if funct3 == 0x5:
            return f"sra x{rd}, x{rs1}, x{rs2}" if funct7 == 0x20 else f"srl x{rd}, x{rs1}, x{rs2}"
        if funct3 == 0x6: return f"or x{rd}, x{rs1}, x{rs2}"
        if funct3 == 0x7: return f"and x{rd}, x{rs1}, x{rs2}"

    
    elif opcode == 0b0010011:
        imm = sign_extend(all_inst >> 20, 12)
        shamt = (all_inst >> 20) & 0x1f
        funct7i = (all_inst >> 25) & 0x7f
        if funct3 == 0x0: return f"addi x{rd}, x{rs1}, {imm}"
        if funct3 == 0x1 and funct7i == 0x00: return f"slli x{rd}, x{rs1}, {shamt}"
        if funct3 == 0x2: return f"slti x{rd}, x{rs1}, {imm}"
        if funct3 == 0x3: return f"sltiu x{rd}, x{rs1}, {imm}"
        if funct3 == 0x4: return f"xori x{rd}, x{rs1}, {imm}"
        if funct3 == 0x5:
            return f"srai x{rd}, x{rs1}, {shamt}" if funct7i == 0x20 else f"srli x{rd}, x{rs1}, {shamt}"
        if funct3 == 0x6: return f"ori x{rd}, x{rs1}, {imm}"
        if funct3 == 0x7: return f"andi x{rd}, x{rs1}, {imm}"

   
    elif opcode == 0b0000011:
        imm = sign_extend(all_inst >> 20, 12)
        if funct3 == 0x0: return f"lb x{rd}, {imm}(x{rs1})"
        if funct3 == 0x1: return f"lh x{rd}, {imm}(x{rs1})"
        if funct3 == 0x2: return f"lw x{rd}, {imm}(x{rs1})"
        if funct3 == 0x4: return f"lbu x{rd}, {imm}(x{rs1})"
        if funct3 == 0x5: return f"lhu x{rd}, {imm}(x{rs1})"

    
    elif opcode == 0b0100011:
        imm = ((all_inst >> 7) & 0x1f) | (((all_inst >> 25) & 0x7f) << 5)
        imm = sign_extend(imm, 12)
        if funct3 == 0x0: return f"sb x{rs2}, {imm}(x{rs1})"
        if funct3 == 0x1: return f"sh x{rs2}, {imm}(x{rs1})"
        if funct3 == 0x2: return f"sw x{rs2}, {imm}(x{rs1})"

    
    elif opcode == 0b1100011:
        imm = (((all_inst >> 31) & 0x1) << 12) | \
              (((all_inst >> 7) & 0x1) << 11) | \
              (((all_inst >> 25) & 0x3f) << 5) | \
              (((all_inst >> 8) & 0xf) << 1)
        imm = sign_extend(imm, 13)
        if funct3 == 0x0: return f"beq x{rs1}, x{rs2}, {imm}"
        if funct3 == 0x1: return f"bne x{rs1}, x{rs2}, {imm}"
        if funct3 == 0x4: return f"blt x{rs1}, x{rs2}, {imm}"
        if funct3 == 0x5: return f"bge x{rs1}, x{rs2}, {imm}"
        if funct3 == 0x6: return f"bltu x{rs1}, x{rs2}, {imm}"
        if funct3 == 0x7: return f"bgeu x{rs1}, x{rs2}, {imm}"

    
    elif opcode == 0b1100111:
        imm = sign_extend(all_inst >> 20, 12)
        if funct3 == 0x0: return f"jalr x{rd}, {imm}(x{rs1})"

   
    elif opcode == 0b1101111:
        imm = (((all_inst >> 31) & 0x1) << 20) | \
              (((all_inst >> 12) & 0xff) << 12) | \
              (((all_inst >> 20) & 0x1) << 11) | \
              (((all_inst >> 21) & 0x3ff) << 1)
        imm = sign_extend(imm, 21)
        return f"jal x{rd}, {imm}"

    elif opcode == 0b0110111:
        imm = all_inst & 0xfffff000
        return f"lui x{rd}, {imm}"
    elif opcode == 0b0010111:
        imm = all_inst & 0xfffff000
        return f"auipc x{rd}, {imm}"

    elif opcode == 0b1110011:
        imm = all_inst >> 20
        if imm == 0: return "ecall"
        if imm == 1: return "ebreak"

  
    elif opcode == 0b0101111:
        funct5 = funct7 & 0x1f
        if funct3 == 0x2:
            if funct5 == 0x02: return f"lr.w x{rd}, (x{rs1})"
            if funct5 == 0x03: return f"sc.w x{rd}, x{rs2}, (x{rs1})"
            if funct5 == 0x01: return f"amoswap.w x{rd}, x{rs2}, (x{rs1})"
            if funct5 == 0x00: return f"amoadd.w x{rd}, x{rs2}, (x{rs1})"
            if funct5 == 0x04: return f"amoxor.w x{rd}, x{rs2}, (x{rs1})"
            if funct5 == 0x0C: return f"amoand.w x{rd}, x{rs2}, (x{rs1})"
            if funct5 == 0x0A: return f"amoor.w x{rd}, x{rs2}, (x{rs1})"
            if funct5 == 0x14: return f"amomax.w x{rd}, x{rs2}, (x{rs1})"
            if funct5 == 0x10: return f"amomin.w x{rd}, x{rs2}, (x{rs1})"

    if funct7 == 0x01:
        if funct3 == 0x0: return f"mul x{rd}, x{rs1}, x{rs2}"
        if funct3 == 0x1: return f"mulh x{rd}, x{rs1}, x{rs2}"
        if funct3 == 0x2: return f"mulhsu x{rd}, x{rs1}, x{rs2}"
        if funct3 == 0x3: return f"mulhu x{rd}, x{rs1}, x{rs2}"
        if funct3 == 0x4: return f"div x{rd}, x{rs1}, x{rs2}"
        if funct3 == 0x5: return f"divu x{rd}, x{rs1}, x{rs2}"
        if funct3 == 0x6: return f"rem x{rd}, x{rs1}, x{rs2}"
        if funct3 == 0x7: return f"remu x{rd}, x{rs1}, x{rs2}"

   
    return f".word 0x{all_inst:08x}"

def disassemble(start_addr=0x80000000, end_addr=0x80008000, toDecode=True):
    lines = []
    addr = start_addr
    while addr + 3 < end_addr:
        word_val = get_word(addr)
        if word_val == 0:
            addr += 4
            continue
        asm = decode(word_val) if toDecode else ""
        line = f"{addr:08x}:       {word_val:08x}                {asm}"
        print(line)
        lines.append(line)
        addr += 4
    return lines
