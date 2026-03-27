RISCV=riscv-none-elf-

RISCV_AS_FLAGS=-T./custom/test.ld -static -mcmodel=medany \
	       -fvisibility=hidden -nostdlib -nostartfiles -g \
	       ./custom/crt.S -I ./custom -march=rv32ima_zicsr \
	       -mabi=ilp32 

RISCV_C_FLAGS=-T./custom/test.ld -static -mcmodel=medany \
	       -fvisibility=hidden -nostdlib -nostartfiles -g -O0 \
	       ./custom/syscalls.c ./custom/crt.S -lgcc \
	       -I./custom/env -I./custom/common \
	       -march=rv32imc_zba_zbb_zbs_zbc_zicsr_zifencei -mabi=ilp32 
#	       -march=rv32ima_zicsr -mabi=ilp32 

ASMs    := $(wildcard asms/*.s)
CSRCs   := $(wildcard c_tests/*.c)
ABINs    := $(patsubst asms/%.s,bins/asms/%.r5o,$(ASMs))
CBINs    := $(patsubst c_tests/%.c,bins/c_tests/%.r5o,$(CSRCs))
ADUMPs   := $(patsubst asms/%.s,dumps/asms/%.r5o.dump,$(ASMs))
CDUMPs   := $(patsubst c_tests/%.c,dumps/c_tests/%.r5o.dump,$(CSRCs))
ARUNs    := $(patsubst asms/%.s,runs/asms/%,$(ASMs))
CRUNs    := $(patsubst c_tests/%.c,runs/c_tests/%,$(CSRCs))


.PHONY: all run_all asms asms_run c_tests c_tests_run
all: asms c_tests
asms: $(ABINs) $(ADUMPs)
c_tests: $(CBINs) $(CDUMPs)
run_all: run_asms run_c_tests
run_asms: $(ARUNs)
run_c_tests: $(CRUNs)


bins/asms/%.r5o: asms/%.s
	mkdir -p bins/asms
	$(RISCV)gcc $< $(RISCV_AS_FLAGS) -o $@
	$(RISCV)objcopy -O binary $@ $@b

bins/c_tests/%.r5o: c_tests/%.c
	mkdir -p bins/c_tests
	$(RISCV)gcc $< $(RISCV_C_FLAGS) -o $@
	$(RISCV)objcopy -O binary $@ $@b

dumps/asms/%.r5o.dump: bins/asms/%.r5o
	mkdir -p dumps/asms
	$(RISCV)objdump -d $< > $@

dumps/c_tests/%.r5o.dump: bins/c_tests/%.r5o
	mkdir -p dumps/c_tests
	$(RISCV)objdump -j .text -j .sdata -d $< > $@

runs/asms/%: bins/asms/%.r5o
	mkdir -p runs/asms
	spike --steps=2000  --log-commits --isa=rv32ima_zicsr \
		--priv=msu  -l $< 2> $@.iss

runs/c_tests/%: bins/c_tests/%.r5o
	mkdir -p runs/c_tests
	spike --steps=3000  --log-commits \
		--isa=rv32imc_zba_zbb_zbs_zbc_zicsr_zifencei \
		--priv=msu  -l $< 2> $@.iss


.PHONY: clean
clean:
	rm -rf bins dumps runs

