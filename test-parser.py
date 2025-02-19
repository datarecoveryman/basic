
import Parser
import TokenStream

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
