
import Parser
import TokenStream

def run_test(program, new_parser=True, granular=True):
    print("Test program:")
    print(program.strip())
    print("")

    print("Create token stream and parser...")
    if new_parser:
        ts = TokenStream.TokenStreamSkippy(program)
        p = Parser.ParserFF(ts, debug=False)
    else:
        ts = TokenStream.TokenStream(program)
        p = Parser.Parser(ts)
    print("")

    print("Parse the program into statements:")
    print("(Note: the line numbers are not sorted by Parser.)")
    print("")
    if granular: # Granular
        stmt = p.take_statement()
        while stmt is not None:
            print("Statement:", stmt)
            #print("")
            stmt = p.take_statement()
    else:
        # all() won't get them as it parses if it crashes.
        print("Statements:")
        for statement in p.all():
            print("Statement:", statement)
            #print("")

def test_generic():
    # Line numbers are mandatory
    test_program_1 = "20 LET Y = X\n" \
        + "10 LET X = 10\n" \
        + "30 REM allows anything valid 123456\n" \
        + "40 LET X = 40\n" \
        + "50 PRINT Y\n" \
        + "60 GOTO 999\n"
    run_test(test_program_1)

def test_take_statement():
    program = "10 GOTO 20\n" \
        + "20 LET X = 100\n" \
        + "30 LET Y = X * 4\n" \
        + "15 REM \"String comment\"\n"
    #+ "40 PRINT Y\n" \
    #+ "50 GOTO 999\n"
    run_test(program)

test_generic()
test_take_statement()
