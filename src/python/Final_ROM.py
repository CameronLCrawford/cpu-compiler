#All of the control lines for the CPU
(IC0, IC1, IC2, IC3,
OC0, OC1, OC2, OC3,
AC0, AC1, AC2, AC3,
CI, ADRI, SI, SD,
MCA, MSA, MHLA,
ZFO, SFO,
RI, RO, RST, OUT, HLT) = (2**i for i in range(26))

#Defines each of the 'register in' signals
AI = IC0 #A in
BI = IC1 #B in
HI = IC1 | IC0 #H in
LI = IC2 #L in
CHI = IC2 | IC0 #Counter High in
CLI = IC2 | IC1 #Counter Low in
BHI = IC2 | IC1 | IC0 #Base High in
BLI = IC3 #Base Low in
AHI = IC3 | IC0 #Address High in
ALI = IC3 | IC1 #Address Low in
SHI = IC3 | IC1 | IC0 #Stack High in
SLI = IC3 | IC2 #Stack Low in
II = IC3 | IC2 | IC0 #Instruction in
ATI = IC3 | IC2 | IC1 #A Temp in
FI = IC3 | IC2 | IC1 | IC0 #Flags in

#'Register out' signals
AO = OC0 #A out
BO = OC1 #B out
HO = OC1 | OC0 #H out
LO = OC2 #L out
CHO = OC2 | OC0 #Counter High out
CLO = OC2 | OC1 #Counter Low out
BHO = OC2 | OC1 | OC0 #Base High out
BLO = OC3 #Base Low out
AHO = OC3 | OC0 #Address High out
ALO = OC3 | OC1 #Address Low out
SHO = OC3 | OC1 | OC0 #Stack High out
SLO = OC3 | OC2 #Stack Low out
IO = OC3 | OC2 | OC0 #Instruction out
ATO = OC3 | OC2 | OC1 #A Temp out
FO = OC3 | OC2 | OC1 | OC0 #Flags out

#Arithmetic control signals
ADD = AC0
SUB = AC1
AND = AC1 | AC0
OR = AC2
XOR = AC2 | AC0
INC = AC2 | AC1
DEC = AC2 | AC1 | AC0
NEG = AC3
ADDC = AC3 | AC0
SUBC = AC3 | AC1
INCC = AC3 | AC1 | AC0
DECC = AC3 | AC2
UNEG = AC3 | AC2 | AC0

