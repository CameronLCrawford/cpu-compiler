import xml.etree.ElementTree as ET

class Generator:
    def __init__(self, abstract_syntax_tree, symbol_table):
        self.root = abstract_syntax_tree
        self.symbol_table = symbol_table
        self.generated_assembly = []
        #The symbol table for the current function
        self.function_table = None
        #This keeps a track of the name used for the compiler-generated
        #labels created when using conditionals. For example: the first
        #label will be ".L1" then it will be ".Ln" through to ".L0" as 
        #the final node
        self.current_label = 0

    def compile_program(self):
        initial_statement = self.root.getchildren()[0]
        self.compile_initial(initial_statement)
        for program_element in self.root.getchildren():
            if program_element.tag == "functionDeclaration":
                self.compile_function(program_element)
        return self.generated_assembly

    def compile_initial(self, initial_node):
        self.generated_assembly.append("push c")
        #Adds 10 to the pushed program counter so that when it is popped the program execution
        #resumes from the next sequential instruction
        self.generated_assembly += ("pop l", "pop h", "ap h 10", "push h", "push l")
        self.generated_assembly.append("jmp @{}".format(initial_node.get("value")))
        self.generated_assembly.append("hlt")

    def compile_function_call(self, function_node):
        #Handles all arguments in reverse order so they are accessed with relation
        #to the base pointer correctly
        for argument in reversed(function_node.getchildren()):
            self.compile_expression(argument)
        self.generated_assembly.append("push c")
        #Adds 10 to the pushed program counter so that when it is popped the program execution
        #resumes from the next sequential instruction
        self.generated_assembly += ("pop l", "pop h", "ap h 10", "push h", "push l")
        self.generated_assembly.append("jmp @{}".format(function_node.get("value")))
        #When a function returns, the return value is stored in the B register so it
        #is moved to the accumulator
        self.generated_assembly.append("mov a b")

    def compile_function(self, function_node):
        function_name = function_node.get("value")
        #Adds the label for that function so it is identifiable and can be jumped to
        self.generated_assembly.append("@{}:".format(function_name))
        self.function_table = self.symbol_table[1][self.symbol_table[0].index(function_name)]
        self.generated_assembly += ("push bp", "mov bp sp")
        for local_variable in self.function_table:
            if local_variable[1] == "local":
                #Initialises all local variables to 0
                self.generated_assembly.append("push 0")
        for function_element in function_node:
            if function_element.tag == "functionBody":
                self.compile_statements(function_element)

    def compile_expression(self, expression_node):
        current_element = "term1"
        next_element = "operator"
        operator = None
        for expression_element in expression_node.getchildren():
            if current_element in ("term1", "term2"):
                if expression_element.tag == "expression":
                    self.compile_expression(expression_element)
                elif expression_element.tag == "integer_constant":
                    integer_constant = expression_element.get("value")
                    self.generated_assembly.append("push {}".format(integer_constant))
                elif expression_element.tag == "functionCall":
                    self.compile_function_call(expression_element)
                    self.generated_assembly.append("push a")
                elif expression_element.tag == "localVariable":
                    #local_count refers to the offset from the base pointer the local variable
                    #is. The same applies to argument count and this is 4 as the stack frame for
                    #a function is arranged in the way that between the base pointer and the arguments
                    #for that function there is the program counter and the rest of the base pointer.
                    local_count = 1
                    argument_count = 4
                    for variable in self.function_table:
                        if variable[0] == expression_element.get("value"):
                            if variable[1] == "local":
                                #Loads the accumulator with the local variable and pushes the accumulator
                                self.generated_assembly += ("mphbp", "mov b a", "sp h {}".format(local_count), "mov a b", "mov ar hl", "push a")
                            elif variable[1] == "argument":
                                #Loads the accumulator with the argument variable and pushes the accumulator
                                self.generated_assembly += ("mphbp", "mov b a", "ap h {}".format(argument_count), "mov a b", "mov ar hl", "push a")
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
                    self.generated_assembly += ["pop b", "pop a", "add b", "push a"]
                elif operator == "-":
                    self.generated_assembly += ["pop b", "pop a", "sub b", "push a"]
                elif operator == "&":
                    self.generated_assembly += ["pop b", "pop a", "and b", "push a"]
                elif operator == "|":
                    self.generated_assembly += ["pop b", "pop a", "or a", "push a"]
                elif operator == "^":
                    self.generated_assembly += ["pop b", "pop a", "xor a", "push a"]
                elif operator == "==":
                    self.generated_assembly += ["pop b", "pop a", "sub b", "zfo", "push a"]
                elif operator == ">":
                    self.generated_assembly += ["pop a", "pop b", "sub b", "sfo", "push a"]
                elif operator == "<":
                    self.generated_assembly += ["pop b", "pop a", "sub b", "sfo", "push a"]
                elif operator == ">=":
                    self.generated_assembly += ["pop b", "pop a", "sub b", "sfo", "xor 1", "push a"]
                elif operator == "<=":
                    self.generated_assembly += ["pop a", "pop b", "sub b", "sfo", "xor 1", "push a"]
                elif operator == "and":
                    self.generated_assembly += ["pop a", "pop b", "and b", "push a"]
                elif operator == "or":
                    self.generated_assembly += ["pop b", "pop a", "or b", "push a"]
                next_element = "operator"
            current_element = next_element
    
    def compile_statements(self, body_node):
        for statement in body_node.getchildren():
            if statement.tag == "declarationStatement":
                self.compile_declaration(statement)
            elif statement.tag == "ifStatement":
                self.compile_if(statement)
            elif statement.tag == "whileStatement":
                self.compile_while(statement)
            elif statement.tag == "forStatement":
                self.compile_for(statement)
            elif statement.tag == "assignmentStatement":
                self.compile_assignment(statement)
            elif statement.tag == "outputStatement":
                self.compile_output(statement)
            elif statement.tag == "returnStatement":
                self.compile_return(statement)
    
    def compile_declaration(self, declaration_node):
        if len(declaration_node.getchildren()) == 1:
            return
        variable = declaration_node.getchildren()[0].get("value")
        self.compile_expression(declaration_node.getchildren()[1])
        #local_count refers to the offset from the base pointer the local variable
        #is. The same applies to argument count and this is 4 as the stack frame for
        #a function is arranged in the way that between the base pointer and the arguments
        #for that function there is the program counter and the rest of the base pointer.
        local_count = 1
        argument_count = 4
        for variable in self.function_table:
            if variable[0] == declaration_node[0].get("value"):
                if variable[1] == "local":
                    #Loads the accumulator with the local variable and pushes the accumulator
                    self.generated_assembly += ("pop a", "mphbp", "mov b a", "sp h {}".format(local_count), "mov a b", "mov hl ar")
                elif variable[1] == "argument":
                    #Loads the accumulator with the argument variable and pushes the accumulator
                    self.generated_assembly += ("pop a", "mphbp", "mov b a", "ap h {}".format(argument_count), "mov a b", "mov hl ar")
            else:
                #If the current variable is not the one looked for then it must be one
                #further away from the base pointer so increment the offset                
                if variable[1] == "local":
                    local_count += 1
                elif variable[1] == "argument":
                    argument_count += 1

    def compile_if(self, if_node):
        elif_count = 0
        else_present = False
        for if_child in if_node.getchildren():
            if if_child.tag == "elifCondition":
                elif_count += 1
            elif if_child.tag == "elseBody":
                else_present = True
        for i, if_child in enumerate(if_node.getchildren()):
            if if_child.tag == "ifCondition":
                final_jump = self.current_label
                self.current_label += 1
                self.compile_expression(if_child[0])
                #Only an if (no elif or else)
                if else_present == False and elif_count == 0:
                    self.generated_assembly += ("pop a", "dec", "jn .L{}".format(final_jump))
                    self.compile_statements(if_node.getchildren()[i + 1])
                else:
                    self.generated_assembly += ("pop a", "dec", "jn .L{}".format(self.current_label))
                    self.compile_statements(if_node.getchildren()[i + 1])
                    self.generated_assembly.append("jmp .L{}".format(final_jump))
            elif if_child.tag == "elifCondition":
                self.generated_assembly.append(".L{}:".format(self.current_label))
                self.current_label += 1
                self.compile_expression(if_child[0])
                #If this is the last elif statement jump to the end afterwards
                if else_present == False and (i/2 == elif_count):
                    self.generated_assembly += ("pop a", "dec", "jn .L{}".format(final_jump))
                    self.compile_statements(if_node.getchildren()[i + 1])
                else:
                    self.generated_assembly += ("pop a", "dec", "jn .L{}".format(self.current_label))
                    self.compile_statements(if_node.getchildren()[i + 1])
                    self.generated_assembly.append("jmp .L{}".format(final_jump))
            elif if_child.tag == "elseBody":
                self.generated_assembly.append(".L{}:".format(self.current_label))
                self.compile_statements(if_node.getchildren()[i])
        self.generated_assembly.append(".L{}:".format(final_jump))

    def compile_while(self, while_node):
        final_jump = self.current_label
        self.current_label += 1
        self.generated_assembly.append(".L{}:".format(self.current_label))
        self.current_label += 1
        self.compile_expression(while_node.getchildren()[0][0])
        self.generated_assembly += ("pop a", "dec", "jn .L{}".format(final_jump))
        self.compile_statements(while_node.getchildren()[1])
        self.generated_assembly.append("jmp .L{}".format(self.current_label - 1))
        self.generated_assembly.append(".L{}:".format(final_jump))
        
    def compile_for(self, for_node):
        for_node_children = for_node.getchildren()
        final_jump = self.current_label
        self.current_label += 1
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
        self.compile_assignment(assignment_node)
        self.generated_assembly.append(".L{}:".format(self.current_label))
        #Creates a pseudo condition node
        condition_node = ET.Element("expression")
        ET.SubElement(condition_node, "localVariable", value = variable)
        ET.SubElement(condition_node, "operator", value = "==")
        ET.SubElement(condition_node, "integer_constant", value = end_value)
        self.compile_expression(condition_node)
        self.generated_assembly += ("pop a", "dec", "jp .L{}".format(final_jump))
        self.compile_statements(body)
        #Creates a psuedo assignment node
        increment_node = ET.Element("assignmentStatement")
        ET.SubElement(increment_node, "localVariable", value = variable)
        increment_expression = ET.SubElement(increment_node, "expression")
        ET.SubElement(increment_expression, "localVariable", value = variable)
        ET.SubElement(increment_expression, "operator", value = "+")
        ET.SubElement(increment_expression, "integer_constant", value = increment)
        self.compile_assignment(increment_node)
        self.generated_assembly.append("jmp .L{}".format(self.current_label))
        self.current_label += 1
        self.generated_assembly.append(".L{}:".format(final_jump))
        
    def compile_assignment(self, assigment_node):
        self.compile_expression(assigment_node.getchildren()[1])
        #local_count refers to the offset from the base pointer the local variable
        #is. The same applies to argument count and this is 4 as the stack frame for
        #a function is arranged in the way that between the base pointer and the arguments
        #for that function there is the program counter and the rest of the base pointer.
        local_count = 1
        argument_count = 4
        for variable in self.function_table:
            if variable[0] == assigment_node[0].get("value"):
                if variable[1] == "local":
                    #Loads the accumulator with the local variable and pushes the accumulator
                    self.generated_assembly += ("pop a", "mphbp", "mov b a", "sp h {}".format(local_count), "mov a b", "mov hl ar")
                elif variable[1] == "argument":
                    #Loads the accumulator with the argument variable and pushes the accumulator
                    self.generated_assembly += ("pop a", "mphbp", "mov b a", "ap h {}".format(argument_count), "mov a b", "mov hl ar")
            else:
                #If the current variable is not the one looked for then it must be one
                #further away from the base pointer so increment the offset
                if variable[1] == "local":
                    local_count += 1
                elif variable[1] == "argument":
                    argument_count += 1

    def compile_output(self, output_node):
        self.compile_expression(output_node.getchildren()[0])
        self.generated_assembly += ("pop a", "out")

    def compile_return(self, return_node):
        #Compiles the expression and leaves the value in the B register
        self.compile_expression(return_node.getchildren()[0])
        self.generated_assembly.append("pop b")
        local_variable_count = 0
        for variable in self.function_table:
            if variable[1] == "localVariable":
                local_variable_count += 1
        #Subtracts the number of local variables from the stack pointer to 'pop'
        #them all off at once
        self.generated_assembly.append("sp sp {}".format(local_variable_count))
        #Cleans up the stack frame
        self.generated_assembly += ("mov sp bp", "pop bp", "pop c")
