DATA 170 60 255 85 3 144 0 200 19 222 134 41 176 99 7 121

LD 0 0   		#Loads 170 in R0; 		R0 = 0xAA
LD 1 4   		#Loads 3 in R1;   		R1 = 0x3
LD 2 8           	#Loads 19 in R2;  		R2 = 0x13
ADD 3 2 2  		#R3 = R2 + R2 = 19 + 19 = 38    R3 = 0x26
ADD 0 2 3   		#R0 = R2 + R3 = 19 + 38 = 57	R0 = 0x39
MULT 0 0 1		#R0 = R0 * R1 = 57 * 3 = 171	R0 = 0xAB
MULT 2 1 2		#R2 = R1 * R2 = 3 * 19 = 57	R2 = 0x39
STR 0 0			#Stores R0 = 171 = 0xAB into memory location index 0 
STR 1 4			#Stores R1 = 3 = 0x3 into memory location index 4
STR 2 8			#Stores R2 = 57 = 0x39 into memory location index 8
STR 3 15		#Stores R3 = 38 = 0x26 into memory location index 15