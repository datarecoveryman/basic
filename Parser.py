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
    def __repr__(self):
        return f"Expression({self.expr})"

    def get_value(self, vars_dict):
        if isinstance(self.expr, TokenStream.TokenNumber):
            return self.expr.value
        if isinstance(self.expr, TokenStream.TokenString):
            return self.expr.value
        if isinstance(self.expr, TokenStream.TokenSymbol):
            #print(f"Symbol: {self.expr.value}")
            if self.expr.value in vars_dict:
                return vars_dict[self.expr.value]
            raise Exception(f"Variable {self.expr.value} not found")
        #if isinstance(self.expr, TokenStream.TokenOperator):
        #    raise Exception(f"Operator {self.expr.value} not supported")
        #if isinstance(self.expr, TokenStream.TokenDelimiter):
        #    raise Exception(f"Delimiter {self.expr.value} not supported")
        # For expressions, the expr is a tuple
        if isinstance(self.expr, tuple):
            #print("Expression tuple:", self.expr)
            op, left_expr, right_expr = self.expr
            left_value = left_expr.get_value(vars_dict)
            right_value = right_expr.get_value(vars_dict)
            if isinstance(op, TokenStream.TokenOperator):
                if op.value == '+':
                    return left_value + right_value
                elif op.value == '-':
                    return left_value - right_value
                elif op.value == '*':
                    return left_value * right_value
                elif op.value == '/':
                    return left_value / right_value
                elif op.value == '^':
                    return left_value ** right_value
                else:
                    raise Exception(f"Unknown operator: {op.value}")
            else:
                raise Exception(f"Unknown expression type: {op}")
        raise Exception(f"Unknown expression type: {self.expr}")

