import Parser
import TokenStream

class Runner:
    def __init__(self, statements, vars_dict):
        self.statements = statements
        self.vars_dict = vars_dict
        # Given a list of statements, create a dictionary of line number -> statement
        self.lines = {}
        for stmt in statements:
            self.lines[stmt.ln] = stmt
        # Use line_numbers as a zero-based index into the lines dictionary
        self.idx = 0
        self.line_numbers = sorted(self.lines.keys())[:]
        #print("line_numbers", self.line_numbers)
        #print("Runner: Lines in order:")
        #for ln in self.line_numbers:
        #    stmt = self.lines[ln]
        #    print(f"{ln}: {stmt}")
    
    def next(self):
        p = self.peek()
        if p is None:
            print("End of program.")
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
            print(f"Assignment: set {stmt.var} to {self.vars_dict[stmt.var]}")
        elif isinstance(stmt, Parser.CodeGoto):
            print("GOTO", stmt.target)
            if stmt.target not in self.line_numbers:
                print(f"Line {stmt.target} not found.")
                return False
            # if idx is going to be incremented later, can I just subtract 1 here?
            self.idx = self.line_numbers.index(stmt.target) - 1
        elif isinstance(stmt, Parser.CodeNoop):
            print("REM Noop")
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
