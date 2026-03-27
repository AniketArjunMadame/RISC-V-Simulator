.section .data

num1: .word 25        
num2: .word 42       
num3: .word 17        


.section .text
.globl main
main:
	    # Load values from memory into registers
    la t1, num1        # Load address of num1 into t1
    lw x1, 0(t1)       # Load value at address in t1 into x1

    la t2, num2        # Load address of num2 into t2
    lw x2, 0(t2)       # Load value at address in t2 into x2

    la t3, num3        # Load address of num3 into t3
    lw x3, 0(t3)       # Load value at address in t3 into x3

    # Compare x1 and x2
    bge x1, x2, L1     # if x1 >= x2, jump to L1
    mv t0, x2          # else, t0 = x2
    j L2

L1:
    mv t0, x1          # t0 = x1

L2:
    # Compare t0 and x3
    bge t0, x3, L3     # if t0 >= x3, jump to L3
    mv x10, x3         # else, x10 = x3 (maximum)
    j END

L3:
    mv x10, t0         # x10 = t0 (maximum)

END:
halt:
	j halt
