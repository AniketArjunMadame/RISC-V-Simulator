    .section .data
    .align 2
count:
    .word 0
    .word 0
    .word 0
    .word 0
    .word 0
    .word 0
    .word 0
    .word 0
    .word 0
    .word 0
    .word 0
marks:
    .word 2
    .word 3
    .word 0
    .word 5
    .word 10
    .word 7
    .word 1
    .word 10
    .word 10
    .word 8
    .word 9
    .word 6
    .word 7
    .word 8
    .word 2
    .word 4
    .word 5
    .word 0
    .word 9
    .word 1
n:
    .word 20

    .section .text
    .globl main
main:
   la x10,marks
   la x11,count
la x12,n
lw x1,0(x12)

loop:
beq x1,x0, halt
lw x2,0(x10)
slli x3,x2,2
add x4,x11,x3
lw x5,0(x4)
addi x5,x5,1
sw x5,0(x4)

addi x10,x10,4
addi x1,x1,-1
j loop

halt:
   j halt






