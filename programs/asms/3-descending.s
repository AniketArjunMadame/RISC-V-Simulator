.section .data
	.align 2
a:
	.word 70
	.word 80
	.word 40
	.word 20
	.word 10
	.word 30
	.word 50
	.word 60
n:
	.word 8

.section .text
.globl main
main:
	la t0, a              
	lw t1, n              
	addi t1, t1, -1       
	li t2, 0              

outer_loop:
	bge t2, t1, end       

	li t3, 0              
inner_loop:
	sub t4, t1, t2        
	bge t3, t4, next_outer 

	slli t5, t3, 2        
	add t6, t0, t5        
	lw t4, 0(t6)    
     
	addi t5, t3, 1        
	slli t5, t5, 2        
	add t5, t0, t5       
	lw t6, 0(t5)          

	blt t4, t6, swap      

	j skip_swap

swap:
	sw t6, 0(t0)          
	sw t4, 0(t5)          

skip_swap:
	addi t3, t3, 1        
	j inner_loop

next_outer:
	addi t2, t2, 1        
	j outer_loop

end:
	li a7, 93             


halt:
	j halt


