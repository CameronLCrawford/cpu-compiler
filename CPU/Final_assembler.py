program_rom = [0]*65536

opcodes = (
    "ADD", "SUB", "AND", "OR", "XOR", "INC", "DEC", "NEG", "UNEG", "ADDC", "SUBC", "INCC", "DECC",
    "MOV", "LDR", "STA", "JMP", "JN", "JP", "JZ", "JNZ", "JE", "JO", "JC", "JNC",
    "PUSH", "POP", "AP", "SP", "MPHBP", "ZFO", "SFO", "OUT", "HLT"
)

#Defines all assembly instructions that the computer knows
#so the assembly can easily compile to machine code
instruction_names = dict(zip(
["ADD", "ADDA", "ADDB", "ADDH", "ADDL", "ADDM", "ADDI", #ADDITION
"SUB", "SUBA", "SUBB", "SUBH", "SUBL", "SUBM", "SUBI", #SUBTRACTION
"AND", "ANDA", "ANDB", "ANDH", "ANDL", "ANDM", "ANDI", #BINARY AND
"OR", "ORA", "ORB", "ORH", "ORL", "ORM", "ORI", #BINARY OR
"XOR", "XORA", "XORB", "XORH", "XORL", "XORM", "XORI", #BINARY XOR
"INC", "DEC", "NEG", "UNEG", #OTHER ALU OPERATIONS
"ADDC", "ADDCA", "ADDCB", "ADDCH", "ADDCL", "ADDCM", "ADDCI", #ADDITION (CARRY CONDITIONAL)
"SUBC", "SUBCA", "SUBCB", "SUBCH", "SUBCL", "SUBCM", "SUBCI", #SUBTRACTION (CARRY CONDITIONAL)
"INCC", "DECC", #INCREMENTATION / DECREMENTATION (CARRY CONDITIONAL)
"MOVAB", "MOVAH", "MOVAL", #MOVE TO A
"MOVBA", "MOVBH", "MOVBL", #MOVE TO B
"MOVHA", "MOVHB", "MOVHL", #MOVE TO H
"MOVLA", "MOVLB", "MOVLH", #MOVE TO L
"LDA", "LDAI", "LDAM", "LDB", "LDBI", "LDBM", #LOAD A / B
"LDH", "LDHI", "LDHM", "LDL", "LDLI", "LDLM", #LOAD H / L
"STAI", "STAM", #STORE A
"JMPM", "JMPI", #JUMP (UNCONDITIONAL)
"JNM", "JNI", "JPM", "JPI", "JZM", "JZI", "JNZM", "JNZI", #JUMP CONDITIONAL
"JEM", "JEI", "JOM", "JOI", "JCM", "JCI", "JNCM", "JNCI", #JUMP CONDITIONAL
"PUSH", "PUSHI", "PUSHA", "PUSHB", "PUSHH", "PUSHL", "PUSHS", "PUSHBP", "PUSHC", #PUSH TO STACK
"POP", "POPA", "POPB", "POPH", "POPL", "POPS", "POPBP", "POPC", #POP FROM STACK
"LDSPH", "LDSPL", "LDSP", "LDSPHM", "LDSPLM", "LDSPHL", #LOAD STACK POINTER
"LDBPH", "LDBPL", "LDBP", "LDBPHM", "LDBPLM", "LDBPHL", #LOAD BASE POINTER
"MOVBPSP", "MOVSPBP", "MARHL", "MHLAR", #MOVE STACK / BASE POINTER
"MPHSP", "MPHBP", #16 BIT MOVE
"APHI", "APSPH", "APBPH", "APSPI", "APBPI", #16 BIT ADDITION
"SPHI", "SPSPH", "SPBPH", "SPSPI", "SPBPI", #16 BIT SUBTRACTION
"ZFO", "SFO", #FLAG OUT OPERATIONS FOR USE IN COMPARISONS
"OUT", "HLT"], range(1, 149)))

symbol_table = {} #Stores all of the symbols used and their memory locations
instructions = {} #Stores all instructions and their memory locations

double_immediate_instructions = ("STA", "JMP", "JN", "JP", "JZ", "JNZ", "JE", "JO", "JC", "JNC")
arithmetic_instructions = ("ADD", "SUB", "AND", "OR", "XOR", "ADDC", "SUBC")
registers = ("A", "B", "H", "L", "M")
jump_instructions = ("JMP", "JN", "JP", "JZ", "JNZ", "JE", "JO", "JC", "JNC")