instructions = [
    [], #NOP (no operation) does nothing
    ################### ARITHMETIC INSTRUCTIONS ############################
    #UNCONDITIONAL ARITHMETIC OPERATIONS
    #Addition (1 - 7)
    [CI | ADRI | RO | HI, CI | ADRI | RO | ALI, HO | AHI, RO | ATI, ADD | AI], #ADD (add) adds value in memory address in adjacent bytes to accumulator
    [AO | ATI, ADD | AI], #ADDA (add A) adds value in accumulator to accumulator
    [BO | ATI, ADD | AI], #ADDB (add B) adds value in B to accumulator
    [HO | ATI, ADD | AI], #ADDH (add H) adds value in H to accumulator
    [LO | ATI, ADD | AI], #ADDL (add L) adds value in L to accumulator
    [HO | AHI, LO | ALI, RO | ATI, ADD | AI], #ADDM (add M) adds value in M to accumulator
    [CI | ADRI | RO | ATI, ADD | AI], #ADDI (add immediate) adds value in adjacent btye to accumulator
    #Subtraction (8 - 14)
    [CI | ADRI | RO | HI, CI | ADRI | RO | ALI, HO | AHI, RO | ATI, SUB | AI], #SUB (sub) subtracts value in memory address in adjacent bytes from accumulator
    [AO | ATI, SUB | AI], #SUBA (subtract A) subtracts value in accumulator from accumulator
    [BO | ATI, SUB | AI], #SUBB (subtract B) subtracts value in B from accumulator
    [HO | ATI, SUB | AI], #SUBH (subtract H) subtracts value in H from accumulator
    [LO | ATI, SUB | AI], #SUBL (subtract L) subtracts value in L from accumulator
    [HO | AHI, LO | ALI, RO | ATI, SUB | AI], #SUBM (subtract M) subtracts the value in M from the accumulator
    [CI | ADRI | RO | ATI, SUB | AI], #SUBI (subtract immediate) subtracts the value in adjacent byte from accumulator
    #Binary AND (15 - 21)
    [CI | ADRI | RO | HI, CI | ADRI | RO | ALI, HO | AHI, RO | ATI, AND | AI], #AND (and) ands value in memory address in adjacent bytes with accumulator
    [AO | ATI, AND | AI], #ANDA (and A) ands value in accumulator with accumulator
    [BO | ATI, AND | AI], #ANDB (and B) ands value in B with accumulator
    [HO | ATI, AND | AI], #ANDH (and H) ands value in H with accumulator
    [LO | ATI, AND | AI], #ANDL (and L) ands value in L with accumulator
    [HO | AHI, LO | ALI, RO | ATI, AND | AI], #ANDM (and M) ands value in M with accumulator
    [CI | ADRI | RO | ATI, AND | AI], #ANDI (and immediate) ands value in adjacent byte with accumulator
    #Binary OR (22 - 28)
    [CI | ADRI | RO | HI, CI | ADRI | RO | ALI, HO | AHI, RO | ATI, OR | AI], #OR (or) ors value in memory address in adjacent bytes with accumulator
    [AO | ATI, OR | AI], #ORA (or A) ors value in accumulator with accumulator
    [BO | ATI, OR | AI], #ORB (or B) ors value in B with accumulator
    [HO | ATI, OR | AI], #ORH (or H) ors value in H with accumulator
    [LO | ATI, OR | AI], #ORL (or L) ors value in L with accumulator
    [HO | AHI, LO | ALI, RO | ATI, OR | AI], #ORM (or M) ors value in M with accumulator
    [CI | ADRI | RO | ATI, OR |AI], #ORI (or immediate) ors value in adjacent byte with accumulator
    #Binary XOR (29 - 35)
    [CI | ADRI | RO | HI, CI | ADRI | RO | ALI, HO | AHI, RO | ATI, XOR | AI], #XOR (exclusive or) xors value in memory address in adjacent bytes with accumulator
    [AO | ATI, XOR | AI], #XORA (exclusive or A) xors value in accumulator with accumulator
    [BO | ATI, XOR | AI], #XORB (exclusive or B) xors value in B with accumulator
    [HO | ATI, XOR | AI], #XORH (exclusive or H) xors value in H with accumulator
    [LO | ATI, XOR | AI], #XORL (exclusive or L) xors value in L with accumulator
    [HO | AHI, LO | ALI, RO | ATI, XOR | AI], #XORM (exclusive or M) xors value in M with accumulator
    [CI | ADRI | RO | ATI, XOR |AI], #XORI (exclusive or immediate) xors value in adjacent byte with accumulator
    #Other (36 - 38)
    [INC | AI], #INC (increment) increments accumulator
    [DEC | AI], #DEC (decrement) decrements accumulator
    [NEG | AI], #NEG (negate) binary negates accumulator
    [UNEG | AI], #UNEG (unary negate) unary negates the accumulator
    #CARRY CONDITIONAL OPERATIONS
    #Addition (40 - 46)
    [CI | ADRI | RO | HI, CI | ADRI | RO | ALI, HO | AHI, RO | ATI, ADDC | AI], #ADDC (add carry conditional) adds value in memory address in adjacent bytes to accumulator (carry conditional)
    [AO | ATI, ADDC | AI], #ADDCA (add carry conditional A) adds value in accumulator to accumulator (carry conditional)
    [BO | ATI, ADDC | AI], #ADDCB (add carry conditional B) adds value in B to accumulator (carry conditional)
    [HO | ATI, ADDC | AI], #ADDCH (add carry conditional H) adds value in H to accumulator (carry conditional)
    [LO | ATI, ADDC | AI], #ADDCL (add carry conditional L) adds value in L to accumulator (carry conditional)
    [HO | AHI, LO | ALI, RO | ATI, ADDC | AI], #ADDCM (add carry conditional M) adds value in M to accumulator (carry conditional)
    [CI | ADRI | RO | ATI, ADDC | AI], #ADDCI (add carry conditional immediate) adds value in adjacent btye to accumulator (carry conditional)
    #Subtraction (47 - 53)
    [CI | ADRI | RO | HI, CI | ADRI | RO | ALI, HO | AHI, RO | ATI, SUBC | AI], #SUBC (subtract carry conditional) subtracts value in memory address in adjacent bytes from accumulator (carry conditional)
    [AO | ATI, SUBC | AI], #SUBCA (subtract carry conditional A) subtracts value in accumulator from accumulator (carry conditional)
    [BO | ATI, SUBC | AI], #SUBCB (subtract carry conditional B) subtracts value in B from accumulator (carry conditional)
    [HO | ATI, SUBC | AI], #SUBCH (subtract carry conditional H) subtracts value in H from accumulator (carry conditional)
    [LO | ATI, SUBC | AI], #SUBCL (subtract carry conditional L) subtracts value in L from accumulator (carry conditional)
    [HO | AHI, LO | ALI, RO | ATI, SUBC | AI], #SUBM (subtract carry conditional M) subtracts the value in M from the accumulator (carry conditional)
    [CI | ADRI | RO | ATI, SUBC | AI], #SUBCI (subtract carry conditional immediate) subtracts the value in adjacent byte from accumulator (carry conditional)
    #Other (54 - 55)
    [INCC | AI], #INCC (increment carry conditional) increments accumulator (carry conditional)
    [DECC | AI], #DECC (decrement carry conditional) decrements accumulator (carry conditional)
    #################### REGISTER INSTRUCTIONS #####################
    #MOVE INSTRUCTIONS
    #Move to A (56 - 58)
    [BO | AI], #MOVAB (move A B) moves value in B to A
    [HO | AI], #MOVAH (move A H) moves value in H to A
    [LO | AI], #MOVAL (move A L) moves value in L to A
    #Move to B (59 - 61)
    [AO | BI], #MOVBA (move B A) moves value in A to B
    [HO | BI], #MOVBH (move B H) moves value in H to B
    [LO | BI], #MOVBL (move B L) moves value in L to B
    #Move to H (62 - 64)
    [AO | HI], #MOVHA (move H A) moves value in A to H
    [BO | HI], #MOVHB (move H B) moves value in B to H
    [LO | HI], #MOVHL (move H L) moves value in L to H
    #Move to L (65 - 67)
    [AO | LI], #MOVLA (move L A) moves value in A to L
    [BO | LI], #MOVLB (move L B) moves value in B to L
    [HO | LI], #MOVLH (move L H) moves value in H to L
    #LOAD INSTRUCTIONS
    #Load A (68 - 70)
    [CI | ADRI | RO | ATI, CI | ADRI | RO | ALI, ATO | AHI, RO | AI], #LDA (load A) loads A with value in address in adjacent bytes
    [CI | ADRI | RO | AI], #LDAI (load A immediate) loads A with adjacent byte
    [HO | AHI, LO | ALI, RO | AI], #LDAM (load A M) loads A with value in M
    #Load B (71 - 73)
    [CI | ADRI | RO | ATI, CI | ADRI | RO | ALI, ATO | AHI, RO | BI], #LDB (load B) loads B with value in address in adjacent bytes
    [CI | ADRI | RO | BI], #LDBI (load B immediate) loads B with adjacent byte
    [HO | AHI, LO | ALI, RO | BI], #LDBM (load B M) loads B with value in M
    #Load H (74 - 76)
    [CI | ADRI | RO | ATI, CI | ADRI | RO | ALI, ATO | AHI, RO | HI], #LDH (load H) loads H with value in address in adjacent bytes
    [CI | ADRI | RO | HI], #LDHI (load H immediate) loads H with adjacent byte
    [HO | AHI, LO | ALI, RO | HI], #LDHM (load H M) loads H with value in M
    #Load L (77 - 79)
    [CI | ADRI | RO | ATI, CI | ADRI | RO | ALI, ATO | AHI, RO | LI], #LDL (load L) loads L with value in address in adjacent bytes
    [CI | ADRI | RO | LI], #LDLI (load L immediate) loads L with adjacent byte
    [HO | AHI, LO | ALI, RO | LI], #LDLM (load L M) loads L with value in M
    #STORE INSTRUCTIONS (80 - 81)
    [CI | ADRI | RO | ATI, CI | ADRI | RO | ALI, ATO | AHI, AO | RI], #STA (store A) stores accumulator in address specified by neBt two adjacent bytes
    [HO | AHI, LO | ALI, AO | RI], #STAM (store A) stores the accumulator in the value in M
    ########################### JUMP INSTRUCTIONS ################################
    #UNCONDITIONAL JUMPS (82 - 83)
    [HO | CHI, LO | CLI], #JMPM (jump M) jumps to value in H and L registers
    [CI | ADRI | RO | ATI, CI | ADRI | RO | CLI, ATO | CHI], #JMI (jump immediate) jumps to value in adjacent bytes
    #CONDITIONAL JUMPS (84 - 99)
    #The reason that these are left blank is because the data for them is only written
    #into specific addresses where both the opcode AND the flags necessary for that
    #instruction to execute are correct. All other instructions are written into all
    #16 (4 flags) locations regardless of flag status.
    [], #JNM (jump if negative M) jumps to M if A is negative
    [], #JNI (jump if negative immediate) jumps to immediate if negative
    [], #JPM (jump if positive M) jumps to M if A if positive
    [], #JPI (jump if positive immediate) jumps to immediate if positive
    [], #JZM (jump if zero M) jumps to M if A register is zero
    [], #JZI (jump if zero immediate) jumps to immediate if zero
    [], #JNZM (jump if not zero M) jumps to M if A is not zero
    [], #JNZI (jump if not zero immediate) jumps to immediate if not zero
    [], #JEM (jump if even M) jumps to M if A if even
    [], #JEI (jump if even immediate) jumps to immediate if even
    [], #JOM (jump if odd M) jump to M if A is odd
    [], #JOI (jump if odd immediate) jumps to immediate if A is odd
    [], #JCM (jump if carry M) jumps to M if carry flag is set
    [], #JCI (jump if carry immediate) jumps to immediate if carry bit is set
    [], #JNCM (jump if no carry M) jumps to M if the carry flag is not set
    [], #JNCI (jump if no carry immediate) jumps to immediate if carry flag not set
    ##################### STACK INSTRUCTIONS #############################
    #PUSH (100 - 108)
    [CI | ADRI | RO | ATI, CI | ADRI | RO | ALI, ATO | AHI, SD | RO | ATI, MSA | ATO | RI], #PUSH (push) pushes the value in the address in the adjacent two bytes onto the stack
    [CI | ADRI | RO | ATI | SD, MSA | ATO | RI], #PUSHI (push immediate) pushes the immediate onto the stack
    [SD, MSA, AO | RI], #PUSHA (push A) pushes register A onto stack
    [SD, MSA, BO | RI], #PUSHB (push B) pushes register B onto stack
    [SD, MSA, HO | RI], #PUSHH (push H) pushes register H onto stack
    [SD, MSA, LO | RI], #PUSHL (push L) pushes register L onto stack
    [SD, MSA, FO | RI], #PUSHS (push status) pushes status byte onto stack
    [SD, MSA, BHO | RI, SD, MSA, BLO | RI], #PUSHBP (push base pointer) pushes the base pointer onto the stack
    [SD, MSA, CHO | RI, SD, MSA, CLO | RI], #PUSHC (push counter) pushes the program counter onto the stack
    #POP (109 - 116)
    [MSA, SI | RO | BI, MCA, CI | ADRI | RO | ATI, CI | ADRI | RO | ALI, ATO | AHI, BO | RI], #POP (pop) pops the stack into the address of the adjacent two bytes NOTE : alters B register
    [MSA, SI | RO | AI], #POPA (pop A) pops the stack into A
    [MSA, SI | RO | BI], #POPB (pop B) pops the stack into B
    [MSA, SI | RO | HI], #POPH (pop H) pops the stack into H
    [MSA, SI | RO | LI], #POPL (pop L) pops the stack into L
    [MSA, SI | RO | FI], #POPS (pop status) pops the stack into the flags register
    [MSA, SI | RO | BLI, MSA, SI | RO | BHI], #POPBP (pop base pointer) pops the base pointer from the stack
    [MSA, SI | RO | CLI, MSA, SI | RO | CHI], #POPC (pop counter) pops the program counter from the stack
    #STACK LOAD (117 - 122)
    [CI | ADRI | RO | HI, CI | ADRI | RO | ALI, HO | AHI, RO | SHI], #LDSPH (load stack pointer high) loads stack pointer (high) with value in address in adjacent bytes
    [CI | ADRI | RO | HI, CI | ADRI | RO | ALI, HO | AHI, RO | SLI], #LDSPL (load stack pointer low) loads stack pointer (low) with value in address in adjacent bytes
    [CI | ADRI | RO | SHI, CI | ADRI | RO | SLI], #LDSP (load stack pointer) loads stack pointer with DBYTE in adjacent two bytes
    [HO | AHI, LO | ALI, RO | SHI], #LDSPHM (load stack pointer high M) loads stack pointer (high) with value in M
    [HO | AHI, LO | ALI, RO | SLI], #LDSPLM (load stack pointer low M) loads stack pointer (low) with value in M
    [HO | SHI, LO | SLI], #LDSPHL (load stack pointer H L) loads stack pointer with H L pair
    #BASE LOAD (123 - 128)
    [CI | ADRI | RO | HI, CI | ADRI | RO | ALI, HO | AHI, RO | BHI], #LDBPH (load base pointer high) loads base pointer (high) with value in address in adjacent bytes
    [CI | ADRI | RO | HI, CI | ADRI | RO | ALI, HO | AHI, RO | BLI], #LDBPL (load base pointer low) loads base pointer (low) with value in address in adjacent bytes
    [CI | ADRI | RO | BHI, CI | ADRI | RO | BLI], #LDBP (load base pointer) loads base pointer with DBYTE in adjacent two bytes
    [HO | AHI, LO | ALI, RO | BHI], #LDBPHM (load base pointer high M) loads base pointer (high) with value in M
    [HO | AHI, LO | ALI, RO | BLI], #LDBPLM (load base pointer low M) loads base pointer (low) with value in M
    [HO | BHI, LO | BLI], #LDBPHL (load base pointer H L) loads base pointer with H L pair
    #STACK REGISTER MOVE (129 - 130)
    [SHO | BHI, SLO | BLI], #MOVBPSP (move base pointer stack pointer) moves the value in the stack pointer to the base pointer
    [BHO | SHI, BLO | SLI], #MOVSPBP (move stack pointer base pointer) moves the value in the base pointer to the stack pointer
    #OTHER (131 - 132)
    [MHLA, RO | AI], #MARHL (move address register H L pair) stores the value pointed to by the HL pair to the accumulator
    [MHLA, AO | RI], #MHLAR (move H L pair address register) stores the accumulator in the value pointed to by the H L pair
    #################### 16 BIT INSTRUCTIONS #############################
    #MOVE (133 - 134)
    [SHO | HI, SLO | LI], #MPHSP (move pair H L stack pointer) moves the value in the stack pointer to the H L pair
    [BHO | HI, BLO | LI], #MPHBP (move pair H L base pointer) moves the value in the base pointer to the H L pair
    #ADD (135 - 139)
    [CI | ADRI | RO | ATI, LO | AI, ADD | LI, CI | ADRI | RO | ATI, HO | AI, ADDC | HI], #APHI (add pair H immediate) adds the immediate two bytes to the H pair NOTE : little endian immediate
    [LO | ATI, SLO | AI, ADD | SLI, HO | ATI, SHO | AI, ADDC | SHI], #APSPH (add pair stack pointer H) adds the value in the H pair to the stack and leaves it in the stack pointer
    [LO | ATI, BLO | AI, ADD | BLI, HO | ATI, BHO | AI, ADDC | BHI], #APBPH (add pair base pointer H) adds the value in the H pair to the base and leaves it in the base pointer
    [CI | ADRI | RO | ATI, SLO | AI, ADD | SLI, CI | ADRI | RO | ATI, SHO | AI, ADDC | SHI], #APSPI (add pair stack pointer immediate) adds the immediate two bytes to the stack pointer NOTE : little endian immediate
    [CI | ADRI | RO | ATI, BLO | AI, ADD | BLI, CI | ADRI | RO | ATI, BHO | AI, ADDC | BHI], #APBPI (add pair base pointer immediate) adds the immediate two bytes to the base pointer NOTE : little endian immediate
    #SUBTRACT (140 - 144)
    [CI | ADRI | RO | ATI, LO | AI, SUB | LI, CI | ADRI | RO | ATI, HO | AI, SUBC | HI], #SPHI (subtract pair H immediate) subtracts the immediate two bytes from the H pair NOTE : little endian immediate
    [LO | ATI, SLO | AI, SUB | SLI, HO | ATI, SHO | AI, SUBC | SHI], #SPSPH (subtract pair stack pointer H) subbtracts the value in the H pair from the stack and leaves it in the stack pointer
    [LO | ATI, BLO | AI, SUB | BLI, HO | ATI, BHO | AI, SUBC | BHI], #SPBPH (subtract pair base pointer H) subtracts the value in the H pair from the base and leaves it in the base pointer
    [CI | ADRI | RO | ATI, SLO | AI, SUB | SLI, CI | ADRI | RO | ATI, SHO | AI, SUBC | SHI], #SPSPI (subtract pair stack pointer immediate) subtracts the immediate two bytes from the stack pointer NOTE : little endian immediate
    [CI | ADRI | RO | ATI, BLO | AI, SUB | BLI, CI | ADRI | RO | ATI, BHO | AI, SUBC | BHI], #SPBPI (subtract pair base pointer immediate) subtracts the immediate two bytes from the base pointer NOTE : little endian immediate
    #################### OTHER INSTRUCTIONS ###############################
    [ZFO | AI], #ZFO (zero flag out) move the zero flag to the accumulator to be used in compare operations
    [SFO | AI], #SFO (sign flag out) move the sign flag to the accumulator to be used in compare operations
    [AO | OUT], #OUT (out) outputs the value in the accumulator
    [HLT] #HLT (halt) stops program execution
]

