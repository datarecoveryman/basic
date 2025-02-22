
import Parser
import TokenStream

def test_generic():
    # Line numbers are mandatory
    test_program_1 = "20 LET Y = X\n" \
        + "10 LET X = 10\n" \
        + "30 REM allows anything valid 123456\n" \
        + "40 LET X = 40\n" \
        + "50 PRINT Y\n" \
        + "60 GOTO 999\n"
    print("Test program:")
    print(test_program_1.strip())
    print("")

    print("Parse the program into statements:")
    print("(Note: the line numbers are not sorted by Parser.)")
    ts = TokenStream.TokenStream(test_program_1)
    p = Parser.Parser(ts)
    statements = p.all()
    for statement in statements:
        print(statement)

def test_take_statement():
    program = "10 GOTO 20\n" \
        + "15 REM \"String comment\"\n" \
        + "20 LET X = 100\n" \
        + "30 LET Y = X * 4\n"
    #+ "40 PRINT Y\n" \
    #+ "50 GOTO 999\n"
    print("Test program:")
    print(program.strip())
    print("")

    #ts = TokenStream.TokenStream(program)
    #p = Parser.Parser(ts)
    ts_skippy = TokenStream.TokenStreamSkippy(program)
    pff = Parser.ParserFF(ts_skippy)
    # all() won't get them as it parses if it crashes.
    #print("Statements:")
    #for statement in pff.all():
    #    print("Statement:", statement)
    #    print("")
    stmt = pff.take_statement()
    while stmt is not None:
        print("Statement:", stmt)
        print("")
        stmt = pff.take_statement()


#test_generic()
test_take_statement()
