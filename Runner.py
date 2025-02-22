import Parser
import TokenStream

class Runner:
    def __init__(self, statements, vars_dict, debug=False):
        self.statements = statements
        self.vars_dict = vars_dict
        self.debug = debug
        # Given a list of statements, create a dictionary of line number -> statement
        self.lines = {}
        for stmt in statements:
            self.lines[stmt.ln] = stmt
            self._debug_print(f"{stmt.ln}: {stmt}")
        # Use line_numbers as a zero-based index into the lines dictionary
        self.idx = 0
        self.line_numbers = sorted(self.lines.keys())[:]
        self._debug_print("Runner: line_numbers", self.line_numbers)
        if self.debug:
            self._debug_print("Runner: Lines in order:")
            for ln in self.line_numbers:
                stmt = self.lines[ln]
                self._debug_print(f"{ln}: {stmt}")
    
    def _debug_print(self, *args):
        if self.debug:
            print(*args)
    
    def next(self):
        p = self.peek()
        if p is None:
            self._debug_print("End of program.")
            return False
        ln, stmt = p
        print(f"Execute line {ln}: {stmt}")
        if isinstance(stmt, Parser.CodeAssignment):
            if isinstance(stmt.expr, Parser.Expression):
                expr_value = stmt.expr.get_value(self.vars_dict)
                #print(f"Expression value: {expr_value}")
                self.vars_dict[stmt.var] = expr_value
            else:
                #print(f"Setting {stmt.var} to literal {stmt.expr}")
                self.vars_dict[stmt.var] = stmt.expr.value
            self._debug_print(f"Assignment: set {stmt.var} to {self.vars_dict[stmt.var]}")
        elif isinstance(stmt, Parser.CodeGoto):
            self._debug_print("GOTO", stmt.target)
            if isinstance(stmt.target, TokenStream.Token):
                #print("GOTO: getting value from token")
                # If the target is a token, get its value
                target_ln = stmt.target.value
            else:
                target_ln = stmt.target
            if target_ln not in self.line_numbers:
                print(f"Line {stmt.target} not found.")
                return False
            # if idx is going to be incremented later, can I just subtract 1 here?
            self.idx = self.line_numbers.index(target_ln) - 1
        elif isinstance(stmt, Parser.CodeNoop):
            self._debug_print("REM Noop")
            pass
        elif isinstance(stmt, Parser.CodePrint):
            if isinstance(stmt.expr, Parser.Expression):
                expr_value = stmt.expr.get_value(self.vars_dict)
                print(f"PRINT expression: {expr_value}")
            else:
                print(f"PRINT literal {stmt.expr}: {stmt.expr.value}")
        else:
            print("Unknown statement type:", stmt)
        self.idx += 1
        return True # Keep running
    
    def peek(self):
        if self.idx < 0 or self.idx >= len(self.line_numbers):
            return None
        ln = self.line_numbers[self.idx]
        return (ln, self.lines[ln])
