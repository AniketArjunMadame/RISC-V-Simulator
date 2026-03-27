import struct

def load(ram, r5ob_path, start=0x80000000):
    """
    Load binary file into memory.
    returns a memory (dictionary).
    """
    mem = {}

    with open(r5ob_path, 'rb') as f:
        offset = start
        while byte := f.read(1):
            ram.write(offset, byte[0])
            offset += 1

    return mem
