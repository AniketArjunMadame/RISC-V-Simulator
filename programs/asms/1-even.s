.section .data
	.align 2
n:	
	.word 5
l:
	.word 2
	.word -1
	.word 7
	.word 5
	.word 3

.section .text
.globl main
main:

    la   x1, n
    lw   x2, 0(x1)

    la   x1,l

    li   x10, 0

loop:
    beq  x2, x0, done 

    lw   x3, 0(x1) 

    blt  x3, x0, skip 

    andi x4, x3, 1
    bne  x4, x0, skip 

    addi x10, x10, 1 

skip:
    addi x1, x1, 4 
    addi x2, x2, -1 
    j    loop

done:
halt:
    j halt
