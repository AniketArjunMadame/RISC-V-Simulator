import json

class Statistics:
    def __init__(self, loggr):
        self.clock_cycles = 0
        self.instruction_count = 0
        self.memory_accesses = 0
        self.logr = loggr

    def increment_clock_cycle(self):
        self.clock_cycles += 1

    def increment_instruction_count(self):
        self.instruction_count += 1

    def increment_memory_access(self):
        self.memory_accesses += 1

    def increment_register_access(self):
        self.register_accesses += 1

    def write_statistics(self, filename):
        stats = {
            "clock_cycles": self.clock_cycles,
            "instructions_executed": self.instruction_count,
            "memory_accesses": self.memory_accesses,
        }
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=4)
        self.logr.info(f"Statistics saved to {filename}")

    def reset(self):
        self.clock_cycles = 0
        self.instruction_count = 0
        self.memory_accesses = 0
        self.register_accesses = 0
