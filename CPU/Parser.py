import xml.etree.ElementTree as element_tree

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.root = element_tree.Element("program")
        self.current_token = 0 
        self.valid_operators = ("+", "-", "&", "|", "^", "==", ">", "<",
	                            "<=", ">=", "and", "or")
        self.identifier = ""
        self.integer_constant = 0
        self.line_count = 0
        self.initial_function = ""
        self.pre_declared_functions = []
        #The symbol table stores all of the identifiers and the context
        #that specifies what type of identifier they are.
        #The table stores each function's local variables in a new list
        #and has a separate list for all of the different function names
        #The first sublist is function names and second is local variables.
        #Each function has its own sublist in the second sublist. The index
        #of the sublist of the each function's local variables is the index
        #of the function name in the first list.
        self.symbol_table = [[], []]
        #This is a variable that keeps track of which function is currently
        #being analysed and allows the parser to efficiently log local variables.
        #It is the index in the symbol table of the current function's table of variables
        self.function_count = -1

    def accept(self, token):
        self.line_count = self.tokens[self.current_token][-1]
        if len(self.tokens[self.current_token]) == 3:
            if self.tokens[self.current_token][0] == token:
                if token == "identifier":
                    self.identifier = self.tokens[self.current_token][1]
                elif token == "integer_constant":
                    self.integer_constant = self.tokens[self.current_token][1]
                self.current_token += 1
                return True
            return False
        if self.tokens[self.current_token][0] == token:
            self.current_token += 1
            return True
        return False

    def expect(self, token):
        if self.accept(token):
            return True
        print("ERROR: Incorrect syntax on line {}.".format(self.line_count - 1))
        print(token)
        return False

    def look_ahead(self, token):
        next_token = self.tokens[self.current_token][0]
        if len(next_token) == 3:
            return next_token[0] == token
        return next_token == token

    def parse_program(self):
        self.parse_initial(self.root)
        while True:
            if self.accept("declare"):
                self.parse_pre_declaration(self.root)
            else:
                break
        while self.current_token < len(self.tokens) and self.expect("function"):
            self.parse_function_declaration(self.root)
        if self.initial_function not in self.symbol_table[0]:
            print("ERROR: initial function not found.")
        
    def parse_pre_declaration(self, node):
        self.expect("identifier")
        self.log_pre_declaration()
        self.expect(";")

    def parse_statements(self, node):
        while not self.accept("}"):
            if self.accept("if"):
                self.parse_if(node)
            elif self.accept("while"):
                self.parse_while(node)
            elif self.accept("for"):
                self.parse_for(node)
            elif self.accept("return"):
                self.parse_return(node)
            elif self.accept("var"):
                self.parse_declaration(node)
            elif self.accept("identifier"):
                self.parse_assignment(node)
            elif self.accept("output"):
                self.parse_output(node)
            else:
                print("ERROR: undefined statement body on line {}.".format(self.line_count))
                break

    def parse_if(self, node):
        if_node = element_tree.SubElement(node, "ifStatement")
        if self.expect("("):
            self.parse_expression(element_tree.SubElement(if_node, "ifCondition"))
            self.expect(")")
        if self.expect("{"):
            self.parse_statements(element_tree.SubElement(if_node, "ifBody"))
        while self.accept("elif"):
            if self.expect("("):
                self.parse_expression(element_tree.SubElement(if_node, "elifCondition"))
                self.expect(")")
            if self.expect("{"):
                self.parse_statements(element_tree.SubElement(if_node, "elifBody"))
        if self.accept("else"):
            if self.expect("{"):
                self.parse_statements(element_tree.SubElement(if_node, "elseBody"))

    def parse_while(self, node):
        while_node = element_tree.SubElement(node, "whileStatement")
        self.expect("(")
        self.parse_expression(element_tree.SubElement(while_node, "whileCondition"))
        self.expect(")")
        self.expect("{")
        self.parse_statements(element_tree.SubElement(while_node, "whileBody"))

    def parse_for(self, node):
        for_node = element_tree.SubElement(node, "forStatement")
        self.expect("identifier")
        element_tree.SubElement(for_node, "loopControlVariable", value = self.identifier)
        self.expect("=")
        self.expect("integer_constant")
        element_tree.SubElement(for_node, "startValue", value = self.integer_constant)
        self.expect("to")
        self.expect("integer_constant")
        element_tree.SubElement(for_node, "endValue", value = self.integer_constant)
        self.expect(":")
        self.expect("integer_constant")
        element_tree.SubElement(for_node, "incrementValue", value = self.integer_constant)
        self.expect("{")
        for_body_node = element_tree.SubElement(for_node, "forBody")
        self.parse_statements(for_body_node)

    def parse_return(self, node):
        return_node = element_tree.SubElement(node, "returnStatement")
        self.parse_expression(return_node)
        self.expect(";")

    def parse_declaration(self, node):
        declaration_node = element_tree.SubElement(node, "declarationStatement")
        self.expect("identifier")
        element_tree.SubElement(declaration_node, "localVariable", value = self.identifier)
        self.log_local_variable("local")
        if self.accept("="):
            self.parse_expression(declaration_node)
            self.expect(";")
        elif self.accept(","):
            while not self.accept(";"):
                self.expect("identifier")
                element_tree.SubElement(declaration_node, "localVariable", value = self.identifier)
                self.log_local_variable("local")
                if self.accept(";"):
                    break
                self.expect(",")
        elif self.accept(";"):
            return

    def parse_assignment(self, node):
        assignment_node = element_tree.SubElement(node, "assignmentStatement")
        element_tree.SubElement(assignment_node, "localVariable", value = self.identifier)
        self.expect("=")
        self.parse_expression(assignment_node)
        self.expect(";")

    def parse_expression(self, node):
        expression_node = element_tree.SubElement(node, "expression")
        previous_token_operator = False
        while True:
            previous_token_operator = not previous_token_operator
            if previous_token_operator:
                if self.accept("integer_constant"):
                    element_tree.SubElement(expression_node, "integer_constant", value = self.integer_constant)
                elif self.accept("identifier"): #Either local variable or function call
                    variable_type = self.check_identifier_type()
                    if variable_type == "functionName": #Function call
                        self.expect("(")
                        self.parse_call(expression_node)
                    else:
                        element_tree.SubElement(expression_node, variable_type, value = self.identifier)
                elif self.accept("("):
                    self.parse_expression(expression_node)
                    self.expect(")")
                else:
                    if self.look_ahead(";") or self.look_ahead(")") or self.look_ahead(","):
                        return
                    else:
                        print("ERROR: unidentified term on line {}.".format(self.line_count))
            else:
                accepted_operator = False
                for operator in self.valid_operators:
                    if self.accept(operator):
                        element_tree.SubElement(expression_node, "operator", value = operator)
                        accepted_operator = True
                        break
                if accepted_operator:
                    continue
                if self.look_ahead(";") or self.look_ahead(")") or self.look_ahead(","):
                        return
                else:
                    print("ERROR: unidentified operator on line {}.".format(self.line_count))

    def parse_call(self, node):
        function_call_node = element_tree.SubElement(node, "functionCall",  value = self.identifier)
        self.parse_expression(function_call_node)
        while not self.accept(")"):
            self.expect(",")
            self.parse_expression(function_call_node)

    def parse_function_declaration(self, node):
        function_declaration_node = element_tree.SubElement(node, "functionDeclaration")
        if self.expect("identifier"):
            self.log_function_name()
            function_declaration_node.set("value", self.identifier)
        self.expect("(")
        if not self.accept(")"):
            parameter_list_node = element_tree.SubElement(function_declaration_node, "parameterList")
            self.parse_parameter_list(parameter_list_node)
        self.expect("{")
        function_body_node = element_tree.SubElement(function_declaration_node, "functionBody")
        self.parse_statements(function_body_node)
    
    def parse_parameter_list(self, node):
        while not self.accept(")"):
            if self.expect("identifier"):
                self.log_local_variable("argument")
                element_tree.SubElement(node, "localVariable", value = self.identifier)
            if self.accept(")"):
                break
            self.expect(",")

    def parse_output(self, node):
        output_node = element_tree.SubElement(node, "outputStatement")
        self.expect("(")
        self.parse_expression(output_node)
        self.expect(")")
        self.expect(";")

    def parse_initial(self, node):
        if self.expect("initial") and self.expect("identifier") and self.expect(";"):
            element_tree.SubElement(node, "initialStatement", value = self.identifier)
            self.initial_function = self.identifier

    def log_function_name(self):
        function_name = self.identifier
        if function_name not in self.pre_declared_functions and function_name in self.symbol_table[0]:
            print("ERROR: function ({}) declared twice on line {}".format(function_name, self.line_count))
            return False
        if function_name in self.pre_declared_functions:
            function_index = self.pre_declared_functions.index(function_name)
            self.function_count = function_index
        else:
            self.function_count = len(self.symbol_table[0])
            self.symbol_table[0].append(function_name)
            self.symbol_table[1].append([])
 
    def log_local_variable(self, variable_type):
        local_variable = self.identifier
        if local_variable in self.symbol_table[1][self.function_count]:
            print("ERROR: variable declared more than once in function on line {}.".format(self.line_count))
            return False
        if local_variable in self.symbol_table[0] or local_variable in self.pre_declared_functions:
            print("ERROR: local variable declared using same identfier as function name on line {}.".format(self.line_count))
            return False
        self.symbol_table[1][self.function_count].append((local_variable, variable_type))

    def log_pre_declaration(self):
        self.pre_declared_functions.append(self.identifier)
        self.symbol_table[0].append(self.identifier)
        self.symbol_table[1].append([])
        self.function_count += 1

    def check_identifier_type(self):
        identifier = self.identifier
        if identifier in self.symbol_table[0] or identifier in self.pre_declared_functions:
            return "functionName"
        for function_table in self.symbol_table[1]:
            for identifier in function_table:
                if identifier[0] == self.identifier:
                    return "localVariable"
        print("ERROR: unidentified identifier on line {}.".format(self.line_count))