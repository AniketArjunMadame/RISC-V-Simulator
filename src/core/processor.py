from abc import ABC, abstractmethod
from .fu import *
from .riscv_tables import *

class Processor:
    def __init__(self, start, ram, logger):
        self.pc = start
        self.registers = [0] * 32
        self.mem = ram
        self.logr = logger

    def fetch(self, pc, mem):
        """
        Fetch instruction from memory at the given PC address.
        Returns: (instruction, next_pc)
        """
        try:
            instruction = mem.read_word(pc)
            self.logr.debug(f"Fetched instruction {instruction:08x} at {pc:08x}")
            next_pc = pc + 4
            return instruction, next_pc
        except ValueError as e:
            self.logr.error(f"Error fetching instruction at {pc:08x}: {e}")
            return None, pc

    def decode(self, instruction):
        """
        Decode the instruction and extract fields.
        Returns: (op, decoded_dict)
        """
        opcode = instruction & 0x7F
        decoded = {"opcode": opcode}
        
        if opcode == 0x33:
            funct7 = (instruction >> 25) & 0x7F
            rs2 = (instruction >> 20) & 0x1F
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            rd = (instruction >> 7) & 0x1F
            imm = 0
            
        
        elif opcode == 0x03:
            imm = instruction >> 20
            if imm & 0x800:  
                imm = imm | 0xFFFFF000
            imm = self._to_signed_32(imm)
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            rd = (instruction >> 7) & 0x1F
            funct7 = 0
            rs2 = 0
            
        
        elif opcode == 0x13:
            imm = instruction >> 20
            if imm & 0x800:  
                imm = imm | 0xFFFFF000
            imm = self._to_signed_32(imm)
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            rd = (instruction >> 7) & 0x1F
            
            if funct3 in [0x1, 0x5]:  
                funct7 = (instruction >> 25) & 0x7F
            else:
                funct7 = 0
            rs2 = 0
            
        
        elif opcode == 0x23:
            imm = ((instruction >> 25) << 5) | ((instruction >> 7) & 0x1F)
            if imm & 0x800:  
                imm = imm | 0xFFFFF000
            imm = self._to_signed_32(imm)
            rs2 = (instruction >> 20) & 0x1F
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            funct7 = 0
            rd = 0
            
        
        elif opcode == 0x63:
            imm_12 = (instruction >> 31) & 0x1
            imm_10_5 = (instruction >> 25) & 0x3F
            imm_4_1 = (instruction >> 8) & 0xF
            imm_11 = (instruction >> 7) & 0x1
            imm = ((imm_12 << 12) | (imm_11 << 11) | (imm_10_5 << 5) | (imm_4_1 << 1))
            if imm & 0x1000:  
                imm = imm | 0xFFFFE000
            imm = self._to_signed_32(imm)
            rs2 = (instruction >> 20) & 0x1F
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            funct7 = 0
            rd = 0
            
        
        elif opcode == 0x37:
            imm = instruction & 0xFFFFF000
            imm = self._to_signed_32(imm)
            rd = (instruction >> 7) & 0x1F
            rs1 = rs2 = funct3 = funct7 = 0
            
        
        elif opcode == 0x17:
            imm = (instruction & 0xFFFFF000)
            rd = (instruction >> 7) & 0x1F
            rs1 = rs2 = funct3 = funct7 = 0
            
        
        elif opcode == 0x6F:
            imm_20 = (instruction >> 31) & 0x1
            imm_10_1 = (instruction >> 21) & 0x3FF
            imm_11 = (instruction >> 20) & 0x1
            imm_19_12 = (instruction >> 12) & 0xFF
            imm = ((imm_20 << 20) | (imm_19_12 << 12) | (imm_11 << 11) | (imm_10_1 << 1))
            if imm & 0x100000:  
                imm = imm | 0xFFE00000
            imm = self._to_signed_32(imm)
            rd = (instruction >> 7) & 0x1F
            rs1 = rs2 = funct3 = funct7 = 0
            
        
        elif opcode == 0x67:
            imm = instruction >> 20
            if imm & 0x800:  
                imm = imm | 0xFFFFF000
            imm = self._to_signed_32(imm)
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            rd = (instruction >> 7) & 0x1F
            funct7 = 0
            rs2 = 0
            
        
        elif opcode == 0x73:
            imm = instruction >> 20
            rs1 = (instruction >> 15) & 0x1F
            funct3 = (instruction >> 12) & 0x07
            rd = (instruction >> 7) & 0x1F
            funct7 = 0
            rs2 = 0
            
        else:
            rs1 = rs2 = rd = imm = funct3 = funct7 = 0
            
        decoded.update({
            "rs1": rs1,
            "rs2": rs2,
            "rd": rd,
            "funct3": funct3,
            "funct7": funct7,
            "imm": imm
        })
        
        self.logr.debug(f'opcode={opcode:02x}, funct3={funct3:01x}, funct7={funct7:02x}')
        op = ((decoded["opcode"] << 12) | (decoded["funct3"] << 8) | decoded["funct7"])
        decoded["op"] = op
        return op, decoded

    def _to_signed_32(self, value):
        
        value = value & 0xFFFFFFFF
        if value & 0x80000000:
            return value - (1 << 32)
        return value
    
    def _to_unsigned_32(self, value):
        """Convert a value to unsigned 32-bit integer."""
        return value & 0xFFFFFFFF

    def operand_fetch(self, decoded, registers, pc):
        
        rs1 = decoded["rs1"]
        rs2 = decoded["rs2"]
        v_rs1 = registers[rs1] if rs1 != 0 else 0
        v_rs2 = registers[rs2] if rs2 != 0 else 0
        v_imm = decoded["imm"]
        op = decoded["op"]
        
        operand_func = alu_operands.get(op, None)
        if operand_func is None:
            self.logr.warning(f"Unknown operation {op:05x}, using default operands")
            op1, op2 = v_rs1, v_rs2
        else:
            op1, op2 = operand_func(v_rs1, v_rs2, v_imm, pc)
            
        self.logr.debug(f"Operands: op1={op1}, op2={op2}")
        return op1, op2

    def execute(self, op, op1, op2):
        """
        Execute the ALU operation.
        Returns: result
        """
        func = alu_function.get(op, None)
        if func is None:
            self.logr.warning(f"Unknown ALU operation {op:05x}, returning 0")
            result = 0
        else:
            result = func(op1, op2)
        self.logr.debug(f"Executed op {op:05x} => result {result}")
        return result

    def update_pc(self, pc, op, result, decoded, registers):
        """
        Update the program counter based on instruction type and execution result.
        Returns: next_pc
        """
        next_pc = pc + 4
        
        if is_branch(op) and result:
            
            next_pc = pc + decoded["imm"]
            self.logr.debug(f"Branch taken to {next_pc:08x}")
        elif is_jump(op):
            opcode = decoded["opcode"]
            if opcode == 0x6F:  
                next_pc = pc + decoded["imm"]
                self.logr.debug(f"JAL to {next_pc:08x}")
            elif opcode == 0x67:  
                rs1_val = registers[decoded["rs1"]] if decoded["rs1"] != 0 else 0
                next_pc = (rs1_val + decoded["imm"]) & ~1
                self.logr.debug(f"JALR to {next_pc:08x}")
                
        return next_pc

    def mem_access(self, op, addr, mem, registers, decoded):
        """
        Perform memory access (load/store operations).
        Returns: ldata (loaded data) or None
        """
        ldata = None
        
        if is_load(op):
            masked = (op & 0x00F00) >> 8
            if masked == 0x0:  
                ldata = mem.read(addr) & 0xFF
               
                if ldata & 0x80:
                    ldata = ldata | 0xFFFFFF00
                ldata = self._to_signed_32(ldata)
                self.logr.debug(f"Load byte from {addr:08x} => {ldata:08x}")
            elif masked == 0x4:  
                ldata = mem.read(addr) & 0xFF
                self.logr.debug(f"Load byte unsigned from {addr:08x} => {ldata:08x}")
            elif masked == 0x1:  
                ldata = mem.read_halfword(addr) & 0xFFFF
               
                if ldata & 0x8000:
                    ldata = ldata | 0xFFFF0000
                ldata = self._to_signed_32(ldata)
                self.logr.debug(f"Load halfword from {addr:08x} => {ldata:08x}")
            elif masked == 0x5:  
                ldata = mem.read_halfword(addr) & 0xFFFF
                self.logr.debug(f"Load halfword unsigned from {addr:08x} => {ldata:08x}")
            elif masked == 0x2:  
                ldata = mem.read_word(addr)
                ldata = self._to_signed_32(ldata)
                self.logr.debug(f"Load word from {addr:08x} => {ldata:08x}")
                
        elif is_store(op):
            rs2 = decoded["rs2"]
            data = registers[rs2] if rs2 != 0 else 0
            masked = (op & 0x00F00) >> 8
            if masked == 0x0:  
                mem.write(addr, data & 0xFF)
                self.logr.debug(f"Store byte to {addr:08x} <= {data & 0xFF:02x}")
            elif masked == 0x1:  
                mem.write_halfword(addr, data & 0xFFFF)
                self.logr.debug(f"Store halfword to {addr:08x} <= {data & 0xFFFF:04x}")
            elif masked == 0x2:  
                mem.write_word(addr, data & 0xFFFFFFFF)
                self.logr.debug(f"Store word to {addr:08x} <= {data:08x}")
                
        return ldata

    def reg_write(self, op, decoded, result, ldata, registers, pc, next_pc, mem, logr):
        """
        Write back results to the register file and log the execution.
        Returns: updated registers
        """
        rd = decoded["rd"]
        
        if is_branch(op):
            logr.out(f"{pc:08x} | next_pc={next_pc:08x} | x?=00000000 | mem[?]=00000000")
            
        elif is_jump(op):
            
            return_addr = (pc + 4) & 0xFFFFFFFF
            if rd != 0:
                registers[rd] = return_addr
            logr.out(f"{pc:08x} | next_pc={next_pc:08x} | x{rd}={return_addr:08x} | mem[?]=00000000")
            
        elif is_load(op) and ldata is not None:
            if rd != 0:
                registers[rd] = self._to_unsigned_32(ldata)
            logr.out(f"{pc:08x} | next_pc={next_pc:08x} | x{rd}={self._to_unsigned_32(ldata):08x} | mem[{result:08x}] => {self._to_unsigned_32(ldata):08x}")
            
        elif is_store(op):
            rs2 = decoded["rs2"]
            data = registers[rs2] if rs2 != 0 else 0
            logr.out(f"{pc:08x} | next_pc={next_pc:08x} | x?=00000000 | mem[{result:08x}] <= {data & 0xFFFFFFFF:08x}")
            
        else:
            
            if rd != 0:
                registers[rd] = self._to_unsigned_32(result)
            logr.out(f"{pc:08x} | next_pc={next_pc:08x} | x{rd}={self._to_unsigned_32(result):08x} | mem[?]=00000000")
        
        
        registers[0] = 0
            
        return registers

    @abstractmethod
    def run(self, num_insts):
        """
        Base run method - can be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the run() method")