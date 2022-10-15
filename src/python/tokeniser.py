def tokenise(storn):
    code = storn
    valid_tokens = (
        "(", ")", "{", "}", ",", ";", "=", "==", "!="
        "+", "-", "++", "--", "&", "|", "^", ":",
        "<", ">", "<=", ">=", "!",
        "and", "or", "xor", "function", "integer_constant",
        "if", "while", "for", "elif", "else", "output",
        "return", "continue", "break", "initial", "var",
        "identifier", "to", "declare"
    )
    #Defines all single character tokens that don't form a part of larger tokens
    single_character_tokens = (
        "(", ")", "{", "}", ",", ";", ":", "&", "|", "^", "#"
    )
    generated_tokens = []
    integer_literal = ""
    identifier = ""
    line_count = 1

    i = 0
    while i < len(code): #Main loop of the tokenizer
        character = code[i]
        if i == len(code) - 1:
            if character == "}":
                add_token(character)
                break
        next_character = code [i + 1]
        if character in single_character_tokens: #Handles all single character tokens
            add_token(character)
            i += 1
        elif character == "=":
            if next_character == "=":
                add_token("==")
                i += 2
            else:
                add_token("=")
                i += 1
        elif character == "+":
            if next_character == "+":
                add_token("++")
                i += 2
            else:
                add_token("+")
                i += 1
        elif character == "-":
            if next_character == "-":
                add_token("--")
                i += 2
            else:
                add_token("-")
                i += 1
        elif character == "<":
            if next_character == "=":
                add_token("<=")
                i += 2
            else:
                add_token("<")
                i += 1
        elif character == ">":
            if next_character == "=":
                add_token(">=")
                i += 2
            else:
                add_token(">")
                i += 1
        elif character == "!":
            if next_character == "=":
                add_token("!=")
                i += 2
            else:
                add_token("!")
                i += 1
        elif character == "\n":
            line_count += 1
            i += 1
        else:
            try:
                int(character)
                integer_literal += character
            except ValueError:
                if character == " ":
                    if integer_literal != "":
                        generated_tokens.append(("integer_constant", integer_literal, line_count))
                        integer_literal = ""
                    if identifier != "":
                        if identifier in valid_tokens:
                            generated_tokens.append((identifier, line_count))
                        else:
                            generated_tokens.append(("identifier", identifier, line_count))
                        identifier = ""
            if identifier == "" and isValidFirstChar(character):
                identifier += character
            elif identifier != "" and isValidChar(character):
                identifier += character
            i += 1

    def add_token(token):
        if integer_literal != "":
            generated_tokens.append(("integer_constant", integer_literal, line_count))
            integer_literal = ""
        if identifier != "":
            if identifier in valid_tokens:
                generated_tokens.append((identifier, line_count))
            else:
                generated_tokens.append(("identifier", identifier, line_count))
            identifier = ""
        generated_tokens.append((token, line_count))

    def isValidFirstChar(character):
        ascii_value = ord(character)
        return (ascii_value >= 65 and ascii_value <= 90) or (ascii_value >= 97 and ascii_value <= 122) or character == "_"

    def isValidChar(character):
        try:
            int(character)
            return True
        except ValueError:
            return isValidFirstChar(character)

    return generated_tokens