def assemble():
    with open("program.txt", 'r') as program_file:
        code = program_file.read().splitlines()
    for i, instruction in enumerate(code):
        code[i] = instruction.split()

    #Populates symbol table and instructions dictionary with memory locations
    instruction_count = 32768
    data_count = 0
    for i, instruction in enumerate(code):
        if len(instruction) == 0: #Blank line
            continue
        if instruction[0].upper() not in opcodes: #Data, Label or comment
            if len(instruction) == 1 and instruction[0][-1] == ':': #Label instruction
                symbol_table[('label',instruction[0][:-1].upper())] = instruction_count
                continue
            if len(instruction) == 1:
                print("Error on line {}. Unidentified instruction".format(i+1))
                end = input("Press <ENTER> to quit")
                quit()
            if instruction[0][:2] == "//": #Comment
                continue
            if instruction[1].upper() in ("BYTE", "DBYTE") and len(instruction) == 3: #Data instruction
                if instruction[1].upper() == "BYTE": #Single byte declaration
                    try:
                        program_rom[data_count] = int(instruction[2])
                        symbol_table[('byte', instruction[0].upper())] = data_count
                        data_count += 1
                        continue
                    except ValueError:
                        print("Error on line {}. BYTE not assigned integer".format(i+1))
                        end = input("Press <ENTER> to quit")
                        quit()
                elif instruction[1].upper() == "DBYTE": #Double byte declaration
                    try:
                        full_value = bin(int(instruction[2]))[2:].zfill(16)
                        high_byte = int(full_value[:8], 2)
                        low_byte = int(full_value[8:], 2)
                        program_rom[data_count] = high_byte
                        program_rom[data_count + 1] = low_byte
                        symbol_table[('dbyte', instruction[0].upper())] = data_count
                        data_count += 2
                        continue
                    except ValueError:
                        print("Error on line {}. DBYTE not assigned integer".format(i+1))
        else:
            instruction_name = instruction[0].upper()
            #Arithmetic instruction (BYTE immediate, immediate, register), Double immediate (Jump, STA)
            if len(instruction) == 2:
                operand1 = instruction[1].upper()
                #Arithmetic instructions with data
                if instruction_name in arithmetic_instructions and operand1 != 'M':
                    try:
                        int(operand1) #Checks if the immediate is a declared BYTE or an integer
                        instructions[(instruction_count, i + 1)] = instruction
                        instruction_count += 2 #One for instruction and one for immediate
                    except ValueError: #The operand is a BYTE so the two immediate bytes are the address of that byte
                        instructions[(instruction_count, i + 1)] = instruction
                        instruction_count += 3 #One for instruction and two for the address of BYTE
                    continue
                #Double immediate instructions with data
                if instruction_name in double_immediate_instructions and operand1 != 'M':
                    instructions[(instruction_count, i + 1)] = instruction
                    instruction_count += 3 #One for instruction and two for immediate
                    continue
                if instruction_name in ("PUSH", "POP") and operand1 not in ("A", "B", "H", "L", "BP", "C"):
                    try: #Applies to PUSH, PUSHI, and POP
                        int(operand1) #Checks for immediate integer
                        instructions[(instruction_count, i + 1)] = instruction
                        instruction_count += 2 #Only applies to PUSHI
                    except ValueError: #Either PUSH or POP
                        instructions[(instruction_count, i + 1)] = instruction
                        instruction_count += 3 #One for instruction and 2 for address of BYTE
                    continue
            #LDR instruction or 16 bit register arithmetic instruction
            if len(instruction) == 3:
                operand1 = instruction[1].upper()
                operand2 = instruction[2].upper()
                if instruction_name == "LDR" and operand1 in ("A", "B", "H", "L", "SP", "BP", "SPH" "SPL", "BPH", "BPL") and operand2 != 'M':
                    try:
                        int(operand2) #Checks if the immediate is a declared BYTE or an integer
                        instructions[(instruction_count, i + 1)] = instruction
                        instruction_count += 2
                    except ValueError: #Immediate is declared BYTE
                        instructions[(instruction_count, i + 1)] = instruction
                        instruction_count += 3
                    continue
                if instruction_name in ("AP", "SP"):
                    try:
                        int(operand2) #Checks if immediate is integer or not
                        instructions[(instruction_count, i + 1)] = instruction
                        instruction_count += 3 #Immediate is integer (16 bit)
                    except ValueError: #Single byte register instruction
                        instructions[(instruction_count, i + 1)] = instruction
                        instruction_count += 1
                    continue
            instructions[(instruction_count, i + 1)] = instruction
            instruction_count += 1 #Default for remaining one-byte instructions (includes M instructions)
            
    #Fills ROM with machine code
    #This substitutes in symbols where necessary too
    for i, instruction in enumerate(instructions.values()):
        rom_address = list(instructions.keys())[i][0]
        code_line = list(instructions.keys())[i][1]
        opcode = instruction[0].upper()
        if len(instruction) > 1:
            operand1 = instruction[1].upper()
        if len(instruction) > 2:
            operand2 = instruction[2].upper()
        ##################################################
        if opcode in arithmetic_instructions:
            if operand1 in registers:
                program_rom[rom_address] = instruction_names[opcode + operand1]
            elif ('byte', operand1) in symbol_table.keys():
                full_address = bin(int(symbol_table['byte', operand1]))[2:].zfill(16)
                high_byte = int(full_address[:8], 2)
                low_byte = int(full_address[8:], 2)
                program_rom[rom_address] = instruction_names[opcode]
                program_rom[rom_address + 1] = high_byte
                program_rom[rom_address + 2] = low_byte
            else:
                try:
                    program_rom[rom_address] = instruction_names[opcode + "I"]
                    program_rom[rom_address + 1] = int(operand1)
                except ValueError:
                    print("Error on line {}. Immediate {} without numeric value".format(code_line, opcode))
                    end = input("Press <ENTER> to quit")
                    quit()
        if opcode in ("AP", "SP"):
            if operand1 in ("H", "SP", "BP"): #Valid AP / SP register pairs
                if operand1 in ("SP", "BP") and operand2 == "H":
                    program_rom[rom_address] = instruction_names[opcode + operand1 + "H"]
                else:
                    try:
                        full_value = bin(int(operand2))[2:].zfill(16)
                        high_byte = int(full_value[:8], 2)
                        low_byte = int(full_value[8:], 2)
                        program_rom[rom_address] = instruction_names[opcode + operand1 + "I"]
                        program_rom[rom_address + 1] = low_byte
                        program_rom[rom_address + 2] = high_byte
                    except ValueError: #The immediate is not an int
                        print("Error on line {}. Invalid {} immediate value".format(code_line, opcode))
                        end = input("Press <ENTER> to quit")
                        quit()
            else:
                print("Error on line {}. {} without valid register pair specified".format(code_line, opcode))
                end = input("Press <ENTER> to quit")
                quit()
        if opcode in ("INC", "DEC", "NEG", "UNEG", "INCC", "DECC"):
            program_rom[rom_address] = instruction_names[opcode]
        if opcode == "MOV":
            try:
                program_rom[rom_address] = instruction_names["MOV" + operand1 + operand2]
            except KeyError:
                if operand1 == "HP" and operand2 in ("SP", "BP"):
                    program_rom[rom_address] = instruction_names["MPHL" + operand2]
                elif operand1 == "AR" and operand2 == "HL" or operand1 == "HL" and operand2 == "AR":
                    program_rom[rom_address] = instruction_names["M{}{}".format(operand1, operand2)]
                else:
                    print("Error on line {}. Invalid MOV instruction".format(code_line))
                    end = input("Press <ENTER> to quit")
                    quit()
        if opcode == "LDR":
            if operand1 not in ("A", "B", "H", "L", "SP", "BP", "SPH" "SPL", "BPH", "BPL"):
                print("Error on line {}. Unknown LDR destination".format(code_line))
                end = input("Press <ENTER> to quit")
                quit()
            elif ('byte', operand2) in symbol_table.keys():
                full_address = bin(int(symbol_table['byte', operand2]))[2:].zfill(16)
                high_byte = int(full_address[:8], 2)
                low_byte = int(full_address[8:], 2)
                program_rom[rom_address] = instruction_names["LD" + operand1]
                program_rom[rom_address + 1] = high_byte
                program_rom[rom_address + 2] = low_byte
            elif ('dbyte', operand2) in symbol_table.keys() and operand1 in ("SP", "BP"):
                program_rom[rom_address] = instruction_names["LD" + operand1]
                program_rom[rom_address + 1] = program_rom[symbol_table[('dbyte', operand2)]]
                program_rom[rom_address + 2] = program_rom[symbol_table[('dbyte', operand2)] + 1]
            elif operand2 == 'M':
                program_rom[rom_address] = instruction_names["LD" + operand1 + "M"]
            else:
                try:
                    program_rom[rom_address] = instruction_names["LD" + operand1 + "I"]
                    program_rom[rom_address + 1] = int(operand2)
                except ValueError:
                    print("Error on line {}. Immediate LD{} without numeric value".format(code_line, operand1))
                    end = input("Press <ENTER> to quit")
                    quit()
                except KeyError: #Instruction is LDSPHL or LDBPHL
                    if operand2 == "HL":
                        program_rom[rom_address] = instruction_names["LD" + operand1 + "HL"]
                    else:
                        print("Error on line {}. LD{} without valid source".format(code_line, operand1))
                        end = input("Press <ENTER> to quit")
                        quit()
        if opcode == "STA":
            if operand1 == "M":
                program_rom[rom_address] = instruction_names["STAM"]
            elif ('dbyte', operand1) in symbol_table.keys():
                program_rom[rom_address] = instruction_names["STAI"]
                program_rom[rom_address + 1] = program_rom[symbol_table[('dbyte', operand1)]]
                program_rom[rom_address + 2] = program_rom[symbol_table[('dbyte', operand1)] + 1]
            elif ('byte', operand1) in symbol_table.keys():
                full_address = bin(int(symbol_table['byte', operand1]))[2:].zfill(16)
                high_byte = int(full_address[:8], 2)
                low_byte = int(full_address[8:], 2)
                program_rom[rom_address] = instruction_names["STAI"]
                program_rom[rom_address + 1] = high_byte
                program_rom[rom_address + 2] = low_byte
            else:
                try:
                    program_rom[rom_address] = instruction_names["STAI"]
                    program_rom[rom_address + 1] = int(operand1)
                    program_rom[rom_address + 2] = int(operand2)
                except ValueError:
                    print("Error on line {}. STA immediate without numeric value".format(code_line))
                    end = input("Press <ENTER> to quit")
                    quit()
        if opcode in jump_instructions:
            if operand1 == "M":
                program_rom[rom_address] = instruction_names[opcode + "M"]
            elif ('label', operand1) in symbol_table.keys():
                full_address = bin(int(symbol_table['label', operand1]))[2:].zfill(16)
                high_byte = int(full_address[:8], 2)
                low_byte = int(full_address[8:], 2)
                program_rom[rom_address] = instruction_names[opcode + "I"]
                program_rom[rom_address + 1] = high_byte
                program_rom[rom_address + 2] = low_byte
            else:
                try:
                    program_rom[rom_address] = instruction_names[opcode + "I"]
                    program_rom[rom_address + 1] = int(operand1)
                    program_rom[rom_address + 2] = int(operand2)
                except ValueError:
                    print("Error on line {}. JMP immediate without numeric value".format(code_line))
                    end = input("Press <ENTER> to quit")
                    quit()
        if opcode == "PUSH":
            if operand1 in ("A", "B", "H", "L", "S", "BP", "C"):
                program_rom[rom_address] = instruction_names["PUSH" + operand1]
            elif ('byte', operand1) in symbol_table.keys():
                full_address = bin(int(symbol_table['byte', operand1]))[2:].zfill(16)
                high_byte = int(full_address[:8], 2)
                low_byte = int(full_address[8:], 2)
                program_rom[rom_address] = instruction_names["PUSH"]
                program_rom[rom_address + 1] = high_byte
                program_rom[rom_address + 2] = low_byte
            else:
                try:
                    program_rom[rom_address] = instruction_names["PUSHI"]
                    program_rom[rom_address + 1] = int(operand1)
                except ValueError:
                    print("Error on line {}. PUSH without valid operand".format(code_line))
                    end = input("Press <ENTER> to quit")
                    quit()
        if opcode == "POP":
            if operand1 in ("A", "B", "H", "L", "S", "BP", "C"):
                program_rom[rom_address] = instruction_names["POP" + operand1]
            elif ('byte', operand1) in symbol_table.keys():
                full_address = bin(int(symbol_table['byte', operand1]))[2:].zfill(16)
                high_byte = int(full_address[:8], 2)
                low_byte = int(full_address[8:], 2)
                program_rom[rom_address] = instruction_names["POP"]
                program_rom[rom_address + 1] = high_byte
                program_rom[rom_address + 2] = low_byte
            else:
                print("Error on line {}. POP without valid operand".format(code_line))
                end = input("Press <ENTER> to quit")
                quit()
        if opcode in ("OUT", "HLT", "ZFO", "SFO", "MPHSP", "MPHBP"):
            program_rom[rom_address] = instruction_names[opcode]

    with open("program_rom.bin", 'wb') as rom:
        rom.write(bytearray(program_rom))

    print("Assembly complete!")
    print("Assembled Machine Code:\n{}\n".format(program_rom[32768:instruction_count]))
    end = input("Press <ENTER> to quit")
    quit()

if __name__ == "__main__":
    assemble()