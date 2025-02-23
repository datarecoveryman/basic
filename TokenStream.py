class Token:
    def __init__(self, value, original):
        self.value = value
        self.original = original    
    def __str__(self):
        value = f"\"{self.value}\"" if isinstance(self.value, str) else self.value
        return f"{self.__class__.__name__}({value}, \"{self.original}\")"
    def __repr__(self):
        return str(self)
class TokenDelimiter(Token):
    pass
class TokenNewline(Token):
    def __str__(self):
        return f"{self.__class__.__name__}()"
class TokenNumber(Token):
    pass
class TokenOperator(Token):
    pass
class TokenSymbol(Token):
    pass
class TokenString(Token):
    pass

class TokenStreamSkippy:
    # This is a "skippy" version of TokenStream.
    # It skips leading spaces (non-newline whitespace), but
    # then demands the required token.

    # TODO: Make the take_ functions even more abstract using take_custom.

    def __init__(self, text):
        self.text = text
        self.idx = 0
        self.operators = ["=", "!", "+", "-", "*", "/", "^", "<", ">", "<=", ">=", "==", "<>"]
        self.delims = "(),"
        self.spaces = " \t"
        self.newlines = "\n\r"
        self.var_first = "_ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.var_other = "_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    def next(self):
        self.skip()
        p = self.peek()
        if p is None:
            return None
        # Guess based off the first non-space character
        if p == "\n":
            return self.take_newline()
        if p == '"':
            return self.take_string()
        if p.isdigit():
            return self.take_number()
        if p in self.delims:
            return self.take_delim()
        if p in self.operators:
            return self.take_operator()
        if p.upper() in self.var_other:
            return self.take_symbol()
        raise ValueError(f"Unexpected character: {p}")
    
    def peek(self): # (READ ONLY) View the current character
        if self.idx < len(self.text):
            return self.text[self.idx]
        return None
    
    def remaining(self): # Return tokens after the current position
        tokens = []
        token = self.next()
        while token is not None:
            tokens.append(token)
            token = self.next()
        return tokens

    def skip(self):
        while self.peek() is not None and self.peek() in self.spaces:
            self.idx += 1
        return self.peek()

    def take_until_newline(self): # Read <not newlines> until the end of the line
        # Intended for reading everything after a REM,
        # even an empty REM would still have the trailing newline.
        # Because this returns the consumed tokens, it also has to
        # consume the newline.
        n = self.next()
        if n is None:
            return None # must have trailing newline
        tokens = []
        while n is not None and not isinstance(n, TokenNewline):
            tokens.append(n)
            n = self.next()
        if n is None:
            raise ValueError("Unterminated line")
        return tokens
    
    # TODO: Test
    def take_custom(self, fn_pred, fn_build):
        self.skip()
        if self.peek() is None or not fn_pred(self.peek()):
            return None
        foo = self.take_lambda(fn_pred)
        return fn_build(foo)

    def take_alpha(self):
        self.skip()
        test_alpha = lambda c: c.isalpha()
        if self.peek() is None or not test_alpha(self.peek()):
            return None
            #raise ValueError(f"Expected alpha, got {self.peek()}")
        sym = self.take_lambda(test_alpha)
        return TokenSymbol(sym.upper(), sym)
    
    def take_delim(self):
        self.skip()
        delim = self.peek()
        if delim not in self.delims:
            return None
            #raise ValueError(f"Expected delimiter, got {delim}")
        self.idx += 1
        return TokenDelimiter(delim, delim)

    def take_lambda(self, fn): # Read a token using a function
        token = ""
        while self.peek() is not None and fn(self.peek()):
            token += self.peek()
            self.idx += 1
        return token
    
    def take_newline(self):
        self.skip()
        nl = self.peek()
        if nl != "\n":
            return None
            #raise ValueError(f"Expected newline, got {nl}")
        self.idx += 1
        return TokenNewline(nl, nl)

    def take_number(self):
        self.skip()
        test_digit = lambda c: c.isdigit()
        if self.peek() is None or not test_digit(self.peek()):
            return None
            #raise ValueError(f"Expected number, got {self.peek()}")
        num = self.take_lambda(test_digit)
        return TokenNumber(int(num), num) if len(num) else None

    def take_operator(self):
        self.skip()
        test_op = lambda c: c in self.operators
        if self.peek() is None or not test_op(self.peek()):
            return None
            #raise ValueError(f"Expected operator, got {self.peek()}")
        ops = self.take_lambda(test_op)
        return TokenOperator(ops, ops)
    
    def take_string(self):
        self.skip()
        # Open quote
        open_quote = self.peek()
        if open_quote != '"':
            return None
            #raise ValueError(f"Expected string, got {open_quote}")
        self.idx += 1
        # Contents (no \" allowed)
        contents = ""
        while self.peek() is not None and self.peek() != '"':
            contents += self.peek()
            self.idx += 1
        # Close quote
        if self.peek() != '"':
            raise ValueError("Unterminated string")
        self.idx += 1
        return TokenString(contents, contents)
    
    def take_symbol(self):
        self.skip()
        test_sym = lambda c: c.upper() in self.var_other
        if self.peek() is None or not test_sym(self.peek()):
            return None
            #raise ValueError(f"Expected symbol, got {self.peek()}")
        sym = self.take_lambda(test_sym)
        return TokenSymbol(sym.upper(), sym)

