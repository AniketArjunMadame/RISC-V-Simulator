.section .data
n: .word 6

.section .text
.globl main
main:
    la   t0, n
    lw   a0, 0(t0)
    jal  fact     

    j    halt     

fact:
    addi sp, sp, -16
    sw   ra, 12(sp) 
    sw   a0, 8(sp)  

    li   t0, 1           
    slt  t2, t0, a0      
    bne  t2, zero, recurse

base_case:
    li   a0, 1      
    j    end_fact

recurse:
    addi a0, a0, -1 
    jal  fact       
    lw   t1, 8(sp)  
    mul  a0, t1, a0 

end_fact:
    lw   ra, 12(sp) 
    addi sp, sp, 16 
    jr   ra 
halt:
    j halt

