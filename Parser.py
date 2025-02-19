
# Using TokenStream.all() for tokens

# class TokenDelimiter(Token):
# class TokenNumber(Token):
# class TokenOperator(Token):
# class TokenSymbol(Token):
# class TokenString(Token):

import TokenStream

class Code:
    def __init__(self, line_number):
        self.ln = line_number
class CodeAssignment(Code):
    def __init__(self, line_number, var, expr):
        super().__init__(line_number)
        self.var = var
        self.expr = expr
    def __str__(self):
        return f"{self.ln}:Assignment({self.var} <- {self.expr})"
class CodeGoto(Code):
    def __init__(self, line_number, target_line_number):
        super().__init__(line_number)
        self.target = target_line_number
    def __str__(self):
        return f"{self.ln}:Goto({self.target})"
class CodeNoop(Code):
    def __init__(self, line_number, comment):
        super().__init__(line_number)
        self.comment = comment
    def __str__(self):
        return f"{self.ln}:Noop({self.comment})"
class CodePrint(Code):
    def __init__(self, line_number, expr):
        super().__init__(line_number)
        self.expr = expr
    def __str__(self):
        return f"{self.ln}:Print({self.expr})"

class Expression:
    def __init__(self, expr):
        # TODO: this will be a tree or something later
        self.expr = expr
    def __str__(self):
        return f"Expression({self.expr})"

class Parser:
    def __init__(self, token_stream):
        if not isinstance(token_stream, TokenStream.TokenStream):
            raise Exception("Expected TokenStream")
        self.tokens = token_stream
        self.line_number_mandatory = True
    
    def all(self):
        # Return all tokens
        self.tokens.reset()
        tokens = []
        token = self.next()
        while token is not None:
            tokens.append(token)
            token = self.next()
        return tokens
    
    def next(self):
        # Next... statement?
        p = self.tokens.next()
        if p is None:
            return None
        p_line_num = 0
        if self.line_number_mandatory:
            if not isinstance(p, TokenStream.TokenNumber):
                raise Exception("Expected line number; got " + str(p))
            p_line_num = p.value
            p = self.tokens.next()
            if p is None:
                raise Exception("Expected statement after line number; got None")
        #print("Line number:", p_line_num)

        #if isinstance(p, TokenSymbol) and p.value == "IF":
        #    return self.parse_if()
        if isinstance(p, TokenStream.TokenSymbol) and p.value == "GOTO":
            # GOTO 123
            line_number = self.tokens.next()
            if not isinstance(line_number, TokenStream.TokenNumber):
                raise Exception("Expected number after GOTO; got " + str(line_number))
            nl = self.tokens.next()
            if not isinstance(nl, TokenStream.TokenNewline):
                raise Exception(f"Expected newline after {p.value}; got {nl}")
            return CodeGoto(p_line_num, line_number.value)
        if isinstance(p, TokenStream.TokenSymbol) and p.value == "PRINT":
            # ["PRINT", "X", "+", "12345"]
            expr = self.take_expression(p_line_num)
            nl = self.tokens.next()
            if not isinstance(nl, TokenStream.TokenNewline):
                raise Exception(f"Expected newline after {p.value}; got {nl}")
            return CodePrint(p_line_num, expr)
        if isinstance(p, TokenStream.TokenSymbol) and p.value == "LET":
            # Assignment statement, e.g. ["LET", "X", "=", "5"]
            v = self.tokens.next()
            if not isinstance(v, TokenStream.TokenSymbol):
                raise Exception("Expected variable after LET; got " + str(v))
            e = self.tokens.next()
            if not isinstance(e, TokenStream.TokenOperator) or e.value != "=":
                raise Exception("Expected = after variable in LET; got " + str(e))
            expr = self.take_expression(p_line_num)
            nl = self.tokens.next()
            if not isinstance(nl, TokenStream.TokenNewline):
                raise Exception(f"Expected newline after {p.value}; got {nl}")
            return CodeAssignment(p_line_num, v.value, expr)
        #if isinstance(p, TokenSymbol) and p.value == "INPUT":
        #    return self.parse_input()
        #if isinstance(p, TokenSymbol) and p.value == "END":
        #    return self.parse_end()
        if isinstance(p, TokenStream.TokenSymbol) and p.value == "REM":
            # must be like REM "my comment"
            p = self.tokens.next()
            rem_tokens = []
            while p is not None and not isinstance(p, TokenStream.TokenNewline):
                #print("REM token:", p)
                rem_tokens.append(p)
                p = self.tokens.next()
            # Ignore the rest of the line
            rem_line = " ".join([str(t.original) for t in rem_tokens])
            return CodeNoop(p_line_num, rem_line)
        raise Exception("Unknown statement: " + str(p))

    def take_expression(self, p_line_num):
        # TODO: this is complicated
        p = self.tokens.next()
        return Expression(p)
