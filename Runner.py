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
            print("Assignment")
            self.vars_dict[stmt.var] = stmt.expr
        elif isinstance(stmt, Parser.CodeGoto):
            print("Goto", stmt.target)
            if stmt.target not in self.line_numbers:
                print(f"Line {stmt.target} not found.")
                return False
            self.idx = self.line_numbers.index(stmt.target)
        elif isinstance(stmt, Parser.CodeNoop):
            print("Noop")
            pass
        elif isinstance(stmt, Parser.CodePrint):
            print("Print")
            print(stmt.expr)
        else:
            print("Unknown statement type:", stmt)
        self.idx += 1
        return True # Keep running
    
    def peek(self):
        if self.idx < 0 or self.idx >= len(self.line_numbers):
            return None
        ln = self.line_numbers[self.idx]
        return (ln, self.lines[ln])
