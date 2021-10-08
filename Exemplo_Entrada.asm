main:
	add $s0, $zero, $zero #0x00008020
	add $s1, $zero, $zero #0x00008820
	addi $t0, $zero, 6 #0x20080006
	addi $t1, $zero, 12 #0x2009000C
	addi $t2, $zero, 3 #0x200A0003
loop:	beq $t0, $zero, exit #0x11000028
	add $s0, $s0, $t1 #0x02098020 s0=117 6
	add $t1, $t1, $t2 #0x012A4820 t1=30
	addi $t0, $t0, -1 #0x2108FFFF
	j loop #0x08000014
exit:
