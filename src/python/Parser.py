import xml.etree.ElementTree as element_tree

def parse(tokens):
    root = element_tree.Element("program")
    current_token = 0 
    valid_operators = ("+", "-", "&", "|", "^", "==", ">", "<",
                            "<=", ">=", "and", "or")
    identifier = ""
    integer_constant = 0
    line_count = 0
    initial_function = ""
    pre_declared_functions = []
    #The symbol table stores all of the identifiers and the context
    #that specifies what type of identifier they are.
    #The table stores each function's local variables in a new list
    #and has a separate list for all of the different function names
    #The first sublist is function names and second is local variables.
    #Each function has its own sublist in the second sublist. The index
    #of the sublist of the each function's local variables is the index
    #of the function name in the first list
    symbol_table = [[], []]
    #This is a variable that keeps track of which function is currently
    #being analysed and allows the parser to efficiently log local variables.
    #It is the index in the symbol table of the current function's table of variables
    function_count = -1

    def accept(token):
        nonlocal line_count
        nonlocal identifier
        nonlocal integer_constant
        nonlocal current_token
        line_count = tokens[current_token][-1]
        if len(tokens[current_token]) == 3:
            if tokens[current_token][0] == token:
                if token == "identifier":
                    identifier = tokens[current_token][1]
                elif token == "integer_constant":
                    integer_constant = tokens[current_token][1]
                current_token += 1
                return True
            return False
        if tokens[current_token][0] == token:
            current_token += 1
            return True
        return False


    #Returns true if and only if the next token to be accepted is the expected one (first argument).
    #Else returns a syntax error and prints the expected token
    def expect(token):
        if accept(token):
            return True
        print("ERROR: Incorrect syntax on line {}.".format(line_count - 1))
        print(token)
        return False

    #Looks ahead to the next token and returns whether it is the expected one
    #(first argument) as a boolean
    def look_ahead(token):
        next_token = tokens[current_token][0]
        if len(next_token) == 3:
            return next_token[0] == token
        return next_token == token
        
    def parse_pre_declaration():
        expect("identifier")
        log_pre_declaration()
        expect(";")

    def parse_statements(node):
        while not accept("}"):
            if accept("if"):
                parse_if(node)
            elif accept("while"):
                parse_while(node)
            elif accept("for"):
                parse_for(node)
            elif accept("return"):
                parse_return(node)
            elif accept("var"):
                parse_declaration(node)
            elif accept("identifier"):
                parse_assignment(node)
            elif accept("output"):
                parse_output(node)
            else:
                print("ERROR: undefined statement body on line {}.".format(line_count))
                break

    def parse_if(node):
        if_node = element_tree.SubElement(node, "ifStatement")
        if expect("("):
            parse_expression(element_tree.SubElement(if_node, "ifCondition"))
            expect(")")
        if expect("{"):
            parse_statements(element_tree.SubElement(if_node, "ifBody"))
        while accept("elif"):
            if expect("("):
                parse_expression(element_tree.SubElement(if_node, "elifCondition"))
                expect(")")
            if expect("{"):
                parse_statements(element_tree.SubElement(if_node, "elifBody"))
        if accept("else"):
            if expect("{"):
                parse_statements(element_tree.SubElement(if_node, "elseBody"))

    def parse_while(node):
        while_node = element_tree.SubElement(node, "whileStatement")
        expect("(")
        parse_expression(element_tree.SubElement(while_node, "whileCondition"))
        expect(")")
        expect("{")
        parse_statements(element_tree.SubElement(while_node, "whileBody"))

    def parse_for(node):
        for_node = element_tree.SubElement(node, "forStatement")
        expect("identifier")
        element_tree.SubElement(for_node, "loopControlVariable", value = identifier)
        expect("=")
        expect("integer_constant")
        element_tree.SubElement(for_node, "startValue", value = integer_constant)
        expect("to")
        expect("integer_constant")
        element_tree.SubElement(for_node, "endValue", value = integer_constant)
        expect(":")
        expect("integer_constant")
        element_tree.SubElement(for_node, "incrementValue", value = integer_constant)
        expect("{")
        for_body_node = element_tree.SubElement(for_node, "forBody")
        parse_statements(for_body_node)

    def parse_return(node):
        return_node = element_tree.SubElement(node, "returnStatement")
        parse_expression(return_node)
        expect(";")

    def parse_declaration(node):
        declaration_node = element_tree.SubElement(node, "declarationStatement")
        expect("identifier")
        element_tree.SubElement(declaration_node, "localVariable", value = identifier)
        log_local_variable("local")
        if accept("="):
            parse_expression(declaration_node)
            expect(";")
        elif accept(","):
            while not accept(";"):
                expect("identifier")
                element_tree.SubElement(declaration_node, "localVariable", value = identifier)
                log_local_variable("local")
                if accept(";"):
                    break
                expect(",")
        elif accept(";"):
            return

    def parse_assignment(node):
        assignment_node = element_tree.SubElement(node, "assignmentStatement")
        element_tree.SubElement(assignment_node, "localVariable", value = identifier)
        expect("=")
        parse_expression(assignment_node)
        expect(";")

    def parse_expression(node):
        expression_node = element_tree.SubElement(node, "expression")
        previous_token_operator = False
        while True:
            previous_token_operator = not previous_token_operator
            if previous_token_operator:
                if accept("integer_constant"):
                    element_tree.SubElement(expression_node, "integer_constant", value = integer_constant)
                #Either local variable or function call
                elif accept("identifier"):
                    variable_type = check_identifier_type()
                    #Function call
                    if variable_type == "functionName":
                        expect("(")
                        parse_call(expression_node)
                    #Variable
                    else:
                        element_tree.SubElement(expression_node, variable_type, value = identifier)
                #Handles nested expressions
                elif accept("("):
                    parse_expression(expression_node)
                    expect(")")
                else:
                    #All signify the end of an expression declaration
                    if look_ahead(";") or look_ahead(")") or look_ahead(","):
                        return
                    else:
                        print("ERROR: unidentified term on line {}.".format(line_count))
            else:
                accepted_operator = False
                for operator in valid_operators:
                    if accept(operator):
                        element_tree.SubElement(expression_node, "operator", value = operator)
                        accepted_operator = True
                        break
                if accepted_operator:
                    continue
                #All signify the end of an expression declaration
                if look_ahead(";") or look_ahead(")") or look_ahead(","):
                        return
                else:
                    print("ERROR: unidentified operator on line {}.".format(line_count))

    def parse_call(node):
        function_call_node = element_tree.SubElement(node, "functionCall",  value = identifier)
        parse_expression(function_call_node)
        while not accept(")"):
            expect(",")
            parse_expression(function_call_node)

    def parse_function_declaration(node):
        function_declaration_node = element_tree.SubElement(node, "functionDeclaration")
        if expect("identifier"):
            log_function_name()
            function_declaration_node.set("value", identifier)
        expect("(")
        if not accept(")"):
            parameter_list_node = element_tree.SubElement(function_declaration_node, "parameterList")
            parse_parameter_list(parameter_list_node)
        expect("{")
        function_body_node = element_tree.SubElement(function_declaration_node, "functionBody")
        parse_statements(function_body_node)
    
    def parse_parameter_list(node):
        while not accept(")"):
            if expect("identifier"):
                log_local_variable("argument")
                element_tree.SubElement(node, "localVariable", value = identifier)
            if accept(")"):
                break
            expect(",")

    def parse_output(node):
        output_node = element_tree.SubElement(node, "outputStatement")
        expect("(")
        parse_expression(output_node)
        expect(")")
        expect(";")

    def parse_initial(node):
        nonlocal initial_function
        if expect("initial") and expect("identifier") and expect(";"):
            element_tree.SubElement(node, "initialStatement", value = identifier)
            initial_function = identifier

    def log_function_name():
        nonlocal function_count
        nonlocal symbol_table
        function_name = identifier
        #Handles the double declaring of functions and prints an error message
        if function_name not in pre_declared_functions and function_name in symbol_table[0]:
            print("ERROR: function ({}) declared twice on line {}".format(function_name, line_count))
            return False
        if function_name in pre_declared_functions:
            function_index = pre_declared_functions.index(function_name)
            function_count = function_index
        else:
            function_count = len(symbol_table[0])
            symbol_table[0].append(function_name)
            symbol_table[1].append([])
 
    def log_local_variable(variable_type):
        nonlocal symbol_table
        local_variable = identifier
        if local_variable in symbol_table[1][function_count]:
            print("ERROR: variable declared more than once in function on line {}.".format(line_count))
            return False
        if local_variable in symbol_table[0] or local_variable in pre_declared_functions:
            print("ERROR: local variable declared using same identfier as function name on line {}.".format(line_count))
            return False
        symbol_table[1][function_count].append((local_variable, variable_type))

    def log_pre_declaration():
        nonlocal symbol_table
        nonlocal function_count
        pre_declared_functions.append(identifier)
        symbol_table[0].append(identifier)
        symbol_table[1].append([])
        function_count += 1

    def check_identifier_type():
        nonlocal identifier
        if identifier in symbol_table[0] or identifier in pre_declared_functions:
            return "functionName"
        for function_table in symbol_table[1]:
            for stored_identifier in function_table:
                if stored_identifier[0] == identifier:
                    return "localVariable"
        print("ERROR: unidentified identifier on line {}.".format(line_count))

    parse_initial(root)
    while True:
        if accept("declare"):
            parse_pre_declaration()
        else:
            break
    #Continues parsing functions until at the end of file
    while current_token < len(tokens) and expect("function"):
        parse_function_declaration(root)
    if initial_function not in symbol_table[0]:
        print("ERROR: initial function not found.")

    #Fetches the next token if and only if it is the one that is expected. The "current_token"
    #pointer is incremented so the next token to be accepted is the next sequential token

    return (root, symbol_table)