final_instructions = []

for i, instruction in enumerate(instructions):
    #Each instruction starts with these two microinstructions
    final_instruction = [MCA, RO | II]
    final_instruction += instruction
    if i in (82, 83): #Doesn't increment counter on jump instructions
        final_instruction.append(RST)
    elif i >= 100 or i <= 81: #Range for jump instructions
        final_instruction.append(RST | CI)
    else:
        final_instruction += [CI, CI, RST | CI]
    final_instructions.append(final_instruction)

jump_m = final_instructions[82] #Address of JMPM in instruction set list
jump_immediate = final_instructions[83] #Address of JMI in instruction set list

rom = [0]*65536
#The ROM is addressed as follows:
#SF|ZF|PF|CF|I7|I6|I5|I4|I3|I2|I1|I0|M3|M2|M1|M0
#15 14 13 12 11 10 9  8  7  6  5  4  3  2  1  0

for flags_int in range(16):
    #converts all number from 0 to 16 to their 4-bit binary equivilants
    #eg. 4 = ['0','1','0','0'] and 9 = 1001
    flags = list(bin(flags_int)[2:].zfill(4))
    #Converts the list of strings to a list of booleans
    for i in range(4):
        flags[i] = int(flags[i])
    #Fills the rom with the operations for each jump instruction
    for i, instruction in enumerate(final_instructions):
        for j, operation in enumerate(instruction):
            address = (flags_int << 12) | (i << 4) | j
            rom[address] = operation

