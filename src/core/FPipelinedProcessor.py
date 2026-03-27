from .pipelined_processor import PipelinedProcessor
from .riscv_tables import *


class FPipelinedProcessor(PipelinedProcessor):
    def __init__(self, start, ram, logger, st):
        super().__init__(start, ram, logger, st)

    def run(self, num_insts):
        """
        Five-stage pipeline with bypass paths.
        Control transfers are decided in DECODE.
        Only load-use stalls are inserted.
        """
        committed = 0
        cycle = 0
        fetch_enabled = True

        
        def _snap():
            
            pr = self.pipeline_regs
            return {
                "IF/ID": pr["IF/ID"].copy() if pr["IF/ID"] else None,
                "ID/EX": pr["ID/EX"].copy() if pr["ID/EX"] else None,
                "EX/MEM": pr["EX/MEM"].copy() if pr["EX/MEM"] else None,
                "MEM/WB": pr["MEM/WB"].copy() if pr["MEM/WB"] else None,
            }

        def _branch_taken(op, decoded, v_rs1, v_rs2):
            
            funct3 = decoded.get("funct3", 0)
            if funct3 == 0x0:  
                return v_rs1 == v_rs2
            if funct3 == 0x1:  
                return v_rs1 != v_rs2
            if funct3 == 0x4:  
                return self._to_signed_32(v_rs1) < self._to_signed_32(v_rs2)
            if funct3 == 0x5:  
                return self._to_signed_32(v_rs1) >= self._to_signed_32(v_rs2)
            if funct3 == 0x6:  
                return (v_rs1 & 0xFFFFFFFF) < (v_rs2 & 0xFFFFFFFF)
            if funct3 == 0x7:  
                return (v_rs1 & 0xFFFFFFFF) >= (v_rs2 & 0xFFFFFFFF)
            return False

        def _maybe_forward_from_exmem(rs1, rs2, exmem, op1, op2):
            
            if exmem is None:
                return op1, op2
            rd_exmem = exmem["decoded"].get("rd", 0)
            op_exmem = exmem["op"]
            if rd_exmem != 0 and not (is_store(op_exmem) or is_branch(op_exmem) or is_load(op_exmem)):
                if rs1 == rd_exmem:
                    op1 = exmem["result"]
                if rs2 == rd_exmem:
                    op2 = exmem["result"]
            return op1, op2

        def _maybe_forward_from_memwb(rs1, rs2, memwb, exmem, op1, op2):
            if memwb is None:
                return op1, op2
            rd_memwb = memwb["decoded"].get("rd", 0)
            op_memwb = memwb["op"]
            if rd_memwb == 0 or is_store(op_memwb) or is_branch(op_memwb):
                return op1, op2
            val = memwb["ldata"] if is_load(op_memwb) else memwb["result"]
            exmem_rd = exmem["decoded"].get("rd", 0) if exmem else 0
            if rs1 == rd_memwb and rs1 != exmem_rd:
                op1 = val
            if rs2 == rd_memwb and rs2 != exmem_rd:
                op2 = val
            return op1, op2

        while committed < num_insts:
            cycle += 1
            self.stats.increment_clock_cycle()

            dummy_regs = _snap()

            
            wb_data = dummy_regs["MEM/WB"]
            if wb_data is not None:
                self.registers = self.reg_write(
                    wb_data["op"], wb_data["decoded"], wb_data["result"], wb_data["ldata"],
                    self.registers, wb_data["curr_pc"], wb_data["next_pc"],
                    self.mem, self.logr
                )
                committed += 1
                self.stats.increment_instruction_count()

            
            mem_data = dummy_regs["EX/MEM"]
            if mem_data is not None:
                ldata = self.mem_access(
                    mem_data["op"], mem_data["result"],
                    self.mem, self.registers, mem_data["decoded"]
                )
                self.pipeline_regs["MEM/WB"] = {
                    "curr_pc": mem_data["curr_pc"],
                    "decoded": mem_data["decoded"],
                    "op": mem_data["op"],
                    "result": mem_data["result"],
                    "next_pc": mem_data["next_pc"],
                    "ldata": ldata,
                }
            else:
                self.pipeline_regs["MEM/WB"] = None

            
            ex_data = dummy_regs["ID/EX"]
            if ex_data is not None:
                op = ex_data["op"]
                decoded = ex_data["decoded"]
                rs1 = decoded.get("rs1", 0)
                rs2 = decoded.get("rs2", 0)
                op1 = ex_data["op1"]
                op2 = ex_data["op2"]

                
                op1, op2 = _maybe_forward_from_exmem(rs1, rs2, dummy_regs["EX/MEM"], op1, op2)
                op1, op2 = _maybe_forward_from_memwb(rs1, rs2, dummy_regs["MEM/WB"], dummy_regs["EX/MEM"], op1, op2)

                result = self.execute(op, op1, op2)
                next_pc = self.update_pc(ex_data["curr_pc"], op, result, decoded, self.registers)

                self.pipeline_regs["EX/MEM"] = {
                    "curr_pc": ex_data["curr_pc"],
                    "decoded": decoded,
                    "op": op,
                    "store_data": ex_data["store_data"],
                    "result": result,
                    "next_pc": next_pc,
                }
            else:
                self.pipeline_regs["EX/MEM"] = None

            
            id_data = dummy_regs["IF/ID"]
            stall = False
            branch_taken_in_decode = False

            if id_data is not None:
                op, decoded = self.decode(id_data["instruction"])
                rs1 = decoded.get("rs1", 0)
                rs2 = decoded.get("rs2", 0)

                v_rs1 = self.registers[rs1] if rs1 != 0 else 0
                v_rs2 = self.registers[rs2] if rs2 != 0 else 0

                
                if dummy_regs["ID/EX"] is not None:
                    idex = dummy_regs["ID/EX"]
                    rd_idex = idex["decoded"].get("rd", 0)
                    op_idex = idex["op"]
                    if is_load(op_idex) and rd_idex != 0:
                        if rs1 == rd_idex or rs2 == rd_idex:
                            stall = True

                
                if not stall and dummy_regs["EX/MEM"] is not None:
                    exmem = dummy_regs["EX/MEM"]
                    rd_exmem = exmem["decoded"].get("rd", 0)
                    op_exmem = exmem["op"]
                    if rd_exmem != 0 and not (is_store(op_exmem) or is_branch(op_exmem)):
                        if is_load(op_exmem):
                            
                            if rs1 == rd_exmem or rs2 == rd_exmem:
                                stall = True
                        else:
                            if rs1 == rd_exmem:
                                v_rs1 = exmem["result"]
                            if rs2 == rd_exmem:
                                v_rs2 = exmem["result"]

                
                if not stall and dummy_regs["MEM/WB"] is not None:
                    memwb = dummy_regs["MEM/WB"]
                    rd_memwb = memwb["decoded"].get("rd", 0)
                    op_memwb = memwb["op"]
                    if rd_memwb != 0 and not (is_store(op_memwb) or is_branch(op_memwb)):
                        val = memwb["ldata"] if is_load(op_memwb) else memwb["result"]
                        exmem_rd = dummy_regs["EX/MEM"]["decoded"].get("rd", 0) if dummy_regs["EX/MEM"] else 0
                        if rs1 == rd_memwb and rs1 != exmem_rd:
                            v_rs1 = val
                        if rs2 == rd_memwb and rs2 != exmem_rd:
                            v_rs2 = val

                if stall:
                    
                    self.pipeline_regs["ID/EX"] = None
                else:
                    
                    if is_branch(op) or is_jump(op):
                        if is_branch(op):
                            if _branch_taken(op, decoded, v_rs1, v_rs2):
                                target_pc = (id_data["curr_pc"] + decoded["imm"]) & 0xFFFFFFFF
                                self.pc = target_pc
                                branch_taken_in_decode = True
                                self.logr.debug(f"Branch taken in DECODE to {target_pc:08x}")
                        else:
                            opcode = decoded["opcode"]
                            if opcode == 0x6F:  
                                target_pc = (id_data["curr_pc"] + decoded["imm"]) & 0xFFFFFFFF
                                self.pc = target_pc
                                branch_taken_in_decode = True
                                self.logr.debug(f"JAL taken in DECODE to {target_pc:08x}")
                            elif opcode == 0x67:  
                                target_pc = (v_rs1 + decoded["imm"]) & ~1
                                self.pc = target_pc
                                branch_taken_in_decode = True
                                self.logr.debug(f"JALR taken in DECODE to {target_pc:08x}")

                    
                    op1, op2 = self.operand_fetch(decoded, self.registers, id_data["curr_pc"])
                    opcode = decoded["opcode"]

                    if opcode in [0x33, 0x03, 0x13, 0x23, 0x63, 0x67]:  
                        if rs1 != 0:
                            op1 = v_rs1
                    if opcode in [0x33, 0x23, 0x63]:  
                        if rs2 != 0:
                            op2 = v_rs2

                    
                    if branch_taken_in_decode:
                        self.pipeline_regs["ID/EX"] = None
                    else:
                        self.pipeline_regs["ID/EX"] = {
                            "curr_pc": id_data["curr_pc"],
                            "decoded": decoded,
                            "op": op,
                            "op1": op1,
                            "op2": op2,
                            "store_data": v_rs2 if decoded["rs2"] != 0 else 0,
                        }
            else:
                self.pipeline_regs["ID/EX"] = None

            
            if not stall and not branch_taken_in_decode and fetch_enabled:
                try:
                    instruction, next_pc = self.fetch(self.pc, self.mem)
                    if instruction is None:
                        self.pipeline_regs["IF/ID"] = None
                        fetch_enabled = False
                    else:
                        self.pipeline_regs["IF/ID"] = {"instruction": instruction, "curr_pc": self.pc}
                        self.pc = (self.pc + 4) & 0xFFFFFFFF
                except:
                    self.pipeline_regs["IF/ID"] = None
                    fetch_enabled = False
            elif stall:
                
                pass
            elif branch_taken_in_decode:
                
                self.pipeline_regs["IF/ID"] = None
        


        self.logr.info(
            f"Simulation complete (with forwarding): executed {committed} instructions in {cycle} cycles."
        )
