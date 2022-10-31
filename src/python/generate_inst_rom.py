import sys

def generate_rom(instruction_rom_bin):
    #All of the control lines for the CPU
    (IC0, IC1, IC2, IC3,
    OC0, OC1, OC2, OC3,
    AC0, AC1, AC2, AC3,
    CI, ADRI, SI, SD,
    MCA, MSA,
    ZFO, SFO,
    RI, RO, RST, OUT, HLT) = (2**i for i in range(25))

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
    LNEG = AC3
    ANEG = AC3 | AC0

    instructions = [
        [], #NOP (no operation) does nothing
        ################### ARITHMETIC INSTRUCTIONS ############################
        #UNCONDITIONAL ARITHMETIC OPERATIONS
        # Addition (1-5)
        [AO | ATI, ADD | AI], #ADDA (add A) adds value in accumulator to accumulator
        [BO | ATI, ADD | AI], #ADDB (add B) adds value in B to accumulator
        [HO | ATI, ADD | AI], #ADDH (add H) adds value in H to accumulator
        [LO | ATI, ADD | AI], #ADDL (add L) adds value in L to accumulator
        [CI | ADRI | RO | ATI, ADD | AI], #ADDI (add immediate) adds value in adjacent btye to accumulator
        # Subtraction (6-9)
        [BO | ATI, SUB | AI], #SUBB (subtract B) subtracts value in B from accumulator
        [HO | ATI, SUB | AI], #SUBH (subtract H) subtracts value in H from accumulator
        [LO | ATI, SUB | AI], #SUBL (subtract L) subtracts value in L from accumulator
        [CI | ADRI | RO | ATI, SUB | AI], #SUBI (subtract immediate) subtracts the value in adjacent byte from accumulator
        # Binary AND (10-13)
        [BO | ATI, AND | AI], #ANDB (and B) ands value in B with accumulator
        [HO | ATI, AND | AI], #ANDH (and H) ands value in H with accumulator
        [LO | ATI, AND | AI], #ANDL (and L) ands value in L with accumulator
        [CI | ADRI | RO | ATI, AND | AI], #ANDI (and immediate) ands value in adjacent byte with accumulator
        # Binary OR (11-14)
        [BO | ATI, OR | AI], #ORB (or B) ors value in B with accumulator
        [HO | ATI, OR | AI], #ORH (or H) ors value in H with accumulator
        [LO | ATI, OR | AI], #ORL (or L) ors value in L with accumulator
        [CI | ADRI | RO | ATI, OR |AI], #ORI (or immediate) ors value in adjacent byte with accumulator
        # Binary XOR (15-18)
        [BO | ATI, XOR | AI], #XORB (exclusive or B) xors value in B with accumulator
        [HO | ATI, XOR | AI], #XORH (exclusive or H) xors value in H with accumulator
        [LO | ATI, XOR | AI], #XORL (exclusive or L) xors value in L with accumulator
        [CI | ADRI | RO | ATI, XOR |AI], #XORI (exclusive or immediate) xors value in adjacent byte with accumulator
        # Other (19-22)
        [INC | AI], #INC (increment) increments accumulator
        [DEC | AI], #DEC (decrement) decrements accumulator
        [LNEG | AI], #LNEG (logical negate) logically negates accumulator
        [ANEG | AI], #ANEG (arithmetic negate) arithmetically negates the accumulator
        #################### REGISTER INSTRUCTIONS #####################
        #MOVE INSTRUCTIONS
        # Move to A (23-26)
        [CI | ADRI | RO | AI], #MOVAI (move A immediate) loads A with adjacent byte
        [BO | AI], #MOVAB (move A B) moves value in B to A
        [HO | AI], #MOVAH (move A H) moves value in H to A
        [LO | AI], #MOVAL (move A L) moves value in L to A
        # Move to B (27-30)
        [CI | ADRI | RO | BI], #MOVBI (move B immediate) loads B with adjacent byte
        [AO | BI], #MOVBA (move B A) moves value in A to B
        [HO | BI], #MOVBH (move B H) moves value in H to B
        [LO | BI], #MOVBL (move B L) moves value in L to B
        # Move to H (31-34)
        [CI | ADRI | RO | HI], #MOVHI (move H immediate) loads H with adjacent byte
        [AO | HI], #MOVHA (move H A) moves value in A to H
        [BO | HI], #MOVHB (move H B) moves value in B to H
        [LO | HI], #MOVHL (move H L) moves value in L to H
        # Move to L (35-38)
        [CI | ADRI | RO | LI], #MOVLI (move L immediate) loads L with adjacent byte
        [AO | LI], #MOVLA (move L A) moves value in A to L
        [BO | LI], #MOVLB (move L B) moves value in B to L
        [HO | LI], #MOVLH (move L H) moves value in H to L
        ########################### JUMP INSTRUCTIONS ################################
        #UNCONDITIONAL JUMPS (39)
        [CI | ADRI | RO | ATI, CI | ADRI | RO | CLI, ATO | CHI], #JMI (jump immediate) jumps to value in adjacent bytes
        # CONDITIONAL JUMPS (40-45)
        #The reason that these are left blank is because the data for them is only written
        #into specific addresses where both the opcode AND the flags necessary for that
        #instruction to execute are correct. All other instructions are written into all
        #6 locations regardless of flag status.
        [], #JNI (jump if negative immediate) jumps to immediate if negative
        [], #JPI (jump if positive immediate) jumps to immediate if positive
        [], #JZI (jump if zero immediate) jumps to immediate if zero
        [], #JNZI (jump if not zero immediate) jumps to immediate if not zero
        [], #JCI (jump if carry immediate) jumps to immediate if carry bit is set
        [], #JNCI (jump if no carry immediate) jumps to immediate if carry flag not set
        ##################### STACK INSTRUCTIONS #############################
        # PUSH (46-53)
        [CI | ADRI | RO | ATI | SD, MSA | ATO | RI], #PUSHI (push immediate) pushes the immediate onto the stack
        [SD, MSA, AO | RI], #PUSHA (push A) pushes register A onto stack
        [SD, MSA, BO | RI], #PUSHB (push B) pushes register B onto stack
        [SD, MSA, HO | RI], #PUSHH (push H) pushes register H onto stack
        [SD, MSA, LO | RI], #PUSHL (push L) pushes register L onto stack
        [SD, MSA, FO | RI], #PUSHS (push status) pushes status byte onto stack
        [SD, MSA, BHO | RI, SD, MSA, BLO | RI], #PUSHBP (push base pointer) pushes the base pointer onto the stack
        [SD, MSA, CHO | RI, SD, MSA, CLO | RI], #PUSHC (push counter) pushes the program counter onto the stack
        # POP (54-61)
        [MSA, SI | RO | BI, MCA, CI | ADRI | RO | ATI, CI | ADRI | RO | ALI, ATO | AHI, BO | RI], #POP (pop) pops the stack into the address of the adjacent two bytes NOTE : alters B register
        [MSA, SI | RO | AI], #POPA (pop A) pops the stack into A
        [MSA, SI | RO | BI], #POPB (pop B) pops the stack into B
        [MSA, SI | RO | HI], #POPH (pop H) pops the stack into H
        [MSA, SI | RO | LI], #POPL (pop L) pops the stack into L
        [MSA, SI | RO | FI], #POPS (pop status) pops the stack into the flags register
        [MSA, SI | RO | BLI, MSA, SI | RO | BHI], #POPBP (pop base pointer) pops the base pointer from the stack
        [MSA, SI | RO | CLI, MSA, SI | RO | CHI], #POPC (pop counter) pops the program counter from the stack
        # STACK REGISTER MOVE (62-63)
        [SHO | BHI, SLO | BLI], #MOVBPSP (move base pointer stack pointer) moves the value in the stack pointer to the base pointer
        [BHO | SHI, BLO | SLI], #MOVSPBP (move stack pointer base pointer) moves the value in the base pointer to the stack pointer
        #################### OTHER INSTRUCTIONS ###############################
        # FLAGS (64-65)
        [ZFO | AI], #ZFO (zero flag out) move the zero flag to the accumulator to be used in compare operations
        [SFO | AI], #SFO (sign flag out) move the sign flag to the accumulator to be used in compare operations
        # ETC (66-67)
        [AO | OUT], #OUT (out) outputs the value in the accumulator
        [HLT] #HLT (halt) stops program execution
    ]

    final_instructions = []

    for i, instruction in enumerate(instructions):
        #Each instruction starts with these two microinstructions
        final_instruction = [MCA, RO | II]
        final_instruction += instruction
        if i == 39: #Doesn't increment counter on jump instructions
            final_instruction.append(RST)
        elif i >= 46 or i <= 38: #Range for jump instructions
            final_instruction.append(RST | CI)
        else:
            final_instruction += [CI, CI, RST | CI]
        final_instructions.append(final_instruction)

    jump_immediate = final_instructions[39] #Address of JMI in instruction set list

    rom = [0]*65536
    #The ROM is addressed as follows:
    #SF|ZF|CF|I7|I6|I5|I4|I3|I2|I1|I0|M3|M2|M1|M0
    #14 13 12 11 10 9  8  7  6  5  4  3  2  1  0

    for flags_int in range(8):
        #converts all numbers from 0 to 7 to their 3-bit binary equivilants
        #eg. 4 = ['1','0','0']
        flags = list(bin(flags_int)[2:].zfill(3))
        #Converts the list of strings to a list of booleans
        for i in range(3):
            flags[i] = int(flags[i])
        #Fills the rom with the operations for each jump instruction
        for i, instruction in enumerate(final_instructions): # TODO: check this
            for j, operation in enumerate(instruction):
                address = (flags_int << 12) | (i << 4) | j
                rom[address] = operation

    for flags_int in range(8):
        #converts all numbers from 0 to 7 to their 3-bit binary equivilants
        #eg. 4 = ['0','1','0','0']
        flags = list(bin(flags_int)[2:].zfill(4))
        #Converts the list of strings to a list of booleans
        for i in range(3):
            flags[i] = int(flags[i])
        #Enumerates through each conditional jump instruction and only fills the
        #ROM with jump instructions if the correct flag conditions are met
        for i, instruction in enumerate(final_instructions[40:46]):
            i += 40
            for which_jump, jump_instruction in enumerate(jump_immediate):
                for j, operation in enumerate(jump_instruction):
                    address = (flags_int << 12) | (i << 4) | j # TODO: check this
                    #Jump if negative immediate
                    if i == 40 and flags[0] and which_jump:
                        rom[address] = jump_immediate[j]
                    #Jump if positive immediate
                    if i == 41 and not flags[0] and which_jump:
                        rom[address] = jump_immediate[j]
                    #Jump if zero immediate
                    if i == 42 and flags[1] and which_jump:
                        rom[address] = jump_immediate[j]
                    #Jump if not zero immediate
                    if i == 43 and not flags[1] and which_jump:
                        rom[address] = jump_immediate[j]
                    #Jump if carry immediate
                    if i == 44 and flags[2] and which_jump:
                        rom[address] = jump_immediate[j]
                    #Jump if no carry immediate
                    if i == 45 and not flags[2] and which_jump:
                        rom[address] = jump_immediate[j]

    file_byte_array = []

    for value in rom:
        value = bin(value)[2:].zfill(32)
        file_byte_array.append(int(value[24:32], 2))
        file_byte_array.append(int(value[16:24], 2))
        file_byte_array.append(int(value[8:16], 2))
        file_byte_array.append(int(value[:8], 2))

    with open(instruction_rom_bin, 'wb') as binary_file:
        binary_file.write(bytearray(file_byte_array))

    print("ROM successfully written")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("ERROR: expected 1 argument")
    else:
        generate_rom(sys.argv[1])