class TokenStream:
    # So, take_delim() and take_newline() demand that
    # they consume the correct character.
    # Other functions just stop at the first non-matching character.
    # TODO: think about this; and see if a name change makes it better.

    def __init__(self, text):
        self.text = text
        self.idx = 0
        self.operators = ["=", "!", "+", "-", "*", "/", "^", "<", ">", "<=", ">=", "==", "<>"]
        self.delims = "(),"
        self.var_first = "_ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.var_other = "_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        self.create_newline_tokens = True # BASIC uses newlines, so keep them.
    
    def all(self): # Return all tokens
        self.reset()
        return self.remaining()
    
    def next(self): # Return next token
        # Skip whitespace
        while self.peek() is not None and self.peek().isspace():
            if self.create_newline_tokens and self.peek() == "\n":
                self.idx += 1
                return TokenNewline("\n", "\n")
            self.idx += 1
        # Use peek to determine what to read
        p = self.peek()
        if p is None:
            return None
        if p == '"':
            self.idx += 1
            return self.take_string()
        if p.isdigit():
            return self.take_number()
        if p.upper() in self.var_other:
            return self.take_symbol()
        if p in self.delims:
            return self.take_delim()
        if p in self.operators:
            # Checking for a char in a list of strings is a little weird, but
            # for an op like "<=", the first peek() will see "<", and then
            # take_operator() is smart enough to catch the rest.
            # Caveat: multi-character ops must have a single char counterpart!
            return self.take_operator()
        raise ValueError(f"Unexpected character: {p}")
    
    def peek(self): # (READ ONLY) View the current character
        if self.idx < len(self.text):
            return self.text[self.idx]
        return None
    
    # HACK?
    def skip_whitespace(self): # When sitting on whitespace, skip forward to the first non-whitespace
        if self.peek() is None or self.peek() not in " \t\n\r":
            raise ValueError("Cannot call skip_whitespace when not on whitespace.")
        while self.peek() is not None and self.peek() in " \t\n\r":
            self.idx += 1
        return self.peek()

    def remaining(self): # Return tokens after the current position
        tokens = []
        token = self.next()
        while token is not None:
            tokens.append(token)
            token = self.next()
        # Unexpected mutation: self.reset()
        return tokens

    def take_delim(self): # Read a single delimiter
        delim = self.peek()
        if delim not in self.delims:
            raise ValueError(f"Expected delimiter, got {delim}")
        self.idx += 1
        return TokenDelimiter(delim, delim)

    def take_lambda(self, fn): # Read a token using a function
        token = ""
        while self.peek() is not None and fn(self.peek()):
            token += self.peek()
            self.idx += 1
        return token
    
    def take_newline(self): # Read a newline
        nl = self.peek()
        if nl != "\n":
            raise ValueError(f"Expected newline, got {nl}")
        self.idx += 1
        return TokenNewline(nl, nl)
    def take_newline_ff(self): # Read a newline, ignoring leading whitespace
        while self.peek() is not None and self.peek() != "\n" and self.peek().isspace():
            self.idx += 1
        return self.take_newline()

    # def take_number(self): # Read digits
    #     num = ""
    #     while self.peek() is not None and self.peek().isdigit():
    #         num += self.peek()
    #         self.idx += 1
    #     return TokenNumber(int(num), num) if len(num) else None
    def take_number(self):
        num = self.take_lambda(lambda c: c.isdigit())
        return TokenNumber(int(num), num) if len(num) else None
    def take_number_ff(self): # Read digits, ignoring leading whitespace
        while self.peek() is not None and self.peek().isspace():
            self.idx += 1
        return self.take_number()

    # def take_operator(self): # Read a (multi-character) operator
    #     ops = ""
    #     while self.peek() is not None and self.peek() in self.operators:
    #         ops += self.peek()
    #         self.idx += 1
    #     return TokenOperator(ops, ops)
    def take_operator(self):
        ops = self.take_lambda(lambda c: c in self.operators)
        return TokenOperator(ops, ops)
    def take_operator_ff(self): # Read a (multi-character) operator, ignoring leading whitespace
        while self.peek() is not None and self.peek().isspace():
            self.idx += 1
        return self.take_operator()
    
    # def take_alpha(self): # Read an all-alpha symbol
    #     sym = ""
    #     while self.peek() is not None and self.peek().isalpha():
    #         sym += self.peek()
    #         self.idx += 1
    #     return TokenSymbol(sym.upper(), sym)
    def take_alpha(self):
        sym = self.take_lambda(lambda c: c.isalpha())
        return TokenSymbol(sym.upper(), sym)
    
    def take_symbol(self): # Read an alphanumeric symbol
        sym = self.take_lambda(lambda c: c.upper() in self.var_other)
        return TokenSymbol(sym.upper(), sym)
    def take_symbol_ff(self): # Read an alphanumeric symbol, ignoring leading whitespace
        while self.peek() is not None and self.peek().isspace():
            self.idx += 1
        return self.take_symbol()
    
    # def take_string(self): # Read a string wrapped in double-quotes
    #     contents = ""
    #     while self.peek() is not None and self.peek() != '"':
    #         contents += self.peek()
    #         self.idx += 1
    #     # Check for unterminated string
    #     if self.peek() != '"':
    #         raise ValueError("Unterminated string")
    #     self.idx += 1
    #     return TokenString(contents, contents)
    def take_string(self):
        contents = self.take_lambda(lambda c: c != '"')
        if self.peek() != '"':
            raise ValueError("Unterminated string")
        self.idx += 1
        return TokenString(contents, contents)
    def take_string_ff(self): # Read a string, ignoring leading whitespace
        while self.peek() is not None and self.peek().isspace():
            self.idx += 1
        open_quote = self.peek()
        if open_quote != '"':
            raise ValueError(f"Expected string, got {open_quote}")
        self.idx += 1
        return self.take_string()

    def reset(self): # Seek to front
        self.idx = 0
