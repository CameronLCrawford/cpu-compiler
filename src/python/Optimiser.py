import sys

def optimise(assembly_file):
    registers = ("A, B, H, L")
    code = []
    with open(assembly_file, 'r') as program_file:
        code = program_file.read().splitlines()
    for i, instruction in enumerate(code):
        code[i] = instruction.split()
    optimised_code = []
    pushed_register = None
    pushed_integer = None
    for instruction in code:
        opcode = instruction[0].upper()
        if len(instruction) > 1:
            operand1 = instruction[1].upper()
        if len(instruction) > 2:
            operand2 = instruction[2].upper()
        #Checks for a push x; pop x and eliminates both lines
        #Also checks for push x; pop y and adds mov y x
        #Also checks for push integer; pop y and adds ldr y integer
        if opcode == "PUSH":
            if pushed_register:
                optimised_code.append("push {}".format(pushed_register))
            if pushed_integer != None:
                optimised_code.append("push {}".format(pushed_integer))
            if operand1 in registers:
                pushed_register = operand1
                pushed_integer = None
            else:
                pushed_register = None
                try:
                    pushed_integer = int(operand1)
                    continue
                except ValueError:
                    pushed_integer = None
                optimised_code.append(" ".join(instruction))
        elif opcode == "POP":
            if pushed_register:
                #push x; pop x
                if pushed_register == operand1:
                    pass
                #push x; pop y
                elif operand1 in registers:
                    optimised_code.append("mov {} {}".format(operand1, pushed_register))
            #push integer; pop y
            elif pushed_integer != None:
                if operand1 in registers:
                    optimised_code.append("ldr {} {}".format(operand1, pushed_integer))
                else:
                    optimised_code.append("push {}".format(pushed_integer))
            else:
                optimised_code.append(" ".join(instruction))
            pushed_register = None
            pushed_integer = None
        else:
            #Checks for arithmetic operations with no effect (add 0, for example)
            if opcode in ("ADD", "SUB"):
                if operand1 == "0":
                    continue
            if opcode in ("AP", "SP"):
                if operand2 == "0":
                    continue
            if pushed_register:
                optimised_code.append("push {}".format(pushed_register))
            if pushed_integer != None:
                optimised_code.append("push {}".format(pushed_integer))
            pushed_register = None
            pushed_integer = None
            optimised_code.append(" ".join(instruction))
    with open(assembly_file, "w") as program_file:
        for instruction in optimised_code:
            program_file.write("".join(instruction))
            program_file.write('\n')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("ERROR: expected 1 argument")
    else:
        compile(sys.argv[1])
