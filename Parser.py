
# Using TokenStream.all() for tokens

# class TokenDelimiter(Token):
# class TokenNumber(Token):
# class TokenOperator(Token):
# class TokenSymbol(Token):
# class TokenString(Token):

import TokenStream

class Code:
    pass
class CodeAssignment(Code):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr
    def __str__(self):
        return f"Assignment({self.var} <- {self.expr})"
class CodeExpression(Code):
    def __init__(self, expr):
        # TODO: this will be a tree or something later
        self.expr = expr
    def __str__(self):
        return f"Expression({self.expr})"
class CodeGoto(Code):
    def __init__(self, line_number):
        self.line_number = line_number
    def __str__(self):
        return f"Goto({self.line_number})"
class CodeNoop(Code):
    def __init__(self, comment):
        self.comment = comment
    def __str__(self):
        return f"Noop({self.comment})"
class CodePrint(Code):
    def __init__(self, expr):
        self.expr = expr
    def __str__(self):
        return f"Print({self.expr})"

class Parser:
    def __init__(self, token_stream):
        if not isinstance(token_stream, TokenStream.TokenStream):
            raise Exception("Expected TokenStream")
        self.tokens = token_stream
    
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
            return CodeGoto(line_number.value)
        if isinstance(p, TokenStream.TokenSymbol) and p.value == "PRINT":
            # ["PRINT", "X", "+", "12345"]
            expr = self.take_expression()
            nl = self.tokens.next()
            if not isinstance(nl, TokenStream.TokenNewline):
                raise Exception(f"Expected newline after {p.value}; got {nl}")
            return CodePrint(expr)
        if isinstance(p, TokenStream.TokenSymbol) and p.value == "LET":
            # Assignment statement, e.g. ["LET", "X", "=", "5"]
            v = self.tokens.next()
            if not isinstance(v, TokenStream.TokenSymbol):
                raise Exception("Expected variable after LET; got " + str(v))
            e = self.tokens.next()
            if not isinstance(e, TokenStream.TokenOperator) or e.value != "=":
                raise Exception("Expected = after variable in LET; got " + str(e))
            expr = self.take_expression()
            nl = self.tokens.next()
            if not isinstance(nl, TokenStream.TokenNewline):
                raise Exception(f"Expected newline after {p.value}; got {nl}")
            return CodeAssignment(v.value, expr)
        #if isinstance(p, TokenSymbol) and p.value == "INPUT":
        #    return self.parse_input()
        #if isinstance(p, TokenSymbol) and p.value == "END":
        #    return self.parse_end()
        if isinstance(p, TokenStream.TokenSymbol) and p.value == "REM":
            # must be like REM "my comment"
            p = self.tokens.next()
            rem_tokens = []
            while p is not None and not isinstance(p, TokenStream.TokenNewline):
                print("REM token:", p)
                rem_tokens.append(p)
                p = self.tokens.next()
            # Ignore the rest of the line
            rem_line = " ".join([str(t.original) for t in rem_tokens])
            return CodeNoop(rem_line)
        raise Exception("Unknown statement: " + str(p))

    def take_expression(self):
        # TODO: this is complicated
        p = self.tokens.next()
        return CodeExpression(p)
