import xml.etree.ElementTree as ET

def generate_assembly(abstract_syntax_tree, symbol_table):

    root = abstract_syntax_tree
    generated_assembly = []
    #The symbol table for the current function
    function_table = None
    #This keeps a track of the name used for the compiler-generated
    #labels created when using conditionals. For example: the first
    #label will be ".L1" then it will be ".Ln" through to ".L0" as 
    #the final node
    current_label = 0
    initial_statement = list(root)[0]
    initial_function = None

    def compile_initial(initial_node):
        nonlocal generated_assembly
        nonlocal initial_function
        generated_assembly.append("push c")
        #Adds 10 to the pushed program counter so that when it is popped the program execution
        #resumes from the next sequential instruction
        generated_assembly += ("pop l", "pop h", "ap h 10", "push h", "push l")
        initial_function = initial_node.get("value")
        generated_assembly.append("jmp @{}".format(initial_function))

    def compile_function_call(function_node):
        nonlocal generated_assembly
        #Handles all arguments in reverse order so they are accessed with relation
        #to the base pointer correctly
        for argument in reversed(list(function_node)):
            compile_expression(argument)
        generated_assembly.append("push c")
        #Adds 10 to the pushed program counter so that when it is popped the program execution
        #resumes from the next sequential instruction
        generated_assembly += ("pop l", "pop h", "ap h 10", "push h", "push l")
        generated_assembly.append("jmp @{}".format(function_node.get("value")))
        #When a function returns, the return value is stored in the B register so it
        #is moved to the accumulator
        generated_assembly.append("mov a b")

    def compile_function(function_node):
        nonlocal generated_assembly
        nonlocal function_table
        function_name = function_node.get("value")
        #Adds the label for that function so it is identifiable and can be jumped to
        generated_assembly.append("@{}:".format(function_name))
        function_table = symbol_table[1][symbol_table[0].index(function_name)]
        generated_assembly += ("push bp", "mov bp sp")
        #Counts the number of local variables and makes space for them on the stack
        #by subtracting that number of bytes from the stack pointer
        local_variable_count = 0
        for local_variable in function_table:
            if local_variable[1] == "local":
                local_variable_count += 1
        generated_assembly.append("sp sp {}".format(local_variable_count))
        for function_element in function_node:
            if function_element.tag == "functionBody":
                compile_statements(function_element)
        if function_name == initial_function:
            generated_assembly.append("hlt")

    def compile_expression(expression_node):
        nonlocal generated_assembly
        current_element = "term1"
        next_element = "operator"
        operator = None
        for expression_element in list(expression_node):
            if current_element in ("term1", "term2"):
                if expression_element.tag == "expression":
                    compile_expression(expression_element)
                elif expression_element.tag == "integer_constant":
                    integer_constant = expression_element.get("value")
                    generated_assembly.append("push {}".format(integer_constant))
                elif expression_element.tag == "functionCall":
                    compile_function_call(expression_element)
                    generated_assembly.append("push a")
                elif expression_element.tag == "localVariable":
                    #local_count refers to the offset from the base pointer the local variable
                    #is. The same applies to argument count and this is 4 as the stack frame for
                    #a function is arranged in the way that between the base pointer and the arguments
                    #for that function there is the program counter and the rest of the base pointer.
                    local_count = 1
                    argument_count = 4
                    for variable in function_table:
                        if variable[0] == expression_element.get("value"):
                            if variable[1] == "local":
                                #Loads the accumulator with the local variable and pushes the accumulator
                                generated_assembly += ("mphbp", "mov b a", "sp h {}".format(local_count), "mov a b", "mov ar hl", "push a")
                            elif variable[1] == "argument":
                                #Loads the accumulator with the argument variable and pushes the accumulator
                                generated_assembly += ("mphbp", "mov b a", "ap h {}".format(argument_count), "mov a b", "mov ar hl", "push a")
                        else:
                            #If the current variable is not the one looked for then it must be one
                            #further away from the base pointer so increment the offset
                            if variable[1] == "local":
                                local_count += 1
                            elif variable[1] == "argument":
                                argument_count += 1
            elif expression_element.tag == "operator":
                operator = expression_element.get("value")
                next_element = "term2"
            if current_element == "term1":
                next_element = "operator"
            elif current_element == "term2":
                if operator == "+":
                    generated_assembly += ["pop b", "pop a", "add b", "push a"]
                elif operator == "-":
                    generated_assembly += ["pop b", "pop a", "sub b", "push a"]
                elif operator == "&":
                    generated_assembly += ["pop b", "pop a", "and b", "push a"]
                elif operator == "|":
                    generated_assembly += ["pop b", "pop a", "or a", "push a"]
                elif operator == "^":
                    generated_assembly += ["pop b", "pop a", "xor a", "push a"]
                elif operator == "==":
                    generated_assembly += ["pop b", "pop a", "sub b", "zfo", "push a"]
                elif operator == ">":
                    generated_assembly += ["pop a", "pop b", "sub b", "sfo", "push a"]
                elif operator == "<":
                    generated_assembly += ["pop b", "pop a", "sub b", "sfo", "push a"]
                elif operator == ">=":
                    generated_assembly += ["pop b", "pop a", "sub b", "sfo", "xor 1", "push a"]
                elif operator == "<=":
                    generated_assembly += ["pop a", "pop b", "sub b", "sfo", "xor 1", "push a"]
                elif operator == "and":
                    generated_assembly += ["pop a", "pop b", "and b", "push a"]
                elif operator == "or":
                    generated_assembly += ["pop b", "pop a", "or b", "push a"]
                next_element = "operator"
            current_element = next_element
    
    def compile_statements(body_node):
        for statement in list(body_node):
            if statement.tag == "declarationStatement":
                compile_declaration(statement)
            elif statement.tag == "ifStatement":
                compile_if(statement)
            elif statement.tag == "whileStatement":
                compile_while(statement)
            elif statement.tag == "forStatement":
                compile_for(statement)
            elif statement.tag == "assignmentStatement":
                compile_assignment(statement)
            elif statement.tag == "outputStatement":
                compile_output(statement)
            elif statement.tag == "returnStatement":
                compile_return(statement)
    
    def compile_declaration(declaration_node):
        nonlocal generated_assembly
        if len(declaration_node) == 1:
            return
        variable = list(declaration_node)[0].get("value")
        compile_expression(list(declaration_node)[1])
        #local_count refers to the offset from the base pointer the local variable
        #is. The same applies to argument count and this is 4 as the stack frame for
        #a function is arranged in the way that between the base pointer and the arguments
        #for that function there is the program counter and the rest of the base pointer.
        local_count = 1
        argument_count = 4
        for variable in function_table:
            if variable[0] == declaration_node[0].get("value"):
                if variable[1] == "local":
                    #Loads the accumulator with the local variable and pushes the accumulator
                    generated_assembly += ("pop a", "mphbp", "mov b a", "sp h {}".format(local_count), "mov a b", "mov hl ar")
                elif variable[1] == "argument":
                    #Loads the accumulator with the argument variable and pushes the accumulator
                    generated_assembly += ("pop a", "mphbp", "mov b a", "ap h {}".format(argument_count), "mov a b", "mov hl ar")
            else:
                #If the current variable is not the one looked for then it must be one
                #further away from the base pointer so increment the offset                
                if variable[1] == "local":
                    local_count += 1
                elif variable[1] == "argument":
                    argument_count += 1

    def compile_if(if_node):
        nonlocal generated_assembly
        nonlocal current_label
        elif_count = 0
        else_present = False
        for if_child in list(if_node):
            if if_child.tag == "elifCondition":
                elif_count += 1
            elif if_child.tag == "elseBody":
                else_present = True
        for i, if_child in enumerate(list(if_node)):
            if if_child.tag == "ifCondition":
                final_jump = current_label
                current_label += 1
                compile_expression(if_child[0])
                #Only an if (no elif or else)
                if else_present == False and elif_count == 0:
                    generated_assembly += ("pop a", "dec", "jn .L{}".format(final_jump))
                    compile_statements(list(if_node)[i + 1])
                else:
                    generated_assembly += ("pop a", "dec", "jn .L{}".format(current_label))
                    compile_statements(list(if_node)[i + 1])
                    generated_assembly.append("jmp .L{}".format(final_jump))
            elif if_child.tag == "elifCondition":
                generated_assembly.append(".L{}:".format(current_label))
                current_label += 1
                compile_expression(if_child[0])
                #If this is the last elif statement jump to the end afterwards
                if else_present == False and (i/2 == elif_count):
                    generated_assembly += ("pop a", "dec", "jn .L{}".format(final_jump))
                    compile_statements(list(if_node)[i + 1])
                else:
                    generated_assembly += ("pop a", "dec", "jn .L{}".format(current_label))
                    compile_statements(list(if_node)[i + 1])
                    generated_assembly.append("jmp .L{}".format(final_jump))
            elif if_child.tag == "elseBody":
                generated_assembly.append(".L{}:".format(current_label))
                compile_statements(list(if_node)[i])
        generated_assembly.append(".L{}:".format(final_jump))

    def compile_while(while_node):
        nonlocal generated_assembly
        nonlocal current_label
        final_jump = current_label
        current_label += 1
        generated_assembly.append(".L{}:".format(current_label))
        current_label += 1
        compile_expression(list(while_node)[0][0])
        generated_assembly += ("pop a", "dec", "jn .L{}".format(final_jump))
        compile_statements(list(while_node)[1])
        generated_assembly.append("jmp .L{}".format(current_label - 1))
        generated_assembly.append(".L{}:".format(final_jump))
        
    def compile_for(for_node):
        nonlocal generated_assembly
        nonlocal current_label
        for_node_children = list(for_node)
        final_jump = current_label
        current_label += 1
        variable = for_node_children[0].get("value")
        start_value = for_node_children[1].get("value")
        end_value = for_node_children[2].get("value")
        increment = for_node_children[3].get("value")
        body = for_node_children[4]
        #Creates a psuedo assignment node to handle the assignment at the beginning
        #of the for loop
        assignment_node = ET.Element("assigment")
        ET.SubElement(assignment_node, "localVariable", value = variable)
        assignment_node_expression = ET.SubElement(assignment_node, "expression")
        ET.SubElement(assignment_node_expression, "integer_constant", value = start_value)
        compile_assignment(assignment_node)
        generated_assembly.append(".L{}:".format(current_label))
        #Creates a pseudo condition node
        condition_node = ET.Element("expression")
        ET.SubElement(condition_node, "localVariable", value = variable)
        ET.SubElement(condition_node, "operator", value = ">=")
        ET.SubElement(condition_node, "integer_constant", value = end_value)
        compile_expression(condition_node)
        generated_assembly += ("pop a", "dec", "jp .L{}".format(final_jump))
        compile_statements(body)
        #Creates a psuedo assignment node
        increment_node = ET.Element("assignmentStatement")
        ET.SubElement(increment_node, "localVariable", value = variable)
        increment_expression = ET.SubElement(increment_node, "expression")
        ET.SubElement(increment_expression, "localVariable", value = variable)
        ET.SubElement(increment_expression, "operator", value = "+")
        ET.SubElement(increment_expression, "integer_constant", value = increment)
        compile_assignment(increment_node)
        generated_assembly.append("jmp .L{}".format(current_label))
        current_label += 1
        generated_assembly.append(".L{}:".format(final_jump))
        
    def compile_assignment(assigment_node):
        nonlocal generated_assembly
        compile_expression(list(assigment_node)[1])
        #local_count refers to the offset from the base pointer the local variable
        #is. The same applies to argument count and this is 4 as the stack frame for
        #a function is arranged in the way that between the base pointer and the arguments
        #for that function there is the program counter and the rest of the base pointer.
        local_count = 1
        argument_count = 4
        for variable in function_table:
            if variable[0] == assigment_node[0].get("value"):
                if variable[1] == "local":
                    #Loads the accumulator with the local variable and pushes the accumulator
                    generated_assembly += ("pop a", "mphbp", "mov b a", "sp h {}".format(local_count), "mov a b", "mov hl ar")
                elif variable[1] == "argument":
                    #Loads the accumulator with the argument variable and pushes the accumulator
                    generated_assembly += ("pop a", "mphbp", "mov b a", "ap h {}".format(argument_count), "mov a b", "mov hl ar")
            else:
                #If the current variable is not the one looked for then it must be one
                #further away from the base pointer so increment the offset
                if variable[1] == "local":
                    local_count += 1
                elif variable[1] == "argument":
                    argument_count += 1

    def compile_output(output_node):
        nonlocal generated_assembly
        compile_expression(list(output_node)[0])
        generated_assembly += ("pop a", "out")

    def compile_return(return_node):
        nonlocal generated_assembly
        #Compiles the expression and leaves the value in the B register
        compile_expression(list(return_node)[0])
        generated_assembly.append("pop b")
        local_variable_count = 0
        for variable in function_table:
            if variable[1] == "localVariable":
                local_variable_count += 1
        #Subtracts the number of local variables from the stack pointer to 'pop'
        #them all off at once
        generated_assembly.append("sp sp {}".format(local_variable_count))
        #Cleans up the stack frame
        generated_assembly += ("mov sp bp", "pop bp", "pop c")

    compile_initial(initial_statement)
    for program_element in list(root):
        if program_element.tag == "functionDeclaration":
            compile_function(program_element)

    return generated_assembly
