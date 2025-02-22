import Parser
import TokenStream
import Runner

def run_test(program, granular=True):
    print("Test program:")
    print(program.strip())
    print("")

    #print("Create token stream and parser...")
    ts = TokenStream.TokenStreamSkippy(program)
    p = Parser.ParserFF(ts, debug=False)
    #print("")

    #print("Parse the program into statements:")
    #print("(Note: the line numbers are not sorted by Parser.)")
    statements = []
    if granular: # Granular
        stmt = p.take_statement()
        while stmt is not None:
            statements.append(stmt)
            #print("  Statement:", stmt)
            stmt = p.take_statement()
    else:
        # all() won't get them as it parses if it crashes.
        statements = p.all()
        #for statement in statements:
        #    print("  Statement:", statement)
    #print("")

    # Give statements to Runner
    my_vars = {}
    my_runner = Runner.Runner(statements, my_vars)
    if True:
        print("Program lines in-order:")
        for ln in my_runner.line_numbers:
            stmt = my_runner.lines[ln]
            print(f"{ln}: {stmt}")
        print("")

    print("Running...")
    max_ops = 15
    ops = 0
    keep_running = my_runner.next()
    while ops < max_ops and keep_running:
        ops += 1
        if ops >= max_ops:
            print("Max ops reached; stopping Runner early.")
            break
        keep_running = my_runner.next()
    print("Vars:", my_vars)
    print("")


test_program_1 = "10 LET X = 100\n" \
    + "20 LET Y = X * 4\n"

#+ "50 LET Y = Y + 1\n" \ # Requires expression support
# Flipping 10 and 20 correctly fails due to undefined X.
test_program_2 = "20 LET X = 100\n" \
    + "10 LET Y = 77\n" \
    + "40 REM comment\n" \
    + "60 PRINT Y\n" \
    + "80 LET Y = Y + X\n" \
    + "99 GOTO 60\n"

run_test(test_program_1)
run_test(test_program_2)
