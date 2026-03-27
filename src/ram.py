class RAM:
    def __init__(self, logger):
        self.mem = {}
        self.logr = logger

    def read(self, address):
        if address in self.mem:
            return self.mem[address]
        else:
            raise ValueError(f"Address {hex(address)} not found in memory.")

    def write(self, address, data):
        self.mem[address] = data

    def read_halfword(self, address):
        word = 0
        for i in range(2):
            word |= self.read(address + i) << (i * 8)
        return word

    def write_halfword(self, address, data):
        for i in range(2):
            self.write(address + i, (data >> (i * 8)) & 0xFF)

    def read_word(self, address):
        word = 0
        for i in range(4):
            word |= self.read(address + i) << (i * 8)
        return word

    def write_word(self, address, data):
        for i in range(4):
            self.write(address + i, (data >> (i * 8)) & 0xFF)

    def dump(self, start, end):
        for i in range(start, end):
            try:
                self.logr.debug(f" mem[{hex(i)}] -> {hex(self.read(i))}")
                self.logr.out(f" {hex(i)} => {hex(self.read(i))}")
            except ValueError:
                self.logr.debug(f" mem[{hex(i)}] -> INVALID")

