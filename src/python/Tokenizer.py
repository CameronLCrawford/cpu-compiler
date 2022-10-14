class Tokenizer:
    def __init__(self, code):
        self.code = code
        self.valid_tokens = (
            "(", ")", "{", "}", ",", ";", "=", "==", "!="
            "+", "-", "++", "--", "&", "|", "^", ":",
            "<", ">", "<=", ">=", "!",
            "and", "or", "xor", "function", "integer_constant",
            "if", "while", "for", "elif", "else", "output",
            "return", "continue", "break", "initial", "var",
            "identifier", "to", "declare"
        )
        #Defines all single character tokens that don't form a part of larger tokens
        self.single_character_tokens = (
            "(", ")", "{", "}", ",", ";", ":", "&", "|", "^", "#"
        )
        self.generated_tokens = []
        self.integer_literal = ""
        self.identifier = ""
        self.line_count = 1

    def scan(self):
        i = 0
        while i < len(self.code): #Main loop of the tokenizer
            character = self.code[i]
            if i == len(self.code) - 1:
                if character == "}":
                    self.add_token(character)
                    break
            next_character = self.code [i + 1]
            if character in self.single_character_tokens: #Handles all single character tokens
                self.add_token(character)
                i += 1
            elif character == "=":
                if next_character == "=":
                    self.add_token("==")
                    i += 2
                else:
                    self.add_token("=")
                    i += 1
            elif character == "+":
                if next_character == "+":
                    self.add_token("++")
                    i += 2
                else:
                    self.add_token("+")
                    i += 1
            elif character == "-":
                if next_character == "-":
                    self.add_token("--")
                    i += 2
                else:
                    self.add_token("-")
                    i += 1
            elif character == "<":
                if next_character == "=":
                    self.add_token("<=")
                    i += 2
                else:
                    self.add_token("<")
                    i += 1
            elif character == ">":
                if next_character == "=":
                    self.add_token(">=")
                    i += 2
                else:
                    self.add_token(">")
                    i += 1
            elif character == "!":
                if next_character == "=":
                    self.add_token("!=")
                    i += 2
                else:
                    self.add_token("!")
                    i += 1
            elif character == "\n":
                self.line_count += 1
                i += 1
            else:
                try:
                    int(character)
                    self.integer_literal += character
                except ValueError:
                    if character == " ":
                        if self.integer_literal != "":
                            self.generated_tokens.append(("integer_constant", self.integer_literal, self.line_count))
                            self.integer_literal = ""
                        if self.identifier != "":
                            if self.identifier in self.valid_tokens:
                                self.generated_tokens.append((self.identifier, self.line_count))
                            else:
                                self.generated_tokens.append(("identifier", self.identifier, self.line_count))
                            self.identifier = ""
                if self.identifier == "" and self.isValidFirstChar(character):
                    self.identifier += character
                elif self.identifier != "" and self.isValidChar(character):
                    self.identifier += character
                i += 1
        return self.generated_tokens

    def add_token(self, token):
        if self.integer_literal != "":
            self.generated_tokens.append(("integer_constant", self.integer_literal, self.line_count))
            self.integer_literal = ""
        if self.identifier != "":
            if self.identifier in self.valid_tokens:
                self.generated_tokens.append((self.identifier, self.line_count))
            else:
                self.generated_tokens.append(("identifier", self.identifier, self.line_count))
            self.identifier = ""
        self.generated_tokens.append((token, self.line_count))

    def isValidFirstChar(self, character):
        ascii_value = ord(character)
        return (ascii_value >= 65 and ascii_value <= 90) or (ascii_value >= 97 and ascii_value <= 122) or character == "_"

    def isValidChar(self, character):
        try:
            int(character)
            return True
        except ValueError:
            return self.isValidFirstChar(character)