class ParserFF:
    # This is a "fast forward" parser. (Copilot said this)
    def __init__(self, token_stream, debug=False):
        if not isinstance(token_stream, TokenStream.TokenStreamSkippy):
            raise Exception("Expected TokenStreamSkippy")
        self.tokens = token_stream
        self.debug = debug # Show the debug print()s

    def _debug_print(self, *msg):
        if self.debug:
            print(*msg)
    
    def all(self):
        statements = []
        stmt = self.take_statement()
        while stmt is not None:
            statements.append(stmt)
            stmt = self.take_statement()
        return statements
    
    def take_statement(self):
        # Consume one statement's worth of tokens,
        # which is variable, since it depends on the statement.
        # General structure: <line number> <verb> <args...> <newline>
        line_number_token = self.tokens.take_number()
        if line_number_token is None:
            # No start, no statement
            return None
        line_number = line_number_token.value
        self._debug_print("Line number:", line_number)
        verb = self.tokens.take_symbol()
        if verb is None:
            raise Exception("Expected verb")
        self._debug_print("Verb:", verb)
        code = None
        if verb.value == "GOTO":
            # GOTO 123
            target_line_number = self.tokens.take_number()
            if target_line_number is None:
                raise Exception("Expected line number after GOTO")
            self._debug_print("GOTO line number:", target_line_number)
            code = CodeGoto(line_number, target_line_number)
        elif verb.value == "LET":
            # LET X = 5
            var = self.tokens.take_symbol()
            if var is None:
                raise Exception("Expected variable after LET")
            self._debug_print("LET variable:", var)
            equals = self.tokens.take_operator()
            if equals is None or equals.value != "=":
                raise Exception("Expected = after variable in LET")
            self._debug_print("LET equals:", equals)
            expr = self.take_expression()
            #expr = self.tokens.take_symbol() # HACK
            code = CodeAssignment(line_number, var.value, expr)
        elif verb.value == "PRINT":
            # PRINT "Hello"
            expr = self.take_expression()
            #expr = self.tokens.take_string() # HACK
            code = CodePrint(line_number, expr)
        elif verb.value == "REM":
            # REM "my comment"
            #comment = self.tokens.take_string() # HACK
            comment_tokens = self.tokens.take_until_newline()
            self._debug_print("take_until_newline:", comment_tokens)
            if comment_tokens is None:
                raise Exception("Expected string after REM")
            self._debug_print("REM comment:", comment_tokens)
            # I don't like putting token/string processing in here.
            # Leave that to CodeNoop.
            #words = " ".join([c.original for c in comment_tokens])
            #self._debug_print("REM words:", words)
            #code = CodeNoop(line_number, words)
            code = CodeNoop(line_number, comment_tokens)
        else:
            raise Exception("Unknown verb: " + str(verb))
        if verb.value != "REM":
            newline = self.tokens.take_newline()
            if newline is None:
                raise Exception("Expected trailing newline")
        return code

    def take_expression(self):
        # parse_expression gets recursive
        return self.parse_expression()

    def get_precedence(self, token):
        if token.value in ('+', '-'):
            return 1
        if token.value in ('*', '/'):
            return 2
        if token.value == '^':
            return 3
        return 0
    
    def parse_primary(self):
        first = self.tokens.skip()
        self._debug_print("parse_primary: first:", first)
        # the "primary" in an expression can be a number, a variable,
        # a string, or a parenthesized expression (recursive).
        # But, with multiple options, the "demanding" approach has
        # to be flexible.
        n = self.tokens.next()
        self._debug_print("Next token:", n)
        if isinstance(n, TokenStream.TokenNumber) or isinstance(n, TokenStream.TokenSymbol):
            self._debug_print("parse_primary: number/symbol:", n)
            return Expression(n)
        if isinstance(n, TokenStream.TokenDelimiter) and n.value == '(':
            expr = self.parse_expression()
            closing_paren = self.tokens.take_delimiter()
            if not isinstance(closing_paren, TokenStream.TokenDelimiter) or closing_paren.value != ')':
                raise Exception("Expected closing parenthesis")
            return expr
        raise Exception("Unexpected token: " + str(n))

    def parse_expression(self, precedence=0):
        left_expr = self.parse_primary()
        while True:
            # parse_expression() always creates a left_expr, the first term.
            self._debug_print(f"left_expr: {left_expr}")
            peek = self.tokens.peek()
            self._debug_print(f"peek: {peek}")
            if peek is None:
                raise Exception("Expected operator or newline, got None")
            if peek == "\n":
               self._debug_print("parse_expression: found newline, ending expression")
               break
            op = self.tokens.take_operator()
            if op is None:
               #print("parse_expression: no operator, breaking; token =", op)
               raise Exception(f"Expected operator, got {peek}")
            # op_or_nl = self.tokens.next()
            # print("parse_expression: op_or_nl:", op_or_nl)
            # # Should be a newline (ending the expression) or an operator
            # if op_or_nl is None:
            #     raise Exception(f"Expected operator or newline, got None")
            # if isinstance(op_or_nl, TokenStream.TokenNewline):
            #     print("parse_expression: found newline, breaking")
            #     break
            # if not isinstance(op_or_nl, TokenStream.TokenOperator):
            #     print("parse_expression: not an operator, breaking")
            # op = op_or_nl
            self._debug_print("parse_expression: operator:", op)
            op_precedence = self.get_precedence(op)
            if op_precedence < precedence:
                break
            right_expr = self.parse_expression(op_precedence + 1)
            left_expr = Expression((op, left_expr, right_expr))
        return left_expr

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
    
    # Comparing next() and take_statement(),
    # next() feels like it's reacting to the current token,
    # a juggling act that seems nebulous.
    # take_statement() is demanding, and forks to different demands.
    # Of the two, I think take_statement() would get lost in a garden path.

    def take_statement(self):
        # Consume one statement's worth of tokens,
        # which is variable, since it depends on the statement.
        # General structure: <line number> <verb> <args...> <newline>
        line_number = self.tokens.take_number_ff() # non-ff works too
        if line_number is None:
            #raise Exception("Expected line number")
            # No start, no statement
            return None
        print("Line number:", line_number)
        verb = self.tokens.take_symbol_ff()
        if verb is None:
            raise Exception("Expected verb")
        print("Verb:", verb)
        code = None
        if verb.value == "GOTO":
            # GOTO 123
            target_line_number = self.tokens.take_number_ff()
            if target_line_number is None:
                raise Exception("Expected line number after GOTO")
            print("GOTO line number:", target_line_number)
            code = CodeGoto(line_number, target_line_number)
        elif verb.value == "LET":
            # LET X = 5
            var = self.tokens.take_symbol_ff()
            if var is None:
                raise Exception("Expected variable after LET")
            print("LET variable:", var)
            equals = self.tokens.take_operator_ff()
            if equals is None or equals.value != "=":
                raise Exception("Expected = after variable in LET")
            print("LET equals:", equals)
            expr = self.take_expression(line_number)
            code = CodeAssignment(line_number, var.value, expr)
        elif verb.value == "PRINT":
            # PRINT "Hello"
            expr = self.take_expression(line_number)
            code = CodePrint(line_number, expr)
        elif verb.value == "REM":
            # REM "my comment"
            comment = self.tokens.take_string_ff()
            if comment is None:
                raise Exception("Expected string after REM")
            print("REM comment:", comment)
            code = CodeNoop(line_number, comment)
        else:
            raise Exception("Unknown verb: " + str(verb))
        # TODO: use verb to determine what else to take
        # Convert verb+args into the appropriate Code* class
        newline = self.tokens.take_newline_ff()
        if newline is None:
            raise Exception("Expected newline")
        print("Newline")
        print("Code:", code)
        return code

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
            print("LET: variable:", v)
            e = self.tokens.next()
            if not isinstance(e, TokenStream.TokenOperator) or e.value != "=":
                raise Exception("Expected = after variable in LET; got " + str(e))
            #print("LET: equals", e)
            expr = self.take_expression(p_line_num)
            print("LET: expression:", expr)
            nl = self.tokens.next()
            #print("LET: expected newline", nl)
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
            #rem_line = " ".join([str(t.original) for t in rem_tokens])
            #return CodeNoop(p_line_num, rem_line)
            return CodeNoop(p_line_num, rem_tokens)
        raise Exception("Unknown statement: " + str(p))

    def take_expression(self, p_line_num):
        return self.parse_expression()

    def parse_expression(self, precedence=0):
        left_expr = self.parse_primary()
        while True:
            peek = self.tokens.peek()
            if peek is not None and peek == "\n":
                #print("parse_expression: newline, breaking")
                break
            #print(f"peek, non-newline: \"{peek}\"")
            token = self.tokens.next()
            #print("skip token:", type(token), token)
            if token is None or not isinstance(token, TokenStream.TokenOperator):
                #print("parse_expression: no operator, breaking; token =", token)
                break
            op_precedence = self.get_precedence(token)
            if op_precedence < precedence:
                break
            #self.tokens.next()  # consume operator
            right_expr = self.parse_expression(op_precedence + 1)
            left_expr = Expression((token, left_expr, right_expr))
        return left_expr

    def parse_primary(self):
        token = self.tokens.next()
        #print("parse_primary: token:", token)
        if isinstance(token, TokenStream.TokenNumber) or isinstance(token, TokenStream.TokenSymbol):
            #print("parse_primary: number/symbol:", token)
            return Expression(token)
        if isinstance(token, TokenStream.TokenDelimiter) and token.value == '(':
            expr = self.parse_expression()
            closing_paren = self.tokens.next()
            if not isinstance(closing_paren, TokenStream.TokenDelimiter) or closing_paren.value != ')':
                raise Exception("Expected closing parenthesis")
            return expr
        raise Exception("Unexpected token: " + str(token))

    def get_precedence(self, token):
        if token.value in ('+', '-'):
            return 1
        if token.value in ('*', '/'):
            return 2
        if token.value == '^':
            return 3
        return 0
