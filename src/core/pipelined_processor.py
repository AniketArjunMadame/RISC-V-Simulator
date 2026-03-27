from .processor import Processor
from .riscv_tables import *


class PipelinedProcessor(Processor):
    def __init__(self, start, ram, logger, st):
        super().__init__(start, ram, logger)
        self.stats = st

        
        self.pipeline_regs = {
            "IF/ID": None,
            "ID/EX": None,
            "EX/MEM": None,
            "MEM/WB": None,
        }

    def run(self, num_insts):
        """
        Run a 5-stage pipelined processor """
        committed = 0
        cycle = 0
        fetch_enabled = True
        flush_cycles = 0  
        
        while committed < num_insts:
            cycle += 1
            self.stats.increment_clock_cycle()
            
            
            dummy_regs = {
                "IF/ID": self.pipeline_regs["IF/ID"].copy() if self.pipeline_regs["IF/ID"] else None,
                "ID/EX": self.pipeline_regs["ID/EX"].copy() if self.pipeline_regs["ID/EX"] else None,
                "EX/MEM": self.pipeline_regs["EX/MEM"].copy() if self.pipeline_regs["EX/MEM"] else None,
                "MEM/WB": self.pipeline_regs["MEM/WB"].copy() if self.pipeline_regs["MEM/WB"] else None,
            }
            
            
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
                    "ldata": ldata
                }
            else:
                self.pipeline_regs["MEM/WB"] = None
            
            
            ex_data = dummy_regs["ID/EX"]
            branch_taken = False
            if ex_data is not None:
                result = self.execute(ex_data["op"], ex_data["op1"], ex_data["op2"])
                next_pc = self.update_pc(
                    ex_data["curr_pc"], ex_data["op"], result, 
                    ex_data["decoded"], self.registers
                )
                
                self.pipeline_regs["EX/MEM"] = {
                    "curr_pc": ex_data["curr_pc"], 
                    "decoded": ex_data["decoded"],
                    "op": ex_data["op"], 
                    "store_data": ex_data["store_data"],
                    "result": result, 
                    "next_pc": next_pc
                }
                
                
                seq_pc = (ex_data["curr_pc"] + 4) & 0xFFFFFFFF
                if (is_branch(ex_data["op"]) or is_jump(ex_data["op"])) and (next_pc != seq_pc):
                    branch_taken = True
                    self.pc = next_pc  
                    flush_cycles = 2   
            else:
                self.pipeline_regs["EX/MEM"] = None
            
            
            id_data = dummy_regs["IF/ID"]
            stall = False
            
            if id_data is not None and not branch_taken:
                op, decoded = self.decode(id_data["instruction"])
                rs1 = decoded.get("rs1", 0)
                rs2 = decoded.get("rs2", 0)
                
                
                hazard_regs = set()
                
                
                if dummy_regs["ID/EX"] is not None:
                    rd_ex = dummy_regs["ID/EX"]["decoded"].get("rd", 0)
                    op_ex = dummy_regs["ID/EX"]["op"]
                    if rd_ex != 0 and not (is_store(op_ex) or is_branch(op_ex)):
                        hazard_regs.add(rd_ex)
                
                
                if dummy_regs["EX/MEM"] is not None:
                    rd_mem = dummy_regs["EX/MEM"]["decoded"].get("rd", 0)
                    op_mem = dummy_regs["EX/MEM"]["op"]
                    if rd_mem != 0 and not (is_store(op_mem) or is_branch(op_mem)):
                        hazard_regs.add(rd_mem)
                
                
                if (rs1 != 0 and rs1 in hazard_regs) or (rs2 != 0 and rs2 in hazard_regs):
                    stall = True
                    
                    self.pipeline_regs["ID/EX"] = None
                else:
                    
                    op1, op2 = self.operand_fetch(decoded, self.registers, id_data["curr_pc"])
                    self.pipeline_regs["ID/EX"] = {
                        "curr_pc": id_data["curr_pc"], 
                        "decoded": decoded,
                        "op": op, 
                        "op1": op1, 
                        "op2": op2,
                        "store_data": self.registers[decoded["rs2"]] if decoded["rs2"] != 0 else 0
                    }
            elif branch_taken:
                
                self.pipeline_regs["ID/EX"] = None
            else:
                self.pipeline_regs["ID/EX"] = None
            
           
            if not stall and flush_cycles == 0 and fetch_enabled:
                try:
                    instruction, next_pc = self.fetch(self.pc, self.mem)
                    if instruction is not None:
                        self.pipeline_regs["IF/ID"] = {
                            "instruction": instruction,
                            "curr_pc": self.pc
                        }
                        if not branch_taken:  
                            self.pc = (self.pc + 4) & 0xFFFFFFFF
                    else:
                        self.pipeline_regs["IF/ID"] = None
                        fetch_enabled = False
                except:
                    self.pipeline_regs["IF/ID"] = None
                    fetch_enabled = False
            elif stall:
                
                pass
            elif flush_cycles > 0 or branch_taken:
                
                self.pipeline_regs["IF/ID"] = None
            
            
            if flush_cycles > 0:
                flush_cycles -= 1
        
        self.logr.info(f"Simulation complete: executed {committed} instructions in {cycle} cycles.")