class Token:
    def __init__(self, value, original):
        self.value = value
        self.original = original    
    def __str__(self):
        value = f"\"{self.value}\"" if isinstance(self.value, str) else self.value
        return f"{self.__class__.__name__}({value}, \"{self.original}\")"
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

class TokenStream:
    def __init__(self, expr):
        self.expr = expr
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
            return self.take_string2()
        if p.isdigit():
            return self.take_number2()
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
        #return self.expr[self.idx]
    
    def peek(self): # (READ ONLY) View the current character
        if self.idx < len(self.expr):
            return self.expr[self.idx]
        return None
    
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
        self.idx += 1
        return TokenDelimiter(delim, delim)

    def take_lambda(self, fn): # Read a token using a function
        token = ""
        while self.peek() is not None and fn(self.peek()):
            token += self.peek()
            self.idx += 1
        return token
    
    def take_number(self): # Read digits
        num = ""
        while self.peek() is not None and self.peek().isdigit():
            num += self.peek()
            self.idx += 1
        return TokenNumber(int(num), num) if len(num) else None
    def take_number2(self):
        num = self.take_lambda(lambda c: c.isdigit())
        return TokenNumber(int(num), num) if len(num) else None

    def take_operator(self): # Read a (multi-character) operator
        ops = ""
        while self.peek() is not None and self.peek() in self.operators:
            ops += self.peek()
            self.idx += 1
        return TokenOperator(ops, ops)
    def take_operator2(self):
        ops = self.take_lambda(lambda c: c in self.operators)
        return TokenOperator(ops, ops)
    
    def take_alpha(self): # Read an all-alpha symbol
        sym = ""
        while self.peek() is not None and self.peek().isalpha():
            sym += self.peek()
            self.idx += 1
        return TokenSymbol(sym.upper(), sym)
    def take_alpha2(self):
        sym = self.take_lambda(lambda c: c.isalpha())
        return TokenSymbol(sym.upper(), sym)
    
    def take_symbol(self): # Read an alphanumeric symbol
        sym = self.take_lambda(lambda c: c.upper() in self.var_other)
        return TokenSymbol(sym.upper(), sym)

    def take_string(self): # Read a string wrapped in double-quotes
        contents = ""
        while self.peek() is not None and self.peek() != '"':
            contents += self.peek()
            self.idx += 1
        # Check for unterminated string
        if self.peek() != '"':
            raise ValueError("Unterminated string")
        self.idx += 1
        return TokenString(contents, contents)
    def take_string2(self):
        contents = self.take_lambda(lambda c: c != '"')
        if self.peek() != '"':
            raise ValueError("Unterminated string")
        self.idx += 1
        return TokenString(contents, contents)

    def reset(self): # Seek to front
        self.idx = 0