for flags_int in range(16):
    #converts all number from 0 to 16 to their 4-bit binary equivilants
    #eg. 4 = ['0','1','0','0'] and 9 = 1001
    flags = list(bin(flags_int)[2:].zfill(4))
    #Converts the list of strings to a list of booleans
    for i in range(4):
        flags[i] = int(flags[i])
    #Enumerates through each conditional jump instruction and only fills the
    #ROM with jump instructions if the correct flag conditions are met
    for i, instruction in enumerate(final_instructions[84:100]):
        i += 84
        for which_jump, jump_instruction in enumerate((jump_m, jump_immediate)):
            for j, operation in enumerate(jump_instruction):
                address = (flags_int << 12) | (i << 4) | j
                #Jump if negative M
                if i == 84 and flags[0] and not which_jump:
                    rom[address] = jump_m[j]
                #Jump if negative immediate
                if i == 85 and flags[0] and which_jump:
                    rom[address] = jump_immediate[j]
                #Jump if positive M
                if i == 86 and not flags[0] and not which_jump:
                    rom[address] = jump_m[j]
                #Jump if positive immediate
                if i == 87 and not flags[0] and which_jump:
                    rom[address] = jump_immediate[j]
                #Jump if zero M
                if i == 88 and flags[1] and not which_jump:
                    rom[address] = jump_m[j]
                #Jump if zero immediate
                if i == 89 and flags[1] and which_jump:
                    rom[address] = jump_immediate[j]
                #Jump if not zero M
                if i == 90 and not flags[1] and not which_jump:
                    rom[address] = jump_m[j]
                #Jump if not zero immediate
                if i == 91 and not flags[1] and which_jump:
                    rom[address] = jump_immediate[j]
                #Jump if even M
                if i == 92 and flags[2] and not which_jump:
                    rom[address] = jump_m[j]
                #Jump if even immediate
                if i == 93 and flags[2] and which_jump:
                    rom[address] = jump_immediate[j]
                #Jump if odd M
                if i == 94 and not flags[2] and not which_jump:
                    rom[address] = jump_m[j]
                #Jump if odd immediate
                if i == 95 and not flags[2] and which_jump:
                    rom[address] = jump_immediate[j]
                #Jump if carry M
                if i == 96 and flags[3] and not which_jump:
                    rom[address] = jump_m[j]
                #Jump if carry immediate
                if i == 97 and flags[3] and which_jump:
                    rom[address] = jump_immediate[j]
                #Jump if no carry M
                if i == 98 and not flags[3] and not which_jump:
                    rom[address] = jump_m[j]
                #Jump if no carry immediate
                if i == 99 and not flags[3] and which_jump:
                    rom[address] = jump_immediate[j]

file_byte_array = []

for value in rom:
    value = bin(value)[2:].zfill(32)
    file_byte_array.append(int(value[24:32], 2))
    file_byte_array.append(int(value[16:24], 2))
    file_byte_array.append(int(value[8:16], 2))
    file_byte_array.append(int(value[:8], 2))

with open("instruction_rom.bin", 'wb') as binary_file:
    binary_file.write(bytearray(file_byte_array))

with open("instruction_rom.bin", 'rb') as binary_file:
    rom = binary_file.read()

print("ROM successfully written")
end = input("Press <ENTER> to quit")
quit()
