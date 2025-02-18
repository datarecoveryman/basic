
import Parser
import TokenStream

test_program_1 = "LET X = 10\n" \
    + "LET Y = X\n" \
    + "REM This should allow anything valid 123456\n" \
    + "LET X = 40\n" \
    + "PRINT Y\n" \
    + "GOTO 10\n"

print("Test program:")
print(test_program_1)

ts = TokenStream.TokenStream(test_program_1)
p = Parser.Parser(ts)
tokens = p.all()
print("Tokens:")
for token in tokens:
    print(token)
