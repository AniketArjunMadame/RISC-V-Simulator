# Functions to handle memory operations
def to_unsigned(num):
    return (num & 0xFFFFFFFF)

# ALU
e_add  = lambda op1, op2: op1 + op2
e_xor  = lambda op1, op2: op1 ^ op2
e_or   = lambda op1, op2: op1 | op2
e_and  = lambda op1, op2: op1 & op2
e_sll  = lambda op1, op2: op1 << op2  # NOTE: lui uses the same unit
e_srl  = lambda op1, op2: op1 >> op2
e_sra  = lambda op1, op2: (op1 + (1 << 32)) >> op2 if op1 < 0 else op1 >> op2
e_slt  = lambda op1, op2: 1 if op1 < op2 else 0
e_mul  = lambda op1, op2: op1 * op2
e_mulh = lambda op1, op2: (op1 * op2) >> 32
e_div  = lambda op1, op2: op1 // op2
e_rem  = lambda op1, op2: op1 % op2

# AUIPC
e_auipc = lambda op1, op2: op1 + (op2 << 12)

# AGU
e_agu = lambda op1, op2: op1 + op2

# e_lb  = lambda op1, op2: lb(op1, op2)
# e_lh  = lambda op1, op2: lh(op1, op2)
# e_lw  = lambda op1, op2: lw(op1, op2)
# e_lbu = lambda op1, op2: lbu(op1, op2)
# e_lhu = lambda op1, op2: lhu(op1, op2)
# e_sb  = lambda op1, op2: sb(op1, op2)
# e_sh  = lambda op1, op2: sh(op1, op2)
# e_sw  = lambda op1, op2: sw(op1, op2)

# Comparator
e_beq  = lambda op1, op2: op1 == op2
e_bne  = lambda op1, op2: op1 != op2
e_blt  = lambda op1, op2: op1 < op2
e_bge  = lambda op1, op2: op1 >= op2

# NOP
e_nop = lambda op1, op2: None

# e_fu = lambda op1, op2: op1 = self.pc + (op2 << imm)
# e_fu = lambda op1, op2: nop()  # FIXME: Special case of I-type
# e_fu = lambda op1, op2: nop()  # FIXME: Special case of I-type
# e_fu = lambda op1, op2: (op1 * op2) & 0xFFFFFFFF
# e_fu = lambda op1, op2: (op1 * op2) >> 32 & 0xFFFFFFFF
# e_fu = lambda op1, op2: (op1 * (op2 & 0xFFFFFFFF)) & 0xFFFFFFFF
# e_fu = lambda op1, op2: ((op1 & 0xFFFFFFFF) * (op2 & 0xFFFFFFFF)) & 0xFFFFFFFF
# e_fu = lambda op1, op2: op1 // op2
# e_fu = lambda op1, op2: (op1 & 0xFFFFFFFF) // (op2 & 0xFFFFFFFF)
# e_fu = lambda op1, op2: op1 % op2 if op2 != 0 else 0
# e_fu = lambda op1, op2: (op1 & 0xFFFFFFFF) % (op2 & 0xFFFFFFFF) if op2 != 0 else 0


