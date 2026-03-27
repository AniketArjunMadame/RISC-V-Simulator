.section .data
A:  .word 1, 2, 3
    .word 4, 2, 6
    .word 7, 8, 9

B:  .word 9, 8, 7
    .word 6, 5, 3
    .word 7, 2, 1

C:  .word 0, 0, 0
    .word 0, 0, 0
    .word 0, 0, 0

result: .word 0

.section .text
.globl main
main:


la a0, A      
    la a1, B      
    la a2, C      
   
    jal ra, matmul
   
    la t0, result
    sw a0, 0(t0)
     
matmul:
    addi sp, sp, -16    
    sw ra, 12(sp)          
    sw s0, 8(sp)          
    sw s1, 4(sp)          
    sw s2, 0(sp)          

    li s0, 0              

row_loop:
    bge s0, t1, check_zero  

    li s1, 0              

col_loop:
    bge s1, t1, next_row    

    li t0, 0              
    li s2, 0            

inner_loop:
    bge s2, t1, store_c    

    li t1, 3
    mul t2, s0, t1        
    add t2, t2, s2        
    slli t2, t2, 2        
    add t3, a0, t2        
    lw t4, 0(t3)          

    li t1, 3
    mul t2, s2, t1        
    add t2, t2, s1        
    slli t2, t2, 2        
    add t3, a1, t2        
    lw t5, 0(t3)          

    mul t6, t4, t5        
    add t0, t0, t6        

    addi s2, s2, 1
    j inner_loop

store_c:
 
    li t1, 3
    mul t2, s0, t1
    add t2, t2, s1
    slli t2, t2, 2
    add t3, a2, t2
    sw t0, 0(t3)

    addi s1, s1, 1
    j col_loop

next_row:
    addi s0, s0, 1
    j row_loop

check_zero:
    li s0, 0

check_loop:
    bge s0, t1, all_nonzero  
    slli t1, s0, 2          
    add t2, a2, t1
    lw t3, 0(t2)            
    beq t3, x0, return_zero
    addi s0, s0, 1
    j check_loop

return_zero:
    li a0, 0                
    j end_func

all_nonzero:
    li a0, 1                

end_func:
    lw ra, 12(sp)          
    lw s0, 8(sp)            
    lw s1, 4(sp)            
    lw s2, 0(sp)            
    addi sp, sp, 16
    jr ra


halt:
j halt
