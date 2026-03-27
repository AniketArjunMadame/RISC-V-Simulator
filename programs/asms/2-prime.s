.section .data
    .align 2
a:
    .word 10          

    .section .text
    .globl main
main:
    
    la t1, a
    lw t0, 0(t1)      

    
    li t2, 1
    ble t0, t2, not_prime

    
    li t2, 2
    beq t0, t2, is_prime

    
    andi t3, t0, 1
    beqz t3, not_prime

   
    li t1, 3

check_loop:
    
    mul t2, t1, t1
    bgt t2, t0, is_prime

    
    rem t3, t0, t1
    beqz t3, not_prime    

    
    addi t1, t1, 2
    j check_loop

is_prime:
    li a0, 1          
    j halt

not_prime:
    li a0, -1         

halt:
    j halt